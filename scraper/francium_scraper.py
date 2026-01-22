# scraper/francium_scraper.py - Scraper for Francium.lk (uses Selenium)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from scraper.utils import parse_price

def scrape_francium(url, category):
    """Scrape Francium.lk pages"""
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
        
        product_cards = driver.find_elements(By.CSS_SELECTOR, "div.product-card")
        
        for card in product_cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, ".product-card__title").text.strip()
                price_text = card.find_element(By.CSS_SELECTOR, ".price").text
                
                price = parse_price(price_text)
                
                if price and name:
                    products.append({
                        "site": "Francium",
                        "category": category,
                        "product": name,
                        "price_LKR": price,
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