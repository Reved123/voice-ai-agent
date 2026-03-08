def detect_intent(text):

    text = text.lower()

    if "book" in text or "appointment" in text:
        return {
            "intent": "book"
        }

    elif "cancel" in text:
        return {
            "intent": "cancel"
        }

    elif "reschedule" in text or "change" in text:
        return {
            "intent": "reschedule"
        }

    else:
        return {
            "intent": "unknown"
        }