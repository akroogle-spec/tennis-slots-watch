from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import time
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YClientsScraper:
    def __init__(self):
        self.url = "https://n911781.yclients.com/company/1168982/personal/select-time?o="
    
    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        chrome_options.add_argument('--lang=ru-RU')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver
    
    def get_available_dates(self):
        driver = None
        try:
            logger.info(f"Opening URL: {self.url}")
            driver = self.get_driver()
            driver.get(self.url)
            
            logger.info("Waiting for page content to load (15 seconds)...")
            time.sleep(15)
            
            page_source = driver.page_source
            
            available_dates = set()
            
            all_elements = driver.find_elements(By.XPATH, "//*")
            logger.info(f"Total elements on page: {len(all_elements)}")
            
            date_pattern = re.compile(r'\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)', re.IGNORECASE)
            date_pattern_short = re.compile(r'\d{4}-\d{2}-\d{2}')
            
            for element in all_elements:
                try:
                    text = element.text
                    if text:
                        match = date_pattern.search(text)
                        if match:
                            available_dates.add(match.group(0))
                        
                        match_short = date_pattern_short.search(text)
                        if match_short:
                            available_dates.add(match_short.group(0))
                    
                    onclick = element.get_attribute('onclick')
                    if onclick and 'date' in onclick.lower():
                        available_dates.add(onclick)
                except:
                    pass
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            calendar_texts = soup.find_all(string=date_pattern)
            for text in calendar_texts:
                match = date_pattern.search(str(text))
                if match:
                    available_dates.add(match.group(0))
            
            if not available_dates:
                logger.info("Trying to find buttons or clickable date elements...")
                buttons = driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"Found {len(buttons)} buttons on page")
                
                for btn in buttons:
                    try:
                        btn_text = btn.text.strip()
                        btn_class = btn.get_attribute('class') or ''
                        
                        if btn_text and (btn_text.isdigit() and 1 <= int(btn_text) <= 31):
                            if 'disabled' not in btn_class.lower() and 'inactive' not in btn_class.lower():
                                logger.info(f"Found potential date button: {btn_text} (class: {btn_class})")
                                available_dates.add(btn_text)
                    except:
                        pass
            
            result = sorted(list(available_dates))
            logger.info(f"Extracted {len(result)} dates: {result[:10] if len(result) > 10 else result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in scraper: {e}", exc_info=True)
            return []
        finally:
            if driver:
                driver.quit()
                logger.info("Browser closed")
