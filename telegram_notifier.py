import os
from telegram import Bot
from telegram.error import TelegramError
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable not set")
        self.bot = Bot(token=self.bot_token)
    
    async def send_message_async(self, message):
        try:
            if self.chat_id:
                await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML')
                logger.info("Message sent successfully")
                return True
            return False
        except TelegramError as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_message(self, message):
        try:
            asyncio.run(self.send_message_async(message))
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
    
    def notify_new_dates(self, new_dates):
        if not new_dates:
            return
        
        message = "🎾 <b>Новые даты для бронирования!</b>\n\n"
        message += "Добавились следующие даты:\n"
        for date in sorted(new_dates):
            message += f"  • {date}\n"
        message += f"\n<a href='https://n911781.yclients.com/company/1168982/personal/select-time?o='>Забронировать корт</a>"
        
        self.send_message(message)
    
    def notify_no_changes(self):
        message = "ℹ️ Проверка календаря бронирования завершена.\n\nИзменений нет."
        self.send_message(message)
    
    def notify_error(self, error_message):
        message = f"⚠️ <b>Ошибка при проверке календаря</b>\n\n{error_message}"
        self.send_message(message)
