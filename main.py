import redis
import whisper
import uuid
import re
from gtts import gTTS
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from langdetect import detect
from fastapi import WebSocket
import time
import base64
app=FastAPI()

@app.websocket("/ws/voice")
async def websocket_voice_agent(websocket: WebSocket):

    await websocket.accept()
    session_id = str(uuid.uuid4())

    while True:

        
        data = await websocket.receive_bytes()

        start_time = time.time()

        
        audio_path = f"audio_{uuid.uuid4()}.wav"

        with open(audio_path, "wb") as f:
            f.write(data)

        
        stt_start = time.time()
        result = model.transcribe(audio_path)
        text = result["text"]
        stt_time = time.time() - stt_start

        
        lang = detect_language(text)

        
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        store_session(session_id, translated)
        history = get_session(session_id)
        print("Conversation history:",history)

        
        intent = detect_intent(translated)

        response = ""

        if intent == "book_appointment":

            doctor, date, time_slot = extract_appointment_details(translated)

            if doctor and date and time_slot:
                response = book_appointment("Patient", doctor, date, time_slot)
            else:
                response = "Please provide doctor name, date and time"

        elif intent == "cancel_appointment":
            response = cancel_appointment("Patient")

        elif intent == "reschedule_appointment":

            doctor, date, time_slot = extract_appointment_details(translated)

            if date and time_slot:
                response = reschedule_appointment("Patient", date, time_slot)
            else:
                response = "Please provide new date and time"

        else:

            answer = solve_math(translated)

            if answer is not None:
                response = f"The answer is {answer}"
            else:
                response = "Sorry I did not understand"

        
        tts_start = time.time()
        audio_file = text_to_speech(response)
        tts_time = time.time() - tts_start

        with open(audio_file, "rb") as f:
            audio_bytes = f.read()

        
        audio_base64 = base64.b64encode(audio_bytes).decode()

        total_latency = time.time() - start_time

    
        await websocket.send_json({
            "speech_text": text,
            "translated_text": translated,
            "intent": intent,
            "response": response,
            "session_history":history,
            "audio_base64": audio_base64,
            "latency": {
                "stt_time": stt_time,
                "tts_time": tts_time,
                "total_latency": total_latency
            }
        })




redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


model = whisper.load_model("base")


doctor_schedule = {
    "cardiologist": ["10:00", "14:00", "16:00"],
    "dermatologist": ["11:00", "15:00"],
    "dentist": ["09:00", "13:00"]
}


appointments = []


def store_session(session_id, data):
    redis_client.rpush(session_id, data)
    redis_client.expire(session_id,3600)

def get_session(session_id):
    return redis_client.lrange(session_id,0,-1)


def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"


def text_to_speech(text):
    tts = gTTS(text=text, lang="en")
    filename = f"response_{uuid.uuid4()}.mp3"
    tts.save(filename)
    return filename


def detect_intent(text):

    text = text.lower()

    if "cancel" in text:
        return "cancel_appointment"

    if "reschedule" in text:
        return "reschedule_appointment"

    if "book" in text and "appointment" in text:
        return "book_appointment"

    if "appointment" in text:
        return "book_appointment"

    return "general_query"


def extract_appointment_details(text):

    doctor = None
    date = None
    time = None

    for d in doctor_schedule.keys():
        if d in text.lower():
            doctor = d

    time_match = re.search(r"\d{1,2}(:\d{2})?\s*(am|pm)?", text, re.IGNORECASE)
    if time_match:
        time = time_match.group()

    if "tomorrow" in text.lower():
        date = "tomorrow"

    return doctor, date, time


def check_availability(doctor, date, time):

    for appt in appointments:
        if appt["doctor"] == doctor and appt["date"] == date and appt["time"] == time:
            return False

    return True


def book_appointment(patient, doctor, date, time):

    if not check_availability(doctor, date, time):
        return "Sorry, this slot is already booked"

    appointment = {
        "patient": patient,
        "doctor": doctor,
        "date": date,
        "time": time
    }

    appointments.append(appointment)

    return f"Appointment booked with {doctor} on {date} at {time}"


def cancel_appointment(patient):

    global appointments

    appointments = [a for a in appointments if a["patient"] != patient]

    return "Appointment cancelled successfully"


def reschedule_appointment(patient, new_date, new_time):

    for appt in appointments:
        if appt["patient"] == patient:
            appt["date"] = new_date
            appt["time"] = new_time
            return f"Appointment rescheduled to {new_date} at {new_time}"

    return "No appointment found to reschedule"


def solve_math(text):

    numbers = list(map(int, re.findall(r'\d+', text)))

    if len(numbers) < 2:
        return None

    if "divide" in text or "divided" in text:
        if numbers[1] != 0:
            return numbers[0] / numbers[1]

    elif "plus" in text or "add" in text:
        return numbers[0] + numbers[1]

    elif "minus" in text or "subtract" in text:
        return numbers[0] - numbers[1]

    elif "multiply" in text or "times" in text:
        return numbers[0] * numbers[1]

    return None


class InputText(BaseModel):
    text: str

@app.post("/process-text")
def process_text(data: InputText):

    text = data.text

    lang = detect_language(text)

    translated = GoogleTranslator(source='auto', target='en').translate(text)

    intent = detect_intent(translated)

    return {
        "original_text": text,
        "detected_language": lang,
        "translated_text": translated,
        "intent": intent
    }


@app.get("/redis-test")
def redis_test():

    redis_client.set("test_key", "Voice AI working")

    value = redis_client.get("test_key")

    return {"redis_value": value}


@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):

    audio_path = f"audio_{uuid.uuid4()}.wav"

    with open(audio_path, "wb") as f:
        f.write(await file.read())

    result = model.transcribe(audio_path)

    return {
        "transcribed_text": result["text"]
    }


@app.get("/appointments")
def get_appointments():
    return appointments


@app.get("/health")
def health():
    return {"status": "Voice agent running"}


@app.post("/voice-agent")
async def voice_agent(file: UploadFile = File(...)):

    audio_path = f"audio_{uuid.uuid4()}.wav"

    with open(audio_path, "wb") as f:
        f.write(await file.read())

    
    result = model.transcribe(audio_path)
    text = result["text"]

    
    lang = detect_language(text)

    translated = GoogleTranslator(source='auto', target='en').translate(text)

    
    intent = detect_intent(translated)

    response = ""

    if intent == "book_appointment":

        doctor, date, time = extract_appointment_details(translated)

        if doctor and date and time:
            response = book_appointment("Patient", doctor, date, time)
        else:
            response = "Please provide doctor name, date and time"

    elif intent == "cancel_appointment":
        response = cancel_appointment("Patient")

    elif intent == "reschedule_appointment":

        doctor, date, time = extract_appointment_details(translated)

        if date and time:
            response = reschedule_appointment("Patient", date, time)
        else:
            response = "Please provide new date and time"

    else:

        answer = solve_math(translated)

        if answer is not None:
            response = f"The answer is {answer}"
        else:
            response = "Sorry I did not understand your request"

    audio_file = text_to_speech(response)

    return {
        "speech_text": text,
        "language": lang,
        "translated_text": translated,
        "intent": intent,
        "response": response,
        "audio_file": audio_file
    }
