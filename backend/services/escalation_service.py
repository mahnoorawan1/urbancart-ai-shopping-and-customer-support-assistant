ESCALATION_KEYWORDS = [
    "human",
    "agent",
    "representative",
    "manager",
    "complaint",
    "angry",
    "lawsuit",
    "legal",
    "frustrated",
    "not satisfied",
    "speak to someone"
]


def needs_human_handoff(message):

    message = message.lower()

    for keyword in ESCALATION_KEYWORDS:
        if keyword in message:
            return True

    return False