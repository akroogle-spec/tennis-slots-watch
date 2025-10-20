import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from scraper import YClientsScraper
from database import Database
from telegram_notifier import TelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_calendar():
    logger.info("=" * 60)
    logger.info(f"Starting calendar check at {datetime.now()}")
    
    try:
        scraper = YClientsScraper(https://n911781.yclients.com/company/1168982/personal/select-time?o=d252110)
        db = Database()
        notifier = TelegramNotifier()
        
        current_dates = scraper.get_available_dates()
        logger.info(f"Current available dates: {current_dates}")
        
        last_dates, last_check_time = db.get_last_snapshot()
        
        if last_dates is not None:
            logger.info(f"Last check was at {last_check_time}")
            logger.info(f"Last available dates: {last_dates}")
            
            current_set = set(current_dates)
            last_set = set(last_dates)
            
            new_dates = current_set - last_set
            
            if new_dates:
                logger.info(f"Found {len(new_dates)} new dates: {new_dates}")
                notifier.notify_new_dates(sorted(list(new_dates)))
            else:
                logger.info("No new dates found")
        else:
            logger.info("First check - no previous data to compare")
            if current_dates:
                notifier.send_message(f"✅ Мониторинг календаря запущен!\n\nНайдено {len(current_dates)} доступных дат для бронирования.")
        
        db.save_snapshot(current_dates)
        logger.info(f"Snapshot saved with {len(current_dates)} dates")
        
    except Exception as e:
        logger.error(f"Error during calendar check: {e}", exc_info=True)
        try:
            notifier = TelegramNotifier()
            notifier.notify_error(str(e))
        except:
            pass
    
    logger.info("Calendar check completed")
    logger.info("=" * 60)

def main():
    logger.info("Tennis Court Booking Monitor started")
    logger.info("Performing initial check...")
    
    check_calendar()
    
    scheduler = BlockingScheduler()
    scheduler.add_job(check_calendar, 'interval', hours=6, id='calendar_check')
    
    logger.info("Scheduler started - will check every 6 hours")
    logger.info("Next check scheduled for 6 hours from now")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    main()
