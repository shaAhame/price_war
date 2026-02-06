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
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = None
    products = []

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load

        # Try multiple selectors for product cards
        product_selectors = [
            "div.product-card",
            "div.product",
            "li.product-item",
            "div.product-item",
            "article[data-product-id]",
            "a.product-link",
        ]

        product_cards = []
        for selector in product_selectors:
            try:
                product_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if product_cards:
                    print(
                        f"    Found {len(product_cards)} products using selector: {selector}"
                    )
                    break
            except Exception:
                continue

        for card in product_cards:
            try:
                # Try multiple selectors for product name
                name = None
                name_selectors = [
                    ".product-card__title",
                    ".product-title",
                    "h2",
                    "h3",
                    "a.product-link",
                ]
                for name_sel in name_selectors:
                    try:
                        elem = card.find_element(By.CSS_SELECTOR, name_sel)
                        name = elem.text.strip()
                        if name and len(name) > 3:
                            break
                    except Exception:
                        continue

                # Try multiple selectors for price
                price = None
                price_selectors = [
                    ".price",
                    ".product-price",
                    "span.price",
                    "span[data-price]",
                    ".selling-price",
                    "span.amount",
                ]
                price_text = None
                for price_sel in price_selectors:
                    try:
                        elems = card.find_elements(By.CSS_SELECTOR, price_sel)
                        if elems:
                            price_text = elems[-1].text  # Get last price element
                            price = parse_price(price_text)
                            if price:
                                break
                    except Exception:
                        continue

                if price and name and len(name) > 3:
                    products.append(
                        {
                            "site": "Francium",
                            "category": category,
                            "product": name,
                            "price_LKR": price,
                            "is_own_shop": False,
                        }
                    )
            except Exception as e:
                continue

    except Exception as e:
        print(f"  ✗ Error scraping {url}: {e}")
    finally:
        if driver:
            driver.quit()

    return products
