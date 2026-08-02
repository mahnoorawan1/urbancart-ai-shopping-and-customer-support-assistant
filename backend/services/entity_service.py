import re


def extract_entities(user_message):
    message = user_message.lower()

    entities = {
        "category": None,
        "budget": None,
        "brand": None
    }

    # Categories
    categories = [
        "laptop",
        "phone",
        "headphones",
        "earbuds",
        "mouse",
        "keyboard",
        "monitor"
    ]

    for category in categories:
        if category in message:
            entities["category"] = category.title()
            break

    # Brands
    brands = [
        "hp",
        "acer",
        "apple",
        "sony",
        "logitech",
        "dell",
        "lenovo"
    ]

    for brand in brands:
        if brand in message:
            entities["brand"] = brand.title()
            break

    # Budget
    budget = re.search(r"\d+", message)

    if budget:
        entities["budget"] = int(budget.group())

    return entities
