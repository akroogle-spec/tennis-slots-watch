from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)

url = "https://n911781.yclients.com/company/1168982/personal/select-time?o="
print(f"Loading: {url}")
driver.get(url)

print("Waiting 20 seconds for full page load...")
time.sleep(20)

print("\n=== Saving full HTML ===")
with open('page_dump.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)
print("HTML saved to page_dump.html")

print("\n=== Taking screenshot ===")
driver.save_screenshot('page_screenshot.png')
print("Screenshot saved to page_screenshot.png")

print("\n=== Checking for iframes ===")
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print(f"Found {len(iframes)} iframes")

print("\n=== All text content on page ===")
body = driver.find_element(By.TAG_NAME, "body")
print(body.text[:1000])

driver.quit()
print("\nAnalysis complete!")
