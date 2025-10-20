import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YClientsScraper:
    def __init__(self):
        self.url = "https://n911781.yclients.com/company/1168982/personal/select-time?o="
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_available_dates(self):
        try:
            logger.info(f"Fetching data from {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            available_dates = []
            
            date_elements = soup.find_all('div', class_='sc-date-calendar-day')
            if not date_elements:
                date_elements = soup.find_all('button', attrs={'data-date': True})
            
            if not date_elements:
                date_elements = soup.find_all(attrs={'data-date': True})
            
            logger.info(f"Found {len(date_elements)} date elements")
            
            for element in date_elements:
                classes = element.get('class') or []
                if isinstance(classes, str):
                    classes = [classes]
                if 'disabled' not in classes and 'inactive' not in classes:
                    date_attr = element.get('data-date')
                    if date_attr:
                        available_dates.append(str(date_attr))
                    else:
                        text = element.get_text(strip=True)
                        if text and text.isdigit():
                            available_dates.append(text)
            
            if not available_dates:
                logger.warning("No dates found with standard selectors, trying alternative method")
                all_text = soup.get_text()
                logger.info(f"Page contains {len(all_text)} characters")
            
            available_dates = sorted(list(set(available_dates)))
            logger.info(f"Extracted {len(available_dates)} unique available dates")
            
            return available_dates
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
