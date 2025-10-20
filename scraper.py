from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YClientsScraper:
    def __init__(self, base_url="https://n911781.yclients.com/"):
        self.base_url = base_url
        self.city_value = "2"
        self.branch_value = "1168982"
    
    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--lang=ru-RU')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(60)
        return driver
    
    def get_available_dates(self):
        driver = None
        try:
            logger.info(f"Шаг 1: Загрузка базового URL: {self.base_url}")
            driver = self.get_driver()
            driver.get(self.base_url)
            time.sleep(3)
            
            logger.info(f"Шаг 2: Выбор города (значение {self.city_value})")
            city_selected = False
            
            try:
                city_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//button[@value='{self.city_value}']"))
                )
                city_button.click()
                city_selected = True
                logger.info("Город выбран через кнопку")
            except:
                logger.info("Кнопка города не найдена, пробую ссылку...")
                try:
                    city_link = driver.find_element(By.XPATH, f"//a[contains(@href, 'city={self.city_value}')]")
                    city_link.click()
                    city_selected = True
                    logger.info("Город выбран через ссылку")
                except:
                    logger.warning("Не удалось выбрать город стандартными способами")
            
            if city_selected:
                time.sleep(3)
            
            logger.info(f"Шаг 3: Выбор филиала (значение {self.branch_value})")
            branch_selected = False
            
            try:
                branch_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(@href, '{self.branch_value}') or @value='{self.branch_value}']"))
                )
                branch_element.click()
                branch_selected = True
                logger.info("Филиал выбран")
            except:
                logger.warning("Не удалось выбрать филиал, возможно уже на странице календаря")
            
            if branch_selected:
                time.sleep(5)
            
            logger.info(f"Текущий URL: {driver.current_url}")
            
            logger.info("Шаг 4: Ожидание загрузки календаря...")
            time.sleep(10)
            
            logger.info("Шаг 5: Поиск доступных дат через span[data-locator='working_day']")
            
            working_days = driver.find_elements(By.XPATH, "//span[@data-locator='working_day']")
            logger.info(f"Найдено элементов с working_day: {len(working_days)}")
            
            non_working_days = driver.find_elements(By.XPATH, "//span[@data-locator='non_working_day']")
            logger.info(f"Найдено элементов с non_working_day: {len(non_working_days)}")
            
            available_dates = []
            
            for day_element in working_days:
                try:
                    date_text = day_element.text.strip()
                    
                    if not date_text:
                        date_text = day_element.get_attribute('innerText')
                    
                    parent = day_element.find_element(By.XPATH, "./..")
                    aria_label = parent.get_attribute('aria-label')
                    title = parent.get_attribute('title')
                    data_date = parent.get_attribute('data-date')
                    
                    date_info = aria_label or title or data_date or date_text
                    
                    if date_info and date_info not in available_dates:
                        available_dates.append(date_info)
                        logger.info(f"Найдена доступная дата: {date_info}")
                
                except Exception as e:
                    logger.debug(f"Ошибка при обработке элемента: {e}")
                    continue
            
            logger.info(f"Всего найдено доступных дат: {len(available_dates)}")
            
            return sorted(available_dates)
            
        except Exception as e:
            logger.error(f"Ошибка в scraper: {e}", exc_info=True)
            return []
        finally:
            if driver:
                driver.quit()
                logger.info("Браузер закрыт")
