import requests
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YClientsScraper:
    def __init__(self, location_id=1168982):
        self.location_id = location_id
        self.api_url = "https://platform.yclients.com/api/v1/b2c/booking/availability/search-timeslots"
        
        # Заголовки из Developer Tools
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU",
            "authorization": "Bearer gtcwf654agufy25gsadh",
            "content-type": "application/json",
            "origin": "https://n911781.yclients.com",
            "referer": "https://n911781.yclients.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "x-yclients-application-name": "client.booking",
            "x-yclients-application-platform": "angular-18.2.13",
            "x-yclients-application-version": "293699.50aeb64b"
        }
    
    def get_available_dates_for_day(self, date_str):
        """Получает доступные слоты для конкретной даты через API"""
        payload = {
            "context": {
                "location_id": self.location_id
            },
            "filter": {
                "date": date_str,
                "records": [{"attendance_service_items": []}]
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # API возвращает: {"data": [{"attributes": {"datetime": "...", "is_bookable": true}}]}
                if "data" in data and isinstance(data["data"], list):
                    bookable_slots = [
                        slot for slot in data["data"]
                        if slot.get("attributes", {}).get("is_bookable", False)
                    ]
                    return len(bookable_slots) > 0
                
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при запросе API для даты {date_str}: {e}")
            return False
    
    def get_available_dates(self, days_ahead=30):
        """
        Получает список доступных дат для бронирования.
        Проверяет ближайшие days_ahead дней.
        
        Args:
            days_ahead: Сколько дней вперед проверять (по умолчанию 30)
        
        Returns:
            List[str]: Отсортированный список доступных дат в формате "YYYY-MM-DD"
        """
        logger.info(f"Начало проверки доступных дат (следующие {days_ahead} дней)")
        
        available_dates = []
        today = datetime.now()
        
        for day_offset in range(days_ahead):
            check_date = today + timedelta(days=day_offset)
            date_str = check_date.strftime("%Y-%m-%d")
            
            if self.get_available_dates_for_day(date_str):
                available_dates.append(date_str)
                logger.info(f"  ✅ {date_str} - доступна для бронирования")
            else:
                logger.debug(f"  ❌ {date_str} - нет доступных слотов")
        
        logger.info(f"Всего найдено доступных дат: {len(available_dates)}")
        
        return sorted(available_dates)
