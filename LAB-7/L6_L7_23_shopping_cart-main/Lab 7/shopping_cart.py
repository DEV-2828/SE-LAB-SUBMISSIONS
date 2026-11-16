"""Defensive parsers for Lab 7.

Invalid carts/promos return 0; invalid or unsupported pincodes return 'Unknown'.
These fallbacks satisfy the starter's no-crash contract. A malformed cart is
rejected as a whole, so it can never produce a misleading partial total.
"""
import re

ZONES = {"1": "North", "2": "North", "3": "West", "4": "West",
         "5": "South", "6": "South", "7": "East", "8": "East"}


def cart_total(cart):
    """Sum name:pricexqty CSV; prices >= 0 and quantities > 0 are integers.

    Names must be nonempty and cannot contain ':' or ','. Whitespace around
    fields is allowed; numbers use ASCII digits. Empty/invalid input returns 0.
    """
    if not isinstance(cart, str) or not cart.strip():
        return 0
    total = 0
    for item in cart.split(','):
        match = re.fullmatch(r"\s*([^:,]+?)\s*:\s*([0-9]+)\s*x\s*([0-9]+)\s*", item)
        if match is None or not match[1].strip():
            return 0
        try:
            price, qty = int(match[2]), int(match[3])
        except ValueError:  # Includes Python's oversized-integer conversion limit.
            return 0
        if qty <= 0:
            return 0
        total += price * qty
    return total


def promo_percent(code):
    """Accept a complete case-insensitive OFF0..OFF100 code, else return 0."""
    if not isinstance(code, str):
        return 0
    match = re.fullmatch(r"OFF([0-9]{1,3})", code.strip(), flags=re.IGNORECASE | re.ASCII)
    if match is None:
        return 0
    percent = int(match[1])
    return percent if percent <= 100 else 0


def delivery_zone(pincode):
    """Map exactly six ASCII digits using the supplied 1..8 prefix table.

    Prefixes 0 and 9 are unsupported by this exercise's table. No claim about
    real postal-code allocation is made by this simplified mapping.
    """
    if not isinstance(pincode, str):
        return "Unknown"
    pincode = pincode.strip()
    if re.fullmatch(r"[0-9]{6}", pincode) is None:
        return "Unknown"
    return ZONES.get(pincode[0], "Unknown")


def main():
    try:
        print("==== Running cart_total ====")
        user_input = input("Enter cart as name:pricexqty CSV (e.g. pen:10x2,book:250x1): ")
        print("Cart Total:", cart_total(user_input))

        print("\n==== Running promo_percent ====")
        user_input = input("Enter a promo code (e.g. OFF20): ")
        print("Discount Percent:", promo_percent(user_input))

        print("\n==== Running delivery_zone ====")
        user_input = input("Enter a 6 digit pincode (e.g. 560085): ")
        print("Delivery Zone:", delivery_zone(user_input))
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")


if __name__ == "__main__":
    main()
