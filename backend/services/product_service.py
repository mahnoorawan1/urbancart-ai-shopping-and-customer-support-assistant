import json
from pathlib import Path

PRODUCT_PATH = Path(__file__).parent.parent / "data" / "products.json"


def get_products():
    with open(PRODUCT_PATH, "r", encoding="utf-8") as file:
        return json.load(file)