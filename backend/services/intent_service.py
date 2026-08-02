import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = os.getenv("GEMINI_MODEL", "models/gemini-3.5-flash-lite")


def detect_intent(user_message):

    prompts_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "prompts",
        "intent_prompt.txt"
    )
    prompts_path = os.path.abspath(prompts_path)

    try:
        with open(prompts_path, "r", encoding="utf-8") as file:
            prompt = file.read()
    except FileNotFoundError:
        prompt = "{user_message}"

    prompt = prompt.replace("{user_message}", user_message)

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    try:
        return json.loads(response.text)

    except Exception:

        return {
            "intent": "general",
            "entities": {
                "category": None,
                "brand": None,
                "budget": None,
                "order_id": None,
                "email": None,
                "preferences": []
            }
        }