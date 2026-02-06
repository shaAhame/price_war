# scraper/main_scraper.py - Main orchestrator for all scrapers

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.luxuryx_scraper import scrape_luxuryx
from scraper.francium_scraper import scrape_francium
from scraper.woocommerce_scraper import scrape_woocommerce_site
from scraper.selenium_woocommerce_scraper import scrape_with_selenium
from scraper.idealz_scraper import scrape_idealz, save_idealz_prices_to_config
from config import SCRAPING_URLS
import pandas as pd
from datetime import datetime
import json


def main():
    """Main function to run all scrapers and combine results"""
    all_products = []

    print("=" * 60)
    print(f"Starting scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # STEP 1: Scrape your own shop first
    print("\n🏪 Scraping IdealZ (Your Shop)...")
    try:
        idealz_products = scrape_idealz()
        all_products.extend(idealz_products)
        print(f"  ✓ Found {len(idealz_products)} products from your shop")

        # Save your prices for comparison
        if idealz_products:
            my_prices = save_idealz_prices_to_config(idealz_products)
            os.makedirs("data", exist_ok=True)
            with open("data/my_prices.json", "w") as f:
                json.dump(my_prices, f, indent=2)
            print("  ✓ Saved your prices to data/my_prices.json")
    except Exception as e:
        print(f"  ✗ Failed to scrape IdealZ: {e}")

    # STEP 2: Scrape competitors
    print("\n📱 Scraping Competitors...")

    # Scrape LuxuryX sites
    luxuryx_urls = {k: v for k, v in SCRAPING_URLS.items() if "LuxuryX" in k}
    for category, url in luxuryx_urls.items():
        print(f"\nScraping {category}...")
        try:
            products = scrape_luxuryx(url, category)
            all_products.extend(products)
            print(f"  ✓ Found {len(products)} products")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Scrape Francium sites
    francium_urls = {k: v for k, v in SCRAPING_URLS.items() if "Francium" in k}
    for category, url in francium_urls.items():
        print(f"\nScraping {category}...")
        try:
            products = scrape_francium(url, category)
            all_products.extend(products)
            print(f"  ✓ Found {len(products)} products")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Scrape WooCommerce sites (all others use WooCommerce)
    woocommerce_sites = [
        "PresentSolution",
        "DoctorMobile",
        "GeniusMobile",
        "LifeMobile",
        "GQMobiles",
        "XMobile",
    ]

    # Sites that need Selenium (JavaScript-heavy)
    selenium_sites = ["DoctorMobile", "LifeMobile", "GQMobiles", "XMobile"]

    for site_name in woocommerce_sites:
        site_urls = {k: v for k, v in SCRAPING_URLS.items() if site_name in k}
        for category, url in site_urls.items():
            print(f"\nScraping {category}...")
            try:
                if site_name in selenium_sites:
                    # Use Selenium for JavaScript-heavy sites
                    print(f"  (using Selenium for {site_name})")
                    products = scrape_with_selenium(url, category, site_name)
                else:
                    # Use requests for standard WooCommerce sites
                    products = scrape_woocommerce_site(url, category, site_name)

                all_products.extend(products)
                print(f"  ✓ Found {len(products)} products")
            except Exception as e:
                print(f"  ✗ Error: {e}")

    # Save to CSV
    if all_products:
        df = pd.DataFrame(all_products)
        df["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        output_file = "data/all_products.csv"
        df.to_csv(output_file, index=False)

        # Separate your shop's data from competitors
        your_products = df[df.get("is_own_shop", False) == True]
        competitor_products = df[df.get("is_own_shop", False) == False]

        print("\n" + "=" * 60)
        print(f"✓ Successfully scraped {len(all_products)} products")
        print(f"  - Your shop: {len(your_products)} products")
        print(f"  - Competitors: {len(competitor_products)} products")
        print(f"✓ Saved to '{output_file}'")
        print("=" * 60)

        # Show summary by site
        print("\nSummary by site:")
        summary = df.groupby("site").size().sort_values(ascending=False)
        for site, count in summary.items():
            print(f"  {site}: {count} products")
    else:
        print("\n⚠ No products scraped!")


if __name__ == "__main__":
    main()
