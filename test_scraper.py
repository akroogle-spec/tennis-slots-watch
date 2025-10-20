import requests
from bs4 import BeautifulSoup

url = "https://n911781.yclients.com/company/1168982/personal/select-time?o="
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Fetching {url}...")
response = requests.get(url, headers=headers, timeout=30)
print(f"Status code: {response.status_code}")
print(f"Content length: {len(response.content)}")

soup = BeautifulSoup(response.content, 'html.parser')

print("\n=== Looking for various date selectors ===")

selectors = [
    ('div.sc-date-calendar-day', 'Date calendar day'),
    ('button[data-date]', 'Button with data-date'),
    ('[data-date]', 'Any element with data-date'),
    ('div.day', 'Div with class day'),
    ('td.day', 'Table cell with class day'),
    ('div.calendar-day', 'Calendar day div'),
    ('button.day', 'Button with class day'),
]

for selector, description in selectors:
    elements = soup.select(selector)
    print(f"{description} ({selector}): {len(elements)} found")
    if elements and len(elements) <= 5:
        for el in elements[:5]:
            print(f"  - {el}")

print("\n=== Full HTML structure (first 2000 chars) ===")
print(soup.prettify()[:2000])

print("\n=== All script tags ===")
scripts = soup.find_all('script')
print(f"Found {len(scripts)} script tags")
for i, script in enumerate(scripts[:3]):
    if script.string:
        print(f"\nScript {i+1} (first 200 chars):")
        print(script.string[:200])
