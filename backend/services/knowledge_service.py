import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "store_data.json"


def get_store_data():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)