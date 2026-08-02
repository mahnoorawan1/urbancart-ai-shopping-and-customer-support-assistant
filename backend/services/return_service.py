import json
from pathlib import Path

ORDERS_PATH = Path(__file__).parent.parent / "data" / "orders.json"


def check_return(order_id, email):

    with open(ORDERS_PATH, "r", encoding="utf-8") as file:
        orders = json.load(file)

    for order in orders:

        if (
            order["order_id"] == order_id
            and
            order["email"].lower() == email.lower()
        ):
            return order

    return None