# scraper/woocommerce_scraper.py - Generic scraper for WooCommerce sites

import requests
from bs4 import BeautifulSoup
import time

def scrape_woocommerce_site(url, category, site_name):
    """
    Generic scraper for WooCommerce-based sites
    Works for: PresentSolution, DoctorMobile, GeniusMobile, LifeMobile, GQMobiles, XMobile
    """
    products = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Try first 3 pages for each category
        for page in range(1, 4):
            page_url = f"{url}page/{page}/" if page > 1 else url
            
            try:
                response = requests.get(page_url, headers=headers, timeout=15)
                if response.status_code != 200:
                    break
            except:
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # WooCommerce product selectors (try multiple patterns)
            selectors = [
                'li.product',
                'div.product',
                'article.product',
                'div.product-small',
                'div.product-grid-item',
                'li.product-type-simple',
                'div.product-inner'
            ]
            
            product_elements = []
            for selector in selectors:
                product_elements = soup.select(selector)
                if product_elements:
                    break
            
            if not product_elements:
                break
            
            page_products_found = 0
            
            for product in product_elements:
                try:
                    # Extract product name - try multiple selectors
                    name_elem = (
                        product.select_one('h2.woocommerce-loop-product__title') or
                        product.select_one('h3.product-title') or
                        product.select_one('h2.product-title') or
                        product.select_one('.product-title') or
                        product.select_one('a.woocommerce-LoopProduct-link') or
                        product.select_one('.woocommerce-loop-product__title')
                    )
                    
                    # Extract price - try multiple selectors
                    price_elem = (
                        product.select_one('span.woocommerce-Price-amount.amount') or
                        product.select_one('span.price ins span.amount') or
                        product.select_one('span.price span.amount') or
                        product.select_one('ins span.amount') or
                        product.select_one('.price ins .woocommerce-Price-amount') or
                        product.select_one('.price .woocommerce-Price-amount') or
                        product.select_one('.price')
                    )
                    
                    if name_elem and price_elem:
                        name = name_elem.get_text(strip=True)
                        price_text = price_elem.get_text(strip=True)
                        
                        # Extract numeric price
                        price = "".join(c for c in price_text if c.isdigit())
                        
                        # Sanity checks
                        if price and name and len(price) >= 4:  # At least 1000 LKR
                            products.append({
                                "site": site_name,
                                "category": category,
                                "product": name,
                                "price_LKR": int(price),
                                "is_own_shop": False
                            })
                            page_products_found += 1
                except Exception as e:
                    continue
            
            # If no products found on this page, don't try next page
            if page_products_found == 0:
                break
            
            time.sleep(1)  # Be polite between pages
            
    except Exception as e:
        print(f"  ✗ Error scraping {url}: {e}")
    
    return products