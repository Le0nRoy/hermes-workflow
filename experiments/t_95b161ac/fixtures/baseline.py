"""Synthetic initial fixture with a deliberately planted bool-as-int defect."""


def submit(payload):
    if not isinstance(payload, dict):
        return 400, {"error": "invalid quantity"}
    quantity = payload.get("quantity")
    if not isinstance(quantity, int) or not 1 <= quantity <= 100:
        return 400, {"error": "invalid quantity"}
    return 201, {"quantity": quantity}
