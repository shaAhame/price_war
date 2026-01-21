# scraper/idealz_scraper.py - Scraper for your own shop (IdealZ)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_idealz(url="https://idealzpricelist.netlify.app/"):
    """
    Scrape IdealZ price list
    Returns products with both standard and cash prices
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
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 15)
        time.sleep(5)  # Extra wait for JS rendering
        
        # Try multiple approaches to extract data
        
        # Approach 1: Try to execute JavaScript to get the data
        try:
            script = """
                let items = [];
                const rows = document.querySelectorAll('table tbody tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 3) {
                        items.push({
                            product: cells[0].textContent.trim(),
                            standard: cells[1].textContent.trim(),
                            cash: cells[2].textContent.trim()
                        });
                    }
                });
                return items;
            """
            items_data = driver.execute_script(script)
            
            for item in items_data:
                if not item['product']:
                    continue
                    
                product_name = item['product']
                standard_price = "".join(c for c in item['standard'] if c.isdigit())
                cash_price = "".join(c for c in item['cash'] if c.isdigit())
                
                if product_name and standard_price:
                    category = categorize_product(product_name)
                    products.append({
                        "site": "IdealZ (Your Shop)",
                        "category": category,
                        "product": product_name,
                        "price_LKR": int(standard_price),
                        "cash_price_LKR": int(cash_price) if cash_price else int(standard_price),
                        "is_own_shop": True
                    })
        except Exception as e:
            print(f"  ⚠ JavaScript extraction failed: {e}")
            
            # Approach 2: Try traditional DOM parsing
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                
                for row in rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 3:
                            product_name = cells[0].text.strip()
                            standard_price = cells[1].text.strip()
                            cash_price = cells[2].text.strip()
                            
                            # Extract numeric values
                            standard_numeric = "".join(c for c in standard_price if c.isdigit())
                            cash_numeric = "".join(c for c in cash_price if c.isdigit())
                            
                            if product_name and standard_numeric:
                                category = categorize_product(product_name)
                                
                                products.append({
                                    "site": "IdealZ (Your Shop)",
                                    "category": category,
                                    "product": product_name,
                                    "price_LKR": int(standard_numeric),
                                    "cash_price_LKR": int(cash_numeric) if cash_numeric else int(standard_numeric),
                                    "is_own_shop": True
                                })
                    except:
                        continue
            except Exception as e2:
                print(f"  ✗ DOM parsing also failed: {e2}")
                
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
    """
    Extract prices and save to a dictionary format
    This can be used to update MY_PRICES in config.py
    """
    my_prices = {}
    for product in products:
        my_prices[product['product']] = product['price_LKR']
    
    return my_prices