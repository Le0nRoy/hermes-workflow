"""Synthetic quantity contract; bool is deliberately excluded from integers."""


def submit(payload):
    if not isinstance(payload, dict):
        return 400, {"error": "invalid quantity"}
    quantity = payload.get("quantity")
    if type(quantity) is not int or not 1 <= quantity <= 100:
        return 400, {"error": "invalid quantity"}
    return 201, {"quantity": quantity}
