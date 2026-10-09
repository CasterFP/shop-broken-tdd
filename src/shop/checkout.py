"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

import re

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "Order must contain at least one line"
    seen_skus: set[str] = set()
    for position, line in enumerate(lines, start=1):
        for key in REQUIRED_LINE_KEYS:
            if key not in line:
                return f"Line {position} is missing {key}"
        if not line.get("sku"):
            return "SKU must not be empty"
        if re.fullmatch(r"[+-]?\d+(?:_\d+)*", line["qty"].strip()) is None:
            return "Quantity must be an integer"
        if int(line["qty"]) <= 0:
            return "Quantity must be positive"
        if re.fullmatch(r"[+-]?\d+(?:_\d+)*", line["unit_price_kopecks"].strip()) is None:
            return "Unit price must be an integer"
        if int(line["unit_price_kopecks"]) < 0:
            return "Unit price must not be negative"
        if line["sku"] in seen_skus:
            return "SKU must not repeat"
        seen_skus.add(line["sku"])
    if promo_code and promo_code not in PROMO_CODES:
        return "Promo code is not supported"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "Shipping city is not supported"
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None
    subtotal = sum(int(line["qty"]) * int(line["unit_price_kopecks"]) for line in lines)
    quantity = sum(int(line["qty"]) for line in lines)
    discount_percent = 0
    for threshold, tier_percent in TIER_DISCOUNTS:
        if quantity >= threshold:
            discount_percent = tier_percent
    discount_percent = max(discount_percent, PROMO_CODES.get(promo_code, 0))
    discount_percent = min(discount_percent, MAX_DISCOUNT_PERCENT)
    discounted_subtotal = subtotal - percent_of(subtotal, discount_percent)
    return discounted_subtotal + percent_of(discounted_subtotal, VAT_PERCENT)
