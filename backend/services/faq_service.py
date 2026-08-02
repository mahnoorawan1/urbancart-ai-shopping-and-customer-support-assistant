def get_faq_response(message):

    message = message.lower()

    if "shipping" in message:
        return "Standard shipping takes 3-5 business days."

    elif "return" in message:
        return "Products can be returned within 30 days."

    elif "payment" in message:
        return "We accept Visa, Mastercard, and PayPal."

    return "Sorry, I couldn't find an answer."