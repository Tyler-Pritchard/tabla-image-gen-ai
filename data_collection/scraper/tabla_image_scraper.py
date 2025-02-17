import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

SAVE_DIR = "data_collection/scraper/images"
os.makedirs(SAVE_DIR, exist_ok=True)

SEARCH_URL = "https://www.google.com/search?hl=en&q=tabla+drum&tbm=isch"

options = Options()
options.headless = True


def fetch_image_urls(target_count=20):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(SEARCH_URL)
    time.sleep(2)

    body = driver.find_element(By.TAG_NAME, "body")
    image_urls = set()

    while len(image_urls) < target_count:
        images = driver.find_elements(By.CSS_SELECTOR, "img")
        for img in images:
            src = img.get_attribute('src')
            if src and src.startswith('http'):
                image_urls.add(src)

        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    driver.quit()
    return list(image_urls)


def download_images(image_urls):
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                with open(os.path.join(SAVE_DIR, f"tabla_{i}.jpg"), 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: tabla_{i}.jpg")
            else:
                print(f"Failed to download {url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")


if __name__ == "__main__":
    image_urls = fetch_image_urls(target_count=50)  # Change the number as needed
    download_images(image_urls)
