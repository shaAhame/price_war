# WooCommerce Sites - Debug Analysis & Fixes

## Summary Status

| Site            | Status     | Issue                   | Fix                   |
| --------------- | ---------- | ----------------------- | --------------------- |
| PresentSolution | ✅ WORKING | —                       | None needed           |
| GeniusMobile    | ✅ WORKING | —                       | None needed           |
| DoctorMobile    | ❌ BROKEN  | Using "ecomall" theme   | Need custom selectors |
| LifeMobile      | ❌ BROKEN  | 403 Forbidden (blocked) | Need better headers   |
| GQMobiles       | ❌ BROKEN  | Non-standard structure  | Need investigation    |
| XMobile         | ❌ BROKEN  | 404 Not Found           | URL invalid/down      |

---

## Working Sites (No Action Needed)

### ✅ PresentSolution

- **Selector**: `div.product:not(.product-category)`
- **Name**: `h3`
- **Price**: `span.woocommerce-Price-amount.amount bdi`
- **Status**: Perfect, already working

### ✅ GeniusMobile

- **Selector**: `li.product:not(.product-category)`
- **Name**: `h2.woocommerce-loop-product__title`
- **Price**: `span.woocommerce-Price-amount.amount bdi`
- **Status**: Perfect, already working

---

## Broken Sites - Solutions

### ❌ DoctorMobile - Theme: "ecomall"

**Problem**: Uses "ecomall" WooCommerce child theme with different HTML structure

**Solution**: Add custom selectors to woocommerce_scraper.py

The HTML shows it uses class `wd-product` instead of standard `product` class.

**Fix to add**:

```python
selectors = [
    "li.product:not(.product-category)",
    "div.product:not(.product-category)",
    "li.product-type-simple",
    "div.product-small",
    ".products li:not(.product-category)",
    "div[data-product-id]",
    "div.wd-product",  # ADD THIS LINE for ecomall theme
]
```

**For names** (ecomall theme uses different structure):

```python
name_selectors = [
    "h2.woocommerce-loop-product__title",
    "h3.product-title",
    "h2.product-title",
    ".product-title",
    "a.woocommerce-LoopProduct-link",
    "h2",
    "h3",
    'a[href*="product"]',
    ".product-name",
    ".product-item-title",
    "a.product-image-link",  # ADD THIS for ecomall
]
```

---

### ❌ LifeMobile - 403 Forbidden

**Problem**: Server is blocking requests (403 Forbidden status)

**Cause**: Missing or insufficient headers to appear as a real browser

**Solution**: Improve headers in woocommerce_scraper.py

Current headers need to add more browser-like authentication:

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': url,  # ADD THIS
    'Origin': url.split('/product-category')[0],  # ADD THIS
    'Accept-Encoding': 'gzip, deflate, br',  # ADD THIS
}
```

Also add delay between requests to look more human-like:

```python
import time
# Add this in the page loop:
time.sleep(1)  # Before each request
```

---

### ❌ GQMobiles - No Standard HTML Structure

**Problem**: Site doesn't use standard WooCommerce HTML at all (no 'product' classes found)

**Possible Causes**:

- Custom theme with completely different HTML structure
- Site using POST requests instead of standard WooCommerce
- Site using JavaScript rendering (needs Selenium)

**Investigation Steps**:

1. Open site in browser: https://gqmobiles.lk/product-category/iphone/
2. Right-click → Inspect Element on a product
3. Find the product container's class/id
4. Check if it uses custom classes like `item-`, `product-item-`, `prod-`, etc.

**Temporary Workaround**: Use Selenium for this site since standard requests won't work

**Or check**: Maybe the URL structure is wrong - should be verified in config.py

---

### ❌ XMobile - 404 Not Found

**Problem**: URL returns 404 error

**Causes**:

- URL might be incorrect in config.py
- Site structure changed
- Product category URL is wrong

**Solution**: Verify in config.py

Check line with XMobile URL:

```python
# In config.py - find and verify:
"XMobile iPhone": "https://xmobile.lk/product-category/mobile-phone/",
```

Try alternative URLs:

- `https://xmobile.lk/shop/iphone/` (if category name is different)
- `https://xmobile.lk/product-category/iphones/` (singular vs plural)
- `https://xmobile.lk/` (check if site is even up)

---

## Implementation Priority

### High Priority (Easy Fixes):

1. **DoctorMobile**: Add `div.wd-product` selector (2 lines)
2. **LifeMobile**: Add extra headers (5 lines)

### Medium Priority (Investigation Needed):

3. **GQMobiles**: Inspect HTML structure
4. **XMobile**: Verify URL in config.py

---

## Step-by-Step Fix Instructions

### Fix 1: DoctorMobile (5 minutes)

Edit `scraper/woocommerce_scraper.py`:

Find this section (~line 43):

```python
selectors = [
    "li.product:not(.product-category)",
    "div.product:not(.product-category)",
    ...
]
```

Add after last selector:

```python
"div.wd-product",  # ecomall theme
```

Also extend name selectors (~line 65):

```python
name_selectors = [
    ...existing selectors...,
    "a.product-image-link",  # ecomall theme fallback
]
```

### Fix 2: LifeMobile (5 minutes)

Edit `scraper/woocommerce_scraper.py`:

Find the headers section (~line 11):

```python
headers = {
    'User-Agent': '...',
    'Accept': '...',
    'Accept-Language': '...',
    'Connection': 'keep-alive',
}
```

Add these lines before the closing brace:

```python
'Referer': url,
'Origin': url.split('/product-category')[0],
'Accept-Encoding': 'gzip, deflate, br',
```

Also add delay before each request (~line 27):

```python
print(f"    Fetching: {page_url}")
time.sleep(1)  # ADD THIS LINE
response = requests.get(page_url, headers=headers, timeout=20)
```

### Fix 3: GQMobiles (Investigation)

1. Open browser: https://gqmobiles.lk/product-category/iphone/
2. Right-click first product → Inspect
3. Look for container's class name
4. Note the structure
5. Update selectors in woocommerce_scraper.py

**Alternative**: If site requires JavaScript rendering:

- Create `scraper/gqmobiles_scraper.py` using Selenium
- Import and use in main_scraper.py

### Fix 4: XMobile (Verification)

1. Check `config.py` line with "XMobile"
2. Open URL in browser to verify it works
3. If 404, find correct URL
4. Update config.py

---

## Testing After Fixes

For each fix, test immediately:

```python
# test_one_site.py
from scraper.woocommerce_scraper import scrape_woocommerce_site

# Test DoctorMobile
products = scrape_woocommerce_site(
    "https://doctormobile.lk/product-category/iphone/",
    "iPhone",
    "DoctorMobile"
)
print(f"DoctorMobile: {len(products)} products")

# Test LifeMobile
products = scrape_woocommerce_site(
    "https://lifemobile.lk/product-category/iphone/",
    "iPhone",
    "LifeMobile"
)
print(f"LifeMobile: {len(products)} products")
```

Run with:

```bash
python test_one_site.py
```

---

## Summary of Changes Needed

1. **woocommerce_scraper.py**:
   - Add `"div.wd-product"` to selectors list (DoctorMobile)
   - Add `"a.product-image-link"` to name_selectors (DoctorMobile)
   - Add `Referer`, `Origin`, `Accept-Encoding` headers (LifeMobile)
   - Add `time.sleep(1)` before requests (LifeMobile)

2. **config.py**:
   - Verify XMobile URL is correct

3. **Investigate**:
   - GQMobiles HTML structure (may need custom scraper)

---

## Additional Notes

- **PresentSolution & GeniusMobile** are already working perfectly
- **DoctorMobile fix is simple** - just add one selector
- **LifeMobile fix is simple** - just add headers and delay
- **GQMobiles & XMobile** need investigation but are lower priority

After applying these fixes, run:

```bash
python scraper/main_scraper.py
```

This should successfully scrape all working sites!
