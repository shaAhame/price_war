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
# Find products - using Improved selectors
products = soup.select('div.product:not(.product-category)')
if not products:
    print("Trying alternative selector...")
    products = soup.select('li.product:not(.product-category)')

print(f"Found {len(products)} product divs (excluding categories)\n")

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
            try:
                print(f"[OK] {sel}: {elem.get_text(strip=True)[:50]}")
            except:
                print(f"[OK] {sel}: (Found but encoding error printing)")
        else:
            print(f"[NO] {sel}: Not found")
    
    print("\n" + "=" * 60)
    print("PRICE ELEMENTS:")
    print("=" * 60)
    
    price_selectors = [
        'span.woocommerce-Price-amount.amount bdi',
        'span.woocommerce-Price-amount.amount',
        'span.amount',
        '.price',
        'bdi',
        'ins',
    ]
    
    for sel in price_selectors:
        elems = first_product.select(sel)
        if elems:
            try:
                texts = [e.get_text(strip=True) for e in elems]
                print(f"[OK] {sel}: {texts}")
            except:
                print(f"[OK] {sel}: (Found but encoding error printing)")
        else:
            print(f"[NO] {sel}: Not found")