# Lab 7: Shopping Cart Fuzz Testing

Only the repository's three original test functions are used. Each keeps its
original `@given(st.text() | st.none())` decorator. The empty bodies are completed
with calls to cart_total(s), promo_percent(s), and delivery_zone(s), respectively.
No additional test cases, strategies, assertions or custom settings are included.

Run from this folder:

```powershell
python -m pip install -r requirements.txt
python shopping_cart.py
python -m pytest test_shopping_cart.py -v
```

Expected: 3 failed with the original application; 3 passed after the fixes.
The original incomplete test template and application are preserved in original/.
The supplied handout uses generic processor.py filenames; this assigned repository
uses shopping_cart.py and test_shopping_cart.py.

Invalid carts/promos return 0 and invalid/unsupported pincodes return Unknown.
A malformed cart is rejected as a whole. The PDF describes the chosen policy.
The original tests establish only absence of crashes for generated text and None;
they do not establish correct return values or robustness for all other types.

evidence/ contains current real before/after logs, metadata, and output-viewer
screenshots. The PDF is in the workspace DELIVERABLES folder. Screenshots show
recorded subprocess output in a browser, rather than an interactive terminal.
No commit or push has been performed.
