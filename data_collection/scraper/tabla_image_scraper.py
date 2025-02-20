import os
import time
import requests
import csv
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

SAVE_DIR = "data_collection/scraper/images"
METADATA_FILE = "data_collection/scraper/image_metadata.csv"
SEARCH_TERMS = [
    "Dayan drum", "Bayan drum", "tabla drums", 
    "tabla hands playing up close", "tabla performance Indian concert",
    "tabla player on stage", "tabla close-up", "tabla practice session",
    "bayan drum left hand technique", "dayan drum right hand technique",
    "tabla tuning process", "tabla top-down view", "tabla player close-up face"
]

def log(message):
    print(f"[LOG] {message}")

def create_subfolders(terms):
    for term in terms:
        folder = os.path.join(SAVE_DIR, term.replace(" ", "_").lower())
        os.makedirs(folder, exist_ok=True)

def scroll_page(page):
    """Scrolls down the page multiple times to load more images."""
    for _ in range(10):  # Adjust number of scrolls as needed
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(2)  # Allow images to load

def scrape_images_playwright(search_term, target_count=1000):
    image_urls = []
    with sync_playwright() as p:
        log(f"Launching Playwright for {search_term}...")
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        search_url = f"https://www.bing.com/images/search?q={search_term}"
        log(f"Navigating to: {search_url}")
        page.goto(search_url, timeout=60000)
        
        scroll_page(page)  # Scroll down to load more images

        page.wait_for_selector("img.mimg", timeout=10000)
        thumbnails = page.query_selector_all("img.mimg")
        log(f"Found {len(thumbnails)} images for {search_term}")

        collected = 0
        for thumb in thumbnails[:target_count]:
            try:
                thumb.scroll_into_view_if_needed()
                time.sleep(1)
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

def download_image(data):
    url, term = data
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
        else:
            log(f"❌ Failed to download {url}: HTTP {response.status_code}")
    except Exception as e:
        log(f"❌ Failed to download {url}: {e}")

def download_images_multithreaded(image_urls):
    with open(METADATA_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Image Path", "Source URL", "Search Term"])
    
    log("🚀 Starting multi-threaded downloads...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download_image, image_urls)

if __name__ == "__main__":
    create_subfolders(SEARCH_TERMS)
    all_image_urls = []
    
    for term in SEARCH_TERMS:
        image_urls = scrape_images_playwright(term, target_count=1000)
        all_image_urls.extend(image_urls)
    
    download_images_multithreaded(all_image_urls)
    log("✅ Scraping complete.")

