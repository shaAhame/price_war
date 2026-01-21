# debug_woocommerce.py - Debug WooCommerce scraper

import requests
from bs4 import BeautifulSoup

url = "https://presentsolution.lk/product-category/iphone/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=20)
soup = BeautifulSoup(response.content, 'html.parser')

# Find products
products = soup.select('div.product')
print(f"Found {len(products)} product divs\n")

# Examine first product structure
if products:
    first_product = products[0]
    print("=" * 60)
    print("FIRST PRODUCT HTML:")
    print("=" * 60)
    print(first_product.prettify()[:1000])  # First 1000 chars
    print("\n" + "=" * 60)
    print("SEARCHING FOR ELEMENTS:")
    print("=" * 60)
    
    # Try different selectors
    selectors_to_try = [
        'h2.woocommerce-loop-product__title',
        'h3.product-title',
        '.product-title',
        'a.woocommerce-LoopProduct-link',
        'h2',
        'h3',
        'a[href*="product"]',
    ]
    
    for sel in selectors_to_try:
        elem = first_product.select_one(sel)
        if elem:
            print(f"✓ {sel}: {elem.get_text(strip=True)[:50]}")
        else:
            print(f"✗ {sel}: Not found")
    
    print("\n" + "=" * 60)
    print("PRICE ELEMENTS:")
    print("=" * 60)
    
    price_selectors = [
        'span.woocommerce-Price-amount',
        'span.amount',
        '.price',
        'bdi',
        'ins',
    ]
    
    for sel in price_selectors:
        elems = first_product.select(sel)
        if elems:
            print(f"✓ {sel}: {[e.get_text(strip=True) for e in elems]}")
        else:
            print(f"✗ {sel}: Not found")