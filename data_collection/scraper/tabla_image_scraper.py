import os
import time
import requests
import hashlib
import csv
import random
import traceback
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

SAVE_DIR = "data_collection/scraper/images"
os.makedirs(SAVE_DIR, exist_ok=True)
METADATA_FILE = "data_collection/scraper/image_metadata.csv"

SEARCH_TERMS = ["Dayan drum", "Bayan drum", "tabla drums", "tabla drums hands playing", "indian hand drums"]

options = Options()
options.headless = True
options.add_argument("--disable-cache")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

def log(message):
    print(f"[LOG] {message}")

def fetch_image_urls(search_terms, target_count=20):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    image_urls = set()

    for term in search_terms:
        log(f"Searching images for: {term}")
        driver.get(f"https://www.google.com/search?hl=en&q={term}&tbm=isch")
        time.sleep(random.uniform(2, 4))

        collected = 0
        while collected < target_count:
            images = driver.find_elements(By.CSS_SELECTOR, "img")
            for img in images:
                if collected >= target_count:
                    break
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", img)
                    time.sleep(random.uniform(0.5, 1.5))
                    src = img.get_attribute('src')
                    if src and src.startswith('http'):
                        image_urls.add((src, term))
                        log(f"Collected image URL: {src}")
                        collected += 1
                except StaleElementReferenceException:
                    log("[WARNING] Stale element encountered, retrying with delay...")
                    time.sleep(2)
                    continue
                except Exception as e:
                    log(f"Error fetching image: {traceback.format_exc()}")

            driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(random.uniform(2, 4))

    driver.quit()
    log(f"Total image URLs collected: {len(image_urls)}")
    return list(image_urls)

def download_image(data):
    url, term = data
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            image_path = os.path.join(SAVE_DIR, f"tabla_{hash(url)}.jpg")
            with open(image_path, 'wb') as f:
                f.write(response.content)

            with open(METADATA_FILE, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([image_path, url, term, response.headers.get('Content-Length', 'Unknown')])
            log(f"Downloaded: {image_path}")
        else:
            log(f"Failed to download {url}: HTTP {response.status_code}")
    except Exception as e:
        log(f"Failed to download {url}: {e}")

def download_images_multithreaded(image_urls):
    with open(METADATA_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Image Path", "Source URL", "Search Term", "Size (Bytes)"])

    log("Starting multi-threaded downloads...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download_image, image_urls)

if __name__ == "__main__":
    image_urls = fetch_image_urls(SEARCH_TERMS, target_count=5)
    download_images_multithreaded(image_urls)
    log("Scraping complete.")
