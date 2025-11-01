"""Selenium scraper template for JS-heavy pages.
Requires a compatible webdriver (e.g., chromedriver) in PATH.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime
import time
import os

CHROME_DRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH", "chromedriver")  # put chromedriver in PATH or set env
START_URL = "https://example.com"  # change to allowed/test URL

def start_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=opts)
    return driver

def scrape(out_csv="data/scraped_prices_selenium.csv"):
    driver = start_driver(headless=True)
    driver.get(START_URL)
    wait = WebDriverWait(driver, 10)
    # Example: wait for product cards to load
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-card")))
    cards = driver.find_elements(By.CSS_SELECTOR, ".product-card")
    results = []
    for c in cards:
        try:
            title = c.find_element(By.CSS_SELECTOR, ".product-title").text
        except:
            title = None
        try:
            price_raw = c.find_element(By.CSS_SELECTOR, ".price").text
        except:
            price_raw = None
        try:
            link = c.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        except:
            link = None
        results.append({
            "title": title,
            "price_raw": price_raw,
            "link": link,
            "scrape_ts": datetime.utcnow().isoformat()
        })
    # save
    keys = ["title","price_raw","link","scrape_ts"]
    with open(out_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(results)
    driver.quit()
    print(f"Wrote {len(results)} rows to {out_csv}")
    return results

if __name__ == "__main__":
    scrape()