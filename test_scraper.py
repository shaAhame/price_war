# test_scraper.py - Quick test script to verify all scrapers work

import sys
from scraper.idealz_scraper import scrape_idealz
from scraper.luxuryx_scraper import scrape_luxuryx
from scraper.francium_scraper import scrape_francium
from scraper.woocommerce_scraper import scrape_woocommerce_site

def test_idealz():
    """Test IdealZ scraper"""
    print("Testing IdealZ scraper...")
    try:
        products = scrape_idealz()
        print(f"✓ Found {len(products)} products from IdealZ")
        if products:
            print(f"  Sample: {products[0]['product']} - LKR {products[0]['price_LKR']:,}")
        return len(products) > 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_luxuryx():
    """Test LuxuryX scraper"""
    print("\nTesting LuxuryX scraper...")
    try:
        products = scrape_luxuryx("https://luxuryx.lk/iphone-price-in-sri-lanka", "Test iPhone")
        print(f"✓ Found {len(products)} products from LuxuryX")
        if products:
            print(f"  Sample: {products[0]['product']} - LKR {products[0]['price_LKR']:,}")
        return len(products) > 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_francium():
    """Test Francium scraper"""
    print("\nTesting Francium scraper...")
    try:
        products = scrape_francium("https://francium.lk/collections/iphone", "Test iPhone")
        print(f"✓ Found {len(products)} products from Francium")
        if products:
            print(f"  Sample: {products[0]['product']} - LKR {products[0]['price_LKR']:,}")
        return len(products) > 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_woocommerce():
    """Test WooCommerce scraper"""
    print("\nTesting WooCommerce scraper...")
    try:
        products = scrape_woocommerce_site(
            "https://presentsolution.lk/product-category/iphone/", 
            "Test iPhone", 
            "PresentSolution"
        )
        print(f"✓ Found {len(products)} products from WooCommerce site")
        if products:
            print(f"  Sample: {products[0]['product']} - LKR {products[0]['price_LKR']:,}")
        return len(products) > 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing All Scrapers")
    print("=" * 60)
    
    results = {
        "IdealZ (Your Shop)": test_idealz(),
        "LuxuryX": test_luxuryx(),
        "Francium": test_francium(),
        "WooCommerce Sites": test_woocommerce()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for scraper, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{scraper}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! You're ready to scrape.")
    else:
        print("⚠ Some tests failed. Check the errors above.")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)