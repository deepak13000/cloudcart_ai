from langchain.tools import tool

# ── MOCK DATA ───────────────────────────────────────────────────────────────

ORDER_DATABASE: dict = {
    "CC-12345": {
        "status": "Shipped",
        "estimated_delivery": "2026-05-10",
        "tracking_url": "https://track.cloudcart.com/CC-12345",
    },
    "CC-23456": {
        "status": "Out for delivery",
        "estimated_delivery": "2026-05-08",
        "tracking_url": "https://track.cloudcart.com/CC-23456",
    },
    "CC-34567": {
        "status": "Processing",
        "estimated_delivery": "2026-05-15",
        "tracking_url": "https://track.cloudcart.com/CC-34567",
    },
}

INVENTORY: dict = {
    "wireless headphones": 12,
    "fitness tracker": 5,
    "smartphone case": 32,
    "laptop sleeve": 8,
    "usb-c hub": 0,
}

# ── TOOLS ───────────────────────────────────────────────────────────────────

def _get_order_status(order_id: str) -> str:
    """
    Fetch the current CloudCart order status for a given order ID.

    Args:
        order_id: The CloudCart order identifier, e.g. CC-12345.

    Returns:
        A human-readable string with status, ETA, and tracking link.
    """
    normalized = order_id.strip().upper()
    order = ORDER_DATABASE.get(normalized)
    if not order:
        return (
            f"Order {normalized} was not found in the CloudCart system. "
            "Please double-check your order ID."
        )
    return (
        f"Order {normalized} is currently '{order['status']}'. "
        f"Estimated delivery: {order['estimated_delivery']}. "
        f"Track your shipment here: {order['tracking_url']}"
    )


get_order_status = tool(_get_order_status)


def _calculate_shipping_cost(
    weight_kg: float,
    destination: str,
    express: bool = False,
) -> dict:
    """
    Calculate a shipping cost estimate for CloudCart deliveries.

    Args:
        weight_kg:   Package weight in kilograms.
        destination: Country name (india, us, uk, canada, australia, …).
        express:     Whether express shipping is requested.

    Returns:
        A dict with cost_usd, shipping_days, destination, and express flag.
    """
    rates: dict[str, float] = {
        "india": 5.0,
        "us": 10.0,
        "uk": 15.0,
        "canada": 12.0,
        "australia": 18.0,
        "germany": 14.0,
        "france": 14.0,
    }
    base_rate = rates.get(destination.strip().lower(), 20.0)
    express_fee = 10.0 if express else 0.0
    cost_usd = round(base_rate * weight_kg + express_fee, 2)
    shipping_days = 3 if express else 7

    return {
        "cost_usd": cost_usd,
        "shipping_days": shipping_days,
        "destination": destination,
        "express": express,
    }


calculate_shipping_cost = tool(_calculate_shipping_cost)


def _check_product_availability(product_name: str) -> str:
    """
    Check whether a CloudCart product is currently available in inventory.

    Args:
        product_name: The product name to check (case-insensitive).

    Returns:
        A human-readable availability string.
    """
    normalized = product_name.strip().lower()
    quantity = INVENTORY.get(normalized)

    if quantity is None:
        return f"We do not have inventory information for '{product_name}'."
    if quantity == 0:
        return f"'{product_name}' is currently out of stock."
    return f"'{product_name}' is available — {quantity} units in stock."


check_product_availability = tool(_check_product_availability)