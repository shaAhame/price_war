# scraper/woocommerce_scraper.py - Improved WooCommerce scraper with better error handling

import requests
from bs4 import BeautifulSoup
import time
from scraper.utils import parse_price


def scrape_woocommerce_site(url, category, site_name):
    """
    Generic scraper for WooCommerce-based sites with improved price extraction
    """
    products = []
    # Enhanced headers to avoid 403 Forbidden errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        # Try first 3 pages
        for page in range(1, 4):
            page_url = f"{url}page/{page}/" if page > 1 else url

            try:
                print(f"    Fetching: {page_url}")
                # Add minimal delay to appear more human-like (helps with 403 errors)
                time.sleep(0.5)
                response = requests.get(page_url, headers=headers, timeout=20)

                if response.status_code != 200:
                    print(f"    Status code: {response.status_code}")
                    break

            except Exception as e:
                print(f"    Request failed: {e}")
                break

            soup = BeautifulSoup(response.content, "html.parser")

            # Multiple selector patterns
            # Exclude 'product-category' which are just links to subcategories
            selectors = [
                "li.product:not(.product-category)",
                "div.product:not(.product-category)",
                "li.product-type-simple",
                "div.product-small",
                ".products li:not(.product-category)",
                "div[data-product-id]",
                "div.wd-product",  # ecomall WooCommerce theme
            ]

            product_elements = []
            used_selector = None
            for selector in selectors:
                product_elements = soup.select(selector)
                if product_elements:
                    used_selector = selector
                    print(
                        f"    Using selector: {selector} (found {len(product_elements)})"
                    )
                    break

            if not product_elements:
                print(f"    No products found with any selector")
                break

            page_found = 0
            page_no_price = 0

            for product in product_elements:
                try:
                    # Find name
                    name_selectors = [
                        "h2.woocommerce-loop-product__title",
                        "h3.product-title",
                        "h2.product-title",
                        ".product-title",
                        "a.woocommerce-LoopProduct-link",
                        "h2",
                        "h3",
                        'a[href*="product"]',
                        ".product-name",
                        ".product-item-title",
                        "a.product-image-link",  # ecomall theme
                    ]

                    name_elem = None
                    for sel in name_selectors:
                        name_elem = product.select_one(sel)
                        if name_elem:
                            break

                    # Find price
                    price_selectors = [
                        "span.woocommerce-Price-amount.amount bdi",  # Specific for new WC
                        "span.woocommerce-Price-amount.amount",
                        "ins span.amount",
                        "span.price span.amount",
                        ".price ins .amount",
                        ".price .amount",
                        "span.amount",
                        "bdi",
                        ".price",
                        "span.product-price",
                        ".sale-price",
                        ".product-amount",
                        "span[data-price]",
                        "ins",
                        "strong.amount",
                        "span.product-sale-price",
                    ]

                    price_elem = None
                    for sel in price_selectors:
                        # Get the LAST matching element if there are multiple (often sale price is last)
                        elems = product.select(sel)
                        if elems:
                            price_elem = elems[-1]
                            break

                    if name_elem and price_elem:
                        name = name_elem.get_text(strip=True)
                        price_text = price_elem.get_text(strip=True)

                        price = parse_price(price_text)

                        if (
                            price and name and price > 100
                        ):  # Filter out weird low prices
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
                        elif name and not price:
                            page_no_price += 1
                    elif name_elem and not price_elem:
                        page_no_price += 1

                except Exception as e:
                    continue

            print(
                f"    Found {page_found} products from {len(product_elements)} items on page {page}"
                + (f" ({page_no_price} missing prices)" if page_no_price > 0 else "")
            )

            if page_found == 0:
                break

            time.sleep(2)

    except Exception as e:
        print(f"    Error: {e}")

    return products
