# scraper/luxuryx_scraper.py - Scraper for LuxuryX.lk (uses Selenium)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def scrape_luxuryx(url, category):
    """Scrape LuxuryX.lk pages"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    products = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load
        
        items = driver.find_elements(By.TAG_NAME, "li")
        
        for li in items:
            try:
                text = li.text.strip()
                if "LKR" in text:
                    parts = text.split("LKR")
                    if len(parts) == 2:
                        name = parts[0].replace("*", "").strip()
                        price = "".join(c for c in parts[1] if c.isdigit())
                        if price and name:
                            products.append({
                                "site": "LuxuryX",
                                "category": category,
                                "product": name,
                                "price_LKR": int(price),
                                "is_own_shop": False
                            })
            except:
                continue
                
    except Exception as e:
        print(f"  ✗ Error scraping {url}: {e}")
    finally:
        if driver:
            driver.quit()
    
    return products