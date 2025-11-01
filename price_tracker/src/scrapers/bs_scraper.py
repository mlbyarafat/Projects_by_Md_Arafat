"""BeautifulSoup-based scraper template.
Fill TARGET_URL and selectors for the site you have permission to scrape.
"""
import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
from urllib.parse import urljoin

TARGET_URL = "https://example.com/products"  # <<-- change to allowed/test URL
USER_AGENT = "PriceTrackerBot/1.0 (+https://yoursite.example)"

HEADERS = {"User-Agent": USER_AGENT}

def parse_product_card(card):
    # Example selectors — change to match your target
    title_el = card.select_one(".product-title")
    price_el = card.select_one(".price")
    link_el = card.select_one("a")
    title = title_el.get_text(strip=True) if title_el else None
    price_raw = price_el.get_text(strip=True) if price_el else None
    link = urljoin(TARGET_URL, link_el['href']) if link_el and link_el.get('href') else None
    return {"title": title, "price_raw": price_raw, "link": link}

def clean_price(price_raw):
    if not price_raw: 
        return None
    # remove common currency symbols and commas
    cleaned = price_raw.replace(",", "").replace("$", "").replace("USD", "").strip()
    try:
        return float(cleaned)
    except:
        return None

def scrape(page_limit=1, delay=1.0, out_csv="data/scraped_prices.csv"):
    results = []
    for page in range(1, page_limit+1):
        url = f"{TARGET_URL}?page={page}"
        print(f"Fetching {url}")
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select(".product-card")  # change selector
        for c in cards:
            parsed = parse_product_card(c)
            parsed['price'] = clean_price(parsed.get('price_raw'))
            parsed['scrape_ts'] = datetime.utcnow().isoformat()
            results.append(parsed)
        time.sleep(delay)
    # Save CSV
    keys = ["title","price_raw","price","link","scrape_ts"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {len(results)} rows to {out_csv}")
    return results

if __name__ == "__main__":
    scrape(page_limit=1)
