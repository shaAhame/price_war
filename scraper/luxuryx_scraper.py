# scraper/luxuryx_scraper.py - Fixed price extraction

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def scrape_luxuryx(url, category):
    """Scrape LuxuryX.lk pages with better price extraction"""
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
        time.sleep(6)  # Wait for JavaScript
        
        # Get all list items
        items = driver.find_elements(By.TAG_NAME, "li")
        
        for li in items:
            try:
                text = li.text.strip()
                
                # Must contain both product name and LKR
                if not text or "LKR" not in text:
                    continue
                
                # Split by LKR
                parts = text.split("LKR")
                
                if len(parts) >= 2:
                    # Product name is before LKR
                    name = parts[0].replace("*", "").strip()
                    
                    # Price is after LKR - take first number group
                    price_part = parts[1].strip()
                    
                    # Extract all digits (handles commas, spaces, etc)
                    price_match = re.findall(r'[\d,]+', price_part)
                    
                    if price_match:
                        # Take first number found
                        price_str = price_match[0].replace(',', '').replace(' ', '')
                        
                        # Validate: must be at least 4 digits (1000+)
                        if len(price_str) >= 4 and price_str.isdigit():
                            price = int(price_str)
                            
                            # Skip if price is 0 or unreasonably high (>10M)
                            if 1000 <= price <= 10000000:
                                products.append({
                                    "site": "LuxuryX",
                                    "category": category,
                                    "product": name,
                                    "price_LKR": price,
                                    "is_own_shop": False
                                })
                                
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"  ✗ Error scraping {url}: {e}")
    finally:
        if driver:
            driver.quit()
    
    return products