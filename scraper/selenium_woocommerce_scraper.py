"""
scraper/selenium_woocommerce_scraper.py
Selenium-based scraper for JavaScript-heavy WooCommerce sites
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scraper.utils import parse_price


def scrape_with_selenium(url, category, site_name, max_pages=3):
    """
    Scrape WooCommerce sites that require JavaScript rendering

    Args:
        url: Base category URL
        category: Category name for labeling
        site_name: Site name for labeling
        max_pages: Number of pages to scrape
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    driver = None
    products = []

    try:
        driver = webdriver.Chrome(options=chrome_options)

        for page in range(1, max_pages + 1):
            page_url = f"{url}page/{page}/" if page > 1 else url

            try:
                print(f"    Fetching with Selenium: {page_url}")
                driver.get(page_url)

                # Wait for products to load
                wait = WebDriverWait(driver, 10)

                # Try multiple product selectors
                product_selectors = [
                    "li.product",
                    "div.product",
                    "div[data-product-id]",
                    "article[data-product-id]",
                    ".product-item",
                    ".wc-product-item",
                ]

                product_elements = []
                for selector in product_selectors:
                    try:
                        product_elements = wait.until(
                            EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR, selector)
                            )
                        )
                        if product_elements:
                            print(
                                f"    Found {len(product_elements)} products with: {selector}"
                            )
                            break
                    except:
                        continue

                if not product_elements:
                    print(f"    No products found on page {page}")
                    break

                page_found = 0

                for product_elem in product_elements:
                    try:
                        # Extract product name
                        name = None
                        name_selectors = [
                            "h2.woocommerce-loop-product__title",
                            "h3.product-title",
                            ".product-title",
                            "h2",
                            "h3",
                            "a",
                        ]

                        for name_sel in name_selectors:
                            try:
                                name_elem = product_elem.find_element(
                                    By.CSS_SELECTOR, name_sel
                                )
                                name = name_elem.text.strip()
                                if name and len(name) > 3:
                                    break
                            except:
                                pass

                        # Extract price
                        price = None
                        price_selectors = [
                            "span.woocommerce-Price-amount.amount bdi",
                            "span.woocommerce-Price-amount.amount",
                            "span.amount",
                            "span.price",
                            ".price",
                            "bdi",
                        ]

                        for price_sel in price_selectors:
                            try:
                                price_elems = product_elem.find_elements(
                                    By.CSS_SELECTOR, price_sel
                                )
                                if price_elems:
                                    price_text = price_elems[-1].text
                                    price = parse_price(price_text)
                                    if price and price > 100:
                                        break
                            except:
                                pass

                        if name and price and price > 100:
                            products.append(
                                {
                                    "site": site_name,
                                    "category": category,
                                    "product": name,
                                    "price_LKR": price,
                                    "is_own_shop": False,
                                }
                            )
                            page_found += 1

                    except Exception as e:
                        continue

                print(f"    Found {page_found} products on page {page}")

                if page_found == 0:
                    break

                time.sleep(2)

            except Exception as e:
                print(f"    Error loading page: {e}")
                break

    except Exception as e:
        print(f"  Error with Selenium: {e}")
    finally:
        if driver:
            driver.quit()

    return products
