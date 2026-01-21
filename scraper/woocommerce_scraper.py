# scraper/woocommerce_scraper.py - Improved WooCommerce scraper

import requests
from bs4 import BeautifulSoup
import time

def scrape_woocommerce_site(url, category, site_name):
    """
    Generic scraper for WooCommerce-based sites
    """
    products = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        # Try first 2 pages
        for page in range(1, 3):
            page_url = f"{url}page/{page}/" if page > 1 else url
            
            try:
                print(f"    Fetching: {page_url}")
                response = requests.get(page_url, headers=headers, timeout=20)
                
                if response.status_code != 200:
                    print(f"    Status code: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"    Request failed: {e}")
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selector patterns
            selectors = [
                'li.product',
                'div.product',
                'li.product-type-simple',
                'div.product-small',
                '.products li',
                'ul.products li',
            ]
            
            product_elements = []
            for selector in selectors:
                product_elements = soup.select(selector)
                if product_elements:
                    print(f"    Using selector: {selector} (found {len(product_elements)})")
                    break
            
            if not product_elements:
                print(f"    No products found with any selector")
                break
            
            page_found = 0
            
            for product in product_elements:
                try:
                    # Find name
                    name_selectors = [
                        'h2.woocommerce-loop-product__title',
                        'h3.product-title',
                        'h2.product-title',
                        '.product-title',
                        'a.woocommerce-LoopProduct-link',
                    ]
                    
                    name_elem = None
                    for sel in name_selectors:
                        name_elem = product.select_one(sel)
                        if name_elem:
                            break
                    
                    # Find price
                    price_selectors = [
                        'span.woocommerce-Price-amount.amount',
                        'ins span.amount',
                        'span.price span.amount',
                        '.price ins .amount',
                        '.price .amount',
                        'span.amount',
                    ]
                    
                    price_elem = None
                    for sel in price_selectors:
                        price_elem = product.select_one(sel)
                        if price_elem:
                            break
                    
                    if name_elem and price_elem:
                        name = name_elem.get_text(strip=True)
                        price_text = price_elem.get_text(strip=True)
                        
                        # Extract digits
                        price = "".join(c for c in price_text if c.isdigit())
                        
                        if price and name and len(price) >= 4:
                            products.append({
                                "site": site_name,
                                "category": category,
                                "product": name,
                                "price_LKR": int(price),
                                "is_own_shop": False
                            })
                            page_found += 1
                            
                except Exception as e:
                    continue
            
            print(f"    Found {page_found} products on page {page}")
            
            if page_found == 0:
                break
                
            time.sleep(2)
            
    except Exception as e:
        print(f"    Error: {e}")
    
    return products