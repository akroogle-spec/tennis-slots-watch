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
    def __init__(self, url="https://n911781.yclients.com/company/1168982/personal/select-time?o="):
        self.url = url
        self.base_url = "https://n911781.yclients.com"
    
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
    
    def navigate_through_selection(self, driver):
        """Проходит через выбор города и филиала"""
        try:
            # Шаг 1: Сначала перейдем на базовый URL для установки сессии
            logger.info("Шаг 1: Переход на базовый URL")
            driver.get(self.base_url)
            time.sleep(4)
            
            logger.info(f"URL после базового перехода: {driver.current_url}")
            
            # Шаг 2: Ищем и кликаем на город Москва
            if 'select-city' in driver.current_url or 'select-city' in driver.page_source.lower():
                logger.info("Шаг 2: Ищем элемент города Москва...")
                
                # Пробуем разные способы найти Москву
                city_clicked = False
                
                # Способ 1: Кнопка с value="2"
                try:
                    city_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@value='2']"))
                    )
                    driver.execute_script("arguments[0].click();", city_button)
                    logger.info("Город выбран через JavaScript клик на кнопку value='2'")
                    city_clicked = True
                except:
                    pass
                
                # Способ 2: Ссылка на /select-city/2
                if not city_clicked:
                    try:
                        city_link = driver.find_element(By.XPATH, "//a[contains(@href, '/select-city/2') or contains(@href, 'city=2')]")
                        href = city_link.get_attribute('href')
                        logger.info(f"Найдена ссылка на город: {href}")
                        driver.get(href)
                        logger.info("Переход по ссылке города")
                        city_clicked = True
                    except:
                        pass
                
                # Способ 3: Прямой переход на URL с городом
                if not city_clicked:
                    logger.info("Прямой переход на URL с выбором города")
                    driver.get(f"{self.base_url}/select-city/2/select-branch?o=")
                    city_clicked = True
                
                if city_clicked:
                    logger.info("Ожидание после выбора города (5 сек)...")
                    time.sleep(5)
                    logger.info(f"URL после выбора города: {driver.current_url}")
            
            # Шаг 3: Проверяем, есть ли страница выбора филиала
            if 'select-branch' in driver.current_url:
                logger.info("Шаг 3: Обнаружена страница выбора филиала")
                
                try:
                    # Ищем филиал 1168982
                    branch_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, '1168982')] | //button[contains(@value, '1168982')]"))
                    )
                    branch_elem.click()
                    logger.info("Филиал выбран")
                    time.sleep(5)
                except:
                    logger.info("Не найден элемент филиала, переходим напрямую")
                    driver.get(f"{self.base_url}/company/1168982/personal/select-time?o=")
                    time.sleep(5)
            else:
                # Переходим сразу на страницу календаря
                logger.info("Переход на страницу календаря")
                driver.get(self.url)
                time.sleep(8)
            
            logger.info(f"Финальный URL после навигации: {driver.current_url}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при навигации: {e}")
            return False
    
    def get_available_dates(self):
        driver = None
        try:
            driver = self.get_driver()
            
            # Проходим через навигацию
            self.navigate_through_selection(driver)
            
            logger.info("Ожидание загрузки календаря (20 секунд)...")
            time.sleep(20)
            
            logger.info("Поиск доступных дат через span[data-locator='working_day']")
            
            working_day_elements = driver.find_elements(By.XPATH, "//span[@data-locator='working_day']")
            non_working_day_elements = driver.find_elements(By.XPATH, "//span[@data-locator='non_working_day']")
            
            logger.info(f"Найдено элементов с data-locator='working_day': {len(working_day_elements)}")
            logger.info(f"Найдено элементов с data-locator='non_working_day': {len(non_working_day_elements)}")
            
            available_dates = []
            
            for element in working_day_elements:
                try:
                    date_text = element.text.strip()
                    
                    if not date_text:
                        date_text = element.get_attribute('innerText')
                    
                    parent = element.find_element(By.XPATH, "./..")
                    aria_label = parent.get_attribute('aria-label')
                    title = parent.get_attribute('title')
                    data_date = parent.get_attribute('data-date')
                    
                    date_info = aria_label or title or data_date or date_text
                    
                    if date_info and date_info.strip():
                        date_info = date_info.strip()
                        if date_info not in available_dates:
                            available_dates.append(date_info)
                            logger.info(f"  Найдена доступная дата: {date_info}")
                
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
