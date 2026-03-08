appointments = []

def book_appointment(patient, doctor, date, time):

    for a in appointments:
        if a["doctor"] == doctor and a["date"] == date and a["time"] == time:
            return {"status": "failed", "message": "Slot already booked"}

    appointment = {
        "patient": patient,
        "doctor": doctor,
        "date": date,
        "time": time
    }

    appointments.append(appointment)

    return {"status": "success", "appointment": appointment}


def cancel_appointment(patient):

    for a in appointments:
        if a["patient"] == patient:
            appointments.remove(a)
            return {"status": "cancelled"}

    return {"status": "not found"}


def list_appointments():
    return appointments