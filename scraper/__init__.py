# scraper/__init__.py
# Makes the scraper directory a Python package

from .idealz_scraper import scrape_idealz, save_idealz_prices_to_config
from .luxuryx_scraper import scrape_luxuryx
from .francium_scraper import scrape_francium
from .woocommerce_scraper import scrape_woocommerce_site

__all__ = [
    'scrape_idealz',
    'save_idealz_prices_to_config',
    'scrape_luxuryx',
    'scrape_francium',
    'scrape_woocommerce_site'
]