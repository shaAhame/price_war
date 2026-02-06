# scraper/idealz_scraper.py - Custom scraper for IdealZ (React/Vue app)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
from scraper.utils import parse_price

def scrape_idealz(url="https://idealzpricelist.netlify.app/"):
    """
    Scrape IdealZ price list - Custom for React/Vue app
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    products = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait longer for React/Vue to render
        print("  Waiting for page to load...")
        time.sleep(8)
        
        # Click on iPhone tab to load products
        try:
            iphone_button = driver.find_element(By.XPATH, "//button[contains(text(), 'iPhone')]")
            iphone_button.click()
            time.sleep(3)
        except Exception as e:
            print("  Could not click iPhone button, trying alternative...")
        
        # Get all text content from the page
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Parse the text to extract products
        # Format appears to be: "Product Name    Rs. XXX,XXX    Rs. XXX,XXX"
        lines = page_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line in ['Price List', 'Apple Care', 'Genext', 'Company', 
                                     'Apple Devices', 'Android Devices', 'Accessories',
                                     'iPhone', 'Mac & iPad', 'Watch & Accessories']:
                continue
            
            # Look for lines with "iPhone", "iPad", "MacBook", "AirPods", "Watch", "Samsung"
            if any(keyword in line for keyword in ['iPhone', 'iPad', 'MacBook', 'AirPods', 'Watch', 'Galaxy', 'Samsung']):
                # Check if next lines contain prices
                try:
                    # Pattern: Product name on one line, prices on next lines
                    product_name = line
                    
                    # Look ahead for price lines
                    standard_price = None
                    cash_price = None
                    
                    for j in range(1, 4):  # Check next 3 lines
                        if i + j < len(lines):
                            next_line = lines[i + j].strip()
                            
                            # Extract prices using regex
                            prices = re.findall(r'Rs\.\s*([\d,]+)', next_line)
                            
                            if len(prices) >= 2:
                                standard_price = parse_price(prices[0])
                                cash_price = parse_price(prices[1])
                                break
                            elif len(prices) == 1:
                                standard_price = parse_price(prices[0])
                                cash_price = standard_price
                                break
                    
                    # If we found prices in the same line
                    if not standard_price:
                        prices = re.findall(r'Rs\.\s*([\d,]+)', line)
                        if len(prices) >= 2:
                            # Extract product name (remove prices)
                            product_name = re.sub(r'Rs\.\s*[\d,]+', '', line).strip()
                            standard_price = parse_price(prices[0])
                            cash_price = parse_price(prices[1])
                        elif len(prices) == 1:
                            product_name = re.sub(r'Rs\.\s*[\d,]+', '', line).strip()
                            standard_price = parse_price(prices[0])
                            cash_price = standard_price
                    
                    if standard_price:
                        category = categorize_product(product_name)
                        
                        products.append({
                            "site": "IdealZ (Your Shop)",
                            "category": category,
                            "product": product_name,
                            "price_LKR": standard_price,
                            "cash_price_LKR": cash_price if cash_price else standard_price,
                            "is_own_shop": True
                        })
                        
                except Exception:
                    continue
        
        # Alternative approach: Try to find product elements by class or structure
        if len(products) == 0:
            print("  Trying alternative extraction method...")
            
            # Look for all div elements that might contain products
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'iPhone') or contains(text(), 'iPad') or contains(text(), 'MacBook')]")
            
            for elem in elements:
                try:
                    text = elem.text.strip()
                    if 'Rs.' in text:
                        # Extract product and prices
                        prices = re.findall(r'Rs\.\s*([\d,]+)', text)
                        product_name = re.sub(r'Rs\.\s*[\d,]+', '', text).strip()
                        
                        if prices and product_name:
                            standard_price = parse_price(prices[0])
                            cash_price = parse_price(prices[1]) if len(prices) > 1 else standard_price
                            
                            if standard_price:
                                category = categorize_product(product_name)
                                
                                products.append({
                                    "site": "IdealZ (Your Shop)",
                                    "category": category,
                                    "product": product_name,
                                    "price_LKR": standard_price,
                                    "cash_price_LKR": cash_price,
                                    "is_own_shop": True
                                })
                except Exception:
                    continue
        
        # Remove duplicates
        seen = set()
        unique_products = []
        for p in products:
            key = (p['product'], p['price_LKR'])
            if key not in seen:
                seen.add(key)
                unique_products.append(p)
        
        products = unique_products
                
    except Exception as e:
        print(f"  ✗ Error scraping IdealZ: {e}")
    finally:
        if driver:
            driver.quit()
    
    return products

def categorize_product(product_name):
    """Categorize product based on name"""
    product_lower = product_name.lower()
    
    if "iphone" in product_lower:
        return "IdealZ iPhone"
    elif "ipad" in product_lower:
        return "IdealZ iPad"
    elif "macbook" in product_lower or "mac" in product_lower:
        return "IdealZ MacBook"
    elif "airpod" in product_lower:
        return "IdealZ AirPods"
    elif "watch" in product_lower:
        return "IdealZ Watch"
    elif "samsung" in product_lower or "galaxy" in product_lower:
        return "IdealZ Samsung"
    else:
        return "IdealZ Accessories"

def save_idealz_prices_to_config(products):
    """Extract prices and save to dictionary"""
    my_prices = {}
    for product in products:
        my_prices[product['product']] = product['price_LKR']
    return my_prices