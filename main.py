import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import YClientsScraper
from database import Database
from telegram_notifier import TelegramNotifier
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

last_check_status = {
    "status": "starting",
    "last_check": None,
    "next_check": None,
    "dates_found": 0,
    "error": None
}

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "running",
                "service": "Tennis Court Booking Monitor",
                "last_check": last_check_status
            }
            
            self.wfile.write(json.dumps(response, indent=2, default=str).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def start_health_server():
    server = HTTPServer(('0.0.0.0', 5000), HealthCheckHandler)
    logger.info("Health check server started on port 5000")
    server.serve_forever()

def check_calendar():
    global last_check_status
    logger.info("=" * 60)
    logger.info(f"Starting calendar check at {datetime.now()}")
    
    try:
        last_check_status["status"] = "checking"
        
        scraper = YClientsScraper()
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
        
        last_check_status.update({
            "status": "healthy",
            "last_check": datetime.now(),
            "dates_found": len(current_dates),
            "error": None
        })
        
    except Exception as e:
        logger.error(f"Error during calendar check: {e}", exc_info=True)
        last_check_status.update({
            "status": "error",
            "last_check": datetime.now(),
            "error": str(e)
        })
        try:
            notifier = TelegramNotifier()
            notifier.notify_error(str(e))
        except:
            pass
    
    logger.info("Calendar check completed")
    logger.info("=" * 60)

def main():
    logger.info("Tennis Court Booking Monitor started")
    
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    logger.info("Performing initial check...")
    check_calendar()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_calendar, 'interval', hours=1, id='calendar_check')
    scheduler.start()
    
    logger.info("Scheduler started - will check every 1 hour")
    logger.info("Next check scheduled for 1 hour from now")
    
    try:
        while True:
            import time
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
