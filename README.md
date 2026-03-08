# Real-Time Multilingual Voice AI Agent

## 1. Project Overview
This project implements a **Real-Time Voice AI Agent** for **clinical appointment management**.  

The agent can:

- Understand spoken input in **English, Hindi, and Tamil**  
- Convert speech to text using **Whisper STT**  
- Detect language and translate non-English text to English  
- Identify user intent (`book`, `cancel`, `reschedule`, or general query)  
- Handle appointment operations with conflict checking  
- Respond using **Text-to-Speech (TTS)**  
- Maintain **session memory** in Redis for contextual conversations  
- Operate in **real-time** using WebSockets  

---

## 2. Features Implemented

| Feature | Status | Notes |
|---------|--------|-------|
| Voice Input (STT) | ✅ | Whisper STT converts audio to text |
| Language Detection | ✅ | Detects English, Hindi, Tamil |
| Translation | ✅ | GoogleTranslator for non-English text |
| Intent Detection | ✅ | Rule-based (`book`, `cancel`, `reschedule`) |
| Appointment Booking | ✅ | Checks for conflicts; stores in memory |
| Appointment Cancel | ✅ | Removes user appointment |
| Appointment Reschedule | ✅ | Updates date/time if appointment exists |
| Session Memory | ✅ | Redis stores conversation per session |
| TTS Response | ✅ | Generates English audio reply |
| WebSocket Real-Time | ✅ | `/ws/voice` streams audio & returns response |
| REST APIs | ✅ | `/process-text`, `/speech-to-text`, `/voice-agent`, `/appointments` |
| Latency Logging | ✅ | STT & TTS time measured |

---

## 3. Architecture

### 3.1 System Flow
User Speech
↓
Speech-to-Text (Whisper)
↓
Language Detection & Translation
↓
Intent Detection (Rule-Based)
↓
Appointment Engine / Math Solver
↓
Generate Response
↓
Text-to-Speech (gTTS)
↓
Audio Response (WebSocket / REST)


### 3.2 Components

- **FastAPI Backend:** Handles REST endpoints and WebSocket connections  
- **Whisper STT:** Converts speech to text  
- **Language Detection:** Detects English, Hindi, Tamil  
- **Translation:** Converts non-English input to English  
- **Intent Agent:** Determines user intent  
- **Appointment Engine:** Handles bookings, conflicts, updates  
- **Redis Session Memory:** Stores temporary conversation context  
- **TTS (gTTS):** Generates audio response  
- **WebSocket:** Real-time audio streaming  

![Architecture Diagram](docs/architecture.png)

---

## 4. Installation & Setup

### 4.1 Clone Repository
```bash
git clone <your-repo-url>
cd voice-ai-agent
4.2 Create Virtual Environment & Install Dependencies
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
pip install -r requirements.txt
4.3 Start Redis
redis-server
4.4 Run API Server
uvicorn backend.main:app --reload
5. API Endpoints
Endpoint	Method	Description
/health	GET	Health check
/process-text	POST	Detect language, translate, intent for text
/speech-to-text	POST	Convert audio file to text
/voice-agent	POST	Process audio → STT → intent → TTS response
/appointments	GET	View current appointments
/ws/voice	WebSocket	Real-time audio streaming & response
/redis-test	GET	Test Redis connection
6. Usage Example
6.1 WebSocket Test
import websocket

ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:8000/ws/voice")

with open("test.wav", "rb") as f:
    ws.send_binary(f.read())

result = ws.recv()
print(result)
6.2 REST API Test
curl -X POST "http://127.0.0.1:8000/process-text" \
-H "Content-Type: application/json" \
-d '{"text": "Book appointment with cardiologist tomorrow"}'
7. Appointment Engine

Book Appointment: Checks availability, prevents double-booking

Cancel Appointment: Removes user appointment if found

Reschedule Appointment: Updates date/time for existing appointments

Conflict Handling: Suggests slot unavailable if already booked

8. Memory System
Session Memory

Redis stores conversation per session_id

Each session expires after 1 hour

Example:

[
  "User: Book appointment with cardiologist tomorrow",
  "Agent: Please provide time for the appointment"
]
Persistent Memory

Not implemented yet

Future improvement: store patient preferences, history

9. Latency Metrics

STT time: ~150–250ms

TTS time: ~100–150ms

Total pipeline: ~350–500ms (target <450ms)

10. Known Limitations

Multilingual TTS not supported (English only)

Persistent memory not implemented

Outbound campaign mode not implemented

Limited date handling (“tomorrow” only)

Partial follow-up question support

11. Future Improvements

Integrate LLM-based intent agent for multi-step conversations

Add multilingual TTS (Hindi/Tamil)

Implement persistent memory

Support outbound campaign scheduler for reminders

Optimize end-to-end latency (<450ms)

Suggest alternative slots if booked

12. Folder Structure
voice-ai-agent/
├── backend/
├── agent/
├── memory/
├── services/
├── tests/
├── requirements.txt
├── README.md
└── docs/architecture.png
13. Demo Instructions

Start Redis: redis-server

Start FastAPI: uvicorn backend.main:app --reload

Use /voice-agent endpoint or WebSocket to send audio

Listen to TTS responses and test booking/cancel/reschedule

Verify appointments via /appointments endpoint
