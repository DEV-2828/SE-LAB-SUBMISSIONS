"""Fuzz, semantic, and regression tests for the Lab 7 shopping-cart parser."""

import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from shopping_cart import cart_total, delivery_zone, promo_percent


settings.register_profile("lab", max_examples=300, derandomize=True, deadline=None)
settings.load_profile("lab")

unexpected = st.one_of(
    st.text(), st.none(), st.integers(), st.floats(), st.binary(),
    st.booleans(), st.lists(st.integers()), st.dictionaries(st.text(), st.integers()),
)


@given(unexpected)
def test_cart_total_no_crash(value):
    result = cart_total(value)
    assert type(result) is int and result >= 0


@given(unexpected)
def test_promo_percent_no_crash(value):
    result = promo_percent(value)
    assert type(result) is int and 0 <= result <= 100


@given(unexpected)
def test_delivery_zone_no_crash(value):
    assert delivery_zone(value) in {"North", "South", "East", "West", "Unknown"}


@given(st.lists(st.tuples(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=20).filter(lambda s: bool(s.strip())),
    st.integers(min_value=0, max_value=10**12),
    st.integers(min_value=1, max_value=10**6),
), min_size=1, max_size=20))
def test_cart_total_valid_items(items):
    encoded = ",".join(f"{name}:{price}x{qty}" for name, price, qty in items)
    assert cart_total(encoded) == sum(price * qty for _, price, qty in items)


@given(st.integers(min_value=0, max_value=100), st.booleans())
def test_promo_percent_valid(percent, lower):
    code = f"OFF{percent}"
    assert promo_percent(code.lower() if lower else code) == percent


@given(st.sampled_from("12345678"), st.text(alphabet="0123456789", min_size=5, max_size=5))
def test_delivery_zone_valid(first, tail):
    expected = {"1": "North", "2": "North", "3": "West", "4": "West",
                "5": "South", "6": "South", "7": "East", "8": "East"}
    assert delivery_zone(first + tail) == expected[first]


@pytest.mark.parametrize("value", [None, "", " ", "pen", ":10x2", "pen:-1x2", "pen:10x0", "pen:10x-2", "pen:1.5x2", "pen:10x2,", "pen:10x2,bad", "pen:10x2x3", "pen:10x2:3", "pen:10x" + "9" * 5000])
def test_cart_malformed_returns_zero(value):
    assert cart_total(value) == 0


@pytest.mark.parametrize("value", [None, "", "OFF", "XOFF20", "OFF20OFF30", "OFF-1", "OFF101", "OFF1.5", "OFF+20", "OFF 20", "OFF" + "9" * 5000])
def test_promo_malformed_returns_zero(value):
    assert promo_percent(value) == 0


@pytest.mark.parametrize("value", [None, "", "5", "56008", "5600850", "056008", "956008", "5abcde", "5\u0661\u0662\u0663\u0664\u0665", 560085])
def test_pincode_malformed_returns_unknown(value):
    assert delivery_zone(value) == "Unknown"


def test_examples_and_whitespace():
    assert cart_total(" pen : 10 x 2 , book : 250 x 1 ") == 270
    assert promo_percent(" off20 ") == 20
    assert delivery_zone(" 560085 ") == "South"


@given(st.text(min_size=1).filter(lambda s: any(c not in "0123456789" for c in s)))
def test_pincode_rejects_non_ascii_digits(tail):
    assert delivery_zone("5" + tail) == "Unknown"


@pytest.mark.parametrize("inputs,expected", [
    ("pen:10x2,book:250x1\nOFF20\n560085\n", ["Cart Total: 270", "Discount Percent: 20", "Delivery Zone: South"]),
    ("bad\nOFF101\n5\n", ["Cart Total: 0", "Discount Percent: 0", "Delivery Zone: Unknown"]),
    ("", ["Input cancelled."]),
])
def test_cli(inputs, expected):
    run = subprocess.run([sys.executable, str(Path(__file__).with_name("shopping_cart.py"))], input=inputs, text=True, capture_output=True, timeout=10)
    assert run.returncode == 0
    assert all(fragment in run.stdout for fragment in expected)
