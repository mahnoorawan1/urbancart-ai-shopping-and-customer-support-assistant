from services.product_service import get_products


def recommend_products(category=None, max_price=None, brand=None):

    products = get_products()

    results = []

    for product in products:

        # Category filter
        if category:
            if product["category"].lower() != category.lower():
                continue

        # Budget filter
        if max_price:
            if product["price"] > max_price:
                continue

        # Brand filter
        if brand:
            if product["brand"].lower() != brand.lower():
                continue

        # Availability
        if product["stock"] <= 0:
            continue

        results.append(product)

    return results