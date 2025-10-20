from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=chrome_options)

url = "https://n911781.yclients.com/company/1168982/personal/select-time?o="
print(f"Loading {url}...")
driver.get(url)

print("Waiting 3 seconds...")
time.sleep(3)

print("\n=== Page title ===")
print(driver.title)

print("\n=== Trying to find app root ===")
try:
    app_root = driver.find_element(By.TAG_NAME, "app-root")
    print(f"Found app-root: {app_root.tag_name}")
except:
    print("No app-root found")

print("\n=== Looking for Angular components ===")
try:
    ng_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'ng-')]")
    print(f"Found {len(ng_elements)} Angular elements")
except:
    print("No Angular elements found")

print("\n=== Waiting for calendar to load (10 seconds) ===")
time.sleep(10)

print("\n=== Full page source (first 5000 chars) ===")
print(driver.page_source[:5000])

print("\n=== Looking for all clickable elements ===")
buttons = driver.find_elements(By.TAG_NAME, "button")
print(f"Found {len(buttons)} buttons")
for i, btn in enumerate(buttons[:5]):
    print(f"Button {i+1}: class='{btn.get_attribute('class')}', text='{btn.text[:50]}'")

print("\n=== Looking for divs with numbers (potential dates) ===")
all_divs = driver.find_elements(By.TAG_NAME, "div")
print(f"Total divs: {len(all_divs)}")
for div in all_divs[:20]:
    text = div.text.strip()
    if text and text.isdigit() and len(text) <= 2:
        print(f"Found potential date div: '{text}', class='{div.get_attribute('class')}'")

driver.quit()
print("\nDone!")
