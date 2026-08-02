from pathlib import Path
import os
import json

from dotenv import load_dotenv
from google import genai

from services.knowledge_service import get_store_data
from services.recommendation_service import recommend_products

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Load System Prompt
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"

with open(PROMPT_PATH, "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()


# Fallback Models
MODELS = [
    "models/gemini-3.5-flash-lite",
    "models/gemini-3.1-flash-lite",
    "models/gemini-flash-latest",
]


def generate_with_fallback(prompt):

    last_error = None

    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"[WARNING] {model} failed: {e}")
            last_error = e
            continue

    print(last_error)

    return (
        "I'm sorry, our AI assistant is temporarily unavailable. "
        "Please try again in a few moments."
    )


def ask_gemini(user_message):

    store_data = get_store_data()

    prompt = f"""
{SYSTEM_PROMPT}

Store Information:
{json.dumps(store_data, indent=2)}

Customer:
{user_message}
"""

    return generate_with_fallback(prompt)


def recommend_with_ai(
    user_message,
    category=None,
    max_price=None,
    brand=None,
    preferences=None
):

    products = recommend_products(
        category=category,
        max_price=max_price,
        brand=brand
    )



    prompt = f"""
{SYSTEM_PROMPT}

You are UrbanCart AI.

Customer Request:
{user_message}

Customer Preferences:
{json.dumps(preferences, indent=2)}
 ns 
Matching Products:
{json.dumps(products, indent=2)}

Instructions:
- Recommend ONLY from the Matching Products list.
- Explain why each product matches the customer's preferences.
- Mention the product price.
- Mention important specifications.
- Keep the response friendly and concise.
- If there are no matching products, politely tell the customer.
"""

    return generate_with_fallback(prompt)

def explain_order_status(order):

    MODEL = os.getenv("GEMINI_MODEL", "models/gemini-3.5-flash-lite")

    response = client.models.generate_content(
        model=MODEL,
        contents=f"""
{SYSTEM_PROMPT}

You are UrbanCart AI.

The backend has already found the customer's order.

DO NOT invent any information.

Use ONLY the information below.

Order Information:

{json.dumps(order, indent=2)}

Your job:

- Explain the current order status.
- Mention the ordered items.
- Mention the tracking number if available.
- Mention the estimated delivery date.
- Be friendly and professional.
"""
    )

    return response.text

def explain_return(order):

    MODEL = os.getenv("GEMINI_MODEL", "models/gemini-3.5-flash-lite")

    response = client.models.generate_content(
        model=MODEL,
        contents=f"""
{SYSTEM_PROMPT}

You are UrbanCart AI.

The backend has already verified the customer's identity.

Do NOT invent any information.

Use ONLY the Return Information below.

Return Information:

{json.dumps(order, indent=2)}

Reply ONLY in this format:

↩ Return Eligibility

Order ID:

Items:

Eligible:
(Yes or No)

Return Deadline:

Next Step:

If eligible, politely ask the customer for the reason for the return.

If not eligible, politely explain why.

Do not write long paragraphs.
"""
    )

    return response.text