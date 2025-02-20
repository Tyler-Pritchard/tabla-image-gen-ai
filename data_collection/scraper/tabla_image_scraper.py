import os
import csv
import time
import requests
from playwright.sync_api import sync_playwright

SAVE_DIR = "data_collection/scraper/images"
METADATA_FILE = "data_collection/scraper/image_metadata.csv"
SEARCH_TERMS = ["Dayan drum", "Bayan drum", "tabla drums"]

def log(message):
    print(f"[LOG] {message}")

def create_subfolders(terms):
    """Create subfolders for storing downloaded images."""
    for term in terms:
        folder = os.path.join(SAVE_DIR, term.replace(" ", "_").lower())
        os.makedirs(folder, exist_ok=True)

def scrape_images_playwright(search_term, target_count=5):
    """Scrapes Bing for image URLs using Playwright."""
    image_urls = []

    with sync_playwright() as p:
        log(f"Launching Playwright for {search_term}...")
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        search_url = f"https://www.bing.com/images/search?q={search_term}"
        log(f"Navigating to: {search_url}")
        page.goto(search_url, timeout=60000)

        # Ensure images are present
        page.wait_for_selector("img.mimg", timeout=10000)
        thumbnails = page.query_selector_all("img.mimg")

        log(f"Found {len(thumbnails)} images for {search_term}")

        collected = 0
        for thumb in thumbnails[:target_count]:
            try:
                thumb.scroll_into_view_if_needed()
                time.sleep(1)

                # Extract the correct image URL
                img_url = thumb.get_attribute("src") or thumb.get_attribute("data-src")
                
                if not img_url or not img_url.startswith("http"):
                    log(f"❌ Skipped invalid image: {img_url}")
                    continue

                log(f"✅ Found image: {img_url}")

                image_urls.append((img_url, search_term))
                collected += 1
                log(f"[{collected}/{target_count}] Collected: {img_url}")

                if collected >= target_count:
                    break
            except Exception as e:
                log(f"Error collecting image: {e}")

        browser.close()
    
    log(f"✅ Collected {len(image_urls)} high-resolution images for {search_term}")
    return image_urls

def download_images(image_urls):
    """Downloads images from collected URLs."""
    with open(METADATA_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Image Path", "Source URL", "Search Term"])

    for url, term in image_urls:
        log(f"Downloading: {url}")
        folder_path = os.path.join(SAVE_DIR, term.replace(" ", "_").lower())

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image_path = os.path.join(folder_path, f"{term.replace(' ', '_')}_{abs(hash(url))}.jpg")
                with open(image_path, "wb") as f:
                    f.write(response.content)
                log(f"✅ Saved: {image_path}")

                with open(METADATA_FILE, "a", newline="") as csvfile:
                    csv.writer(csvfile).writerow([image_path, url, term])
        except Exception as e:
            log(f"❌ Failed to download {url}: {e}")

if __name__ == "__main__":
    create_subfolders(SEARCH_TERMS)
    all_image_urls = []

    for term in SEARCH_TERMS:
        image_urls = scrape_images_playwright(term, target_count=50)
        all_image_urls.extend(image_urls)

    download_images(all_image_urls)
    log("✅ Scraping complete.")
