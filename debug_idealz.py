# debug_idealz.py - Debug IdealZ scraper with visible browser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
# Remove headless to see what's happening
# chrome_options.add_argument("--headless")  # COMMENTED OUT
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

try:
    print("Opening IdealZ website...")
    driver.get("https://idealzpricelist.netlify.app/")
    
    print("Waiting 10 seconds...")
    time.sleep(10)  # Longer wait
    
    # Check if page loaded
    print(f"Page title: {driver.title}")
    
    # Try to find table
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Found {len(tables)} tables")
    
    # Try to find rows
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"Found {len(rows)} rows")
    
    # Print first few rows
    for i, row in enumerate(rows[:5]):
        print(f"Row {i}: {row.text}")
    
    input("Press Enter to close browser...")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()