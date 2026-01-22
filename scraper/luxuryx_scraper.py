# scraper/luxuryx_scraper.py - Fixed to remove zero prices

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
from scraper.utils import parse_price

def scrape_luxuryx(url, category):
    """Scrape LuxuryX.lk with proper price extraction"""
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
        time.sleep(6)
        
        items = driver.find_elements(By.TAG_NAME, "li")
        
        for li in items:
            try:
                text = li.text.strip()
                
                if not text or "LKR" not in text:
                    continue
                
                # Split by LKR
                if text.count("LKR") >= 1:
                    parts = text.split("LKR")
                    
                    if len(parts) >= 2:
                        name = parts[0].replace("*", "").strip()
                        price_part = parts[1].strip()
                        
                        price = parse_price(price_part)
                        
                        if price and name:
                            # Validation: 10,000 to 10,000,000 LKR range
                            if 10000 <= price <= 10000000:
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
        print(f"  ✗ Error: {e}")
    finally:
        if driver:
            driver.quit()
    
    return products