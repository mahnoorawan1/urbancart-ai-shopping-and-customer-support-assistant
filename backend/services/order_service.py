import json
from pathlib import Path

ORDERS_PATH = Path(__file__).parent.parent / "data" / "orders.json"


def get_order(order_id, email):

    with open(ORDERS_PATH, "r", encoding="utf-8") as file:
        orders = json.load(file)

    for order in orders:

        if (
            order["order_id"].lower() == order_id.lower()
            and
            order["email"].lower() == email.lower()
        ):
            return order

    return None