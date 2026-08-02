def extract_preferences(message):

    text = message.lower()

    preferences = {
        "purpose": None,
        "customer_type": None
    }

    # Customer type

    if "student" in text:
        preferences["customer_type"] = "Student"

    elif "developer" in text:
        preferences["customer_type"] = "Developer"

    elif "designer" in text:
        preferences["customer_type"] = "Designer"

    # Purpose

    if "gaming" in text or "game" in text:
        preferences["purpose"] = "Gaming"

    elif "programming" in text or "coding" in text:
        preferences["purpose"] = "Programming"

    elif "ai" in text or "machine learning" in text:
        preferences["purpose"] = "Artificial Intelligence"

    elif "office" in text:
        preferences["purpose"] = "Office Work"

    return preferences