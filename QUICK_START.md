# Быстрый старт на локальной машине

## 📦 Скачивание проекта

**В Replit:**
1. Нажмите `⋮` (три точки) рядом с названием проекта
2. Выберите **"Download as zip"**
3. Распакуйте на вашем компьютере

## 🚀 Быстрая установка (5 минут)

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Настройте PostgreSQL (если еще не установлен)
# Ubuntu/Debian:
sudo apt install postgresql postgresql-contrib

# macOS:
brew install postgresql@16

# 3. Создайте базу данных
sudo -u postgres psql
CREATE DATABASE tennis_monitor;
\q

# 4. Создайте таблицу
psql -U postgres -d tennis_monitor
CREATE TABLE booking_snapshots (
    id SERIAL PRIMARY KEY,
    check_date TIMESTAMP NOT NULL,
    available_dates TEXT NOT NULL,
    dates_count INTEGER NOT NULL
);
\q

# 5. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env - укажите пароль БД и Telegram токены

# 6. Запустите приложение
python main.py
```

## 📋 Список файлов

```
tennis-monitor/
├── main.py                  # Точка входа, scheduler, health check
├── scraper.py              # API интеграция с yclients.com
├── database.py             # Работа с PostgreSQL
├── telegram_notifier.py    # Telegram уведомления
├── requirements.txt        # Python зависимости
├── .env.example           # Пример переменных окружения
├── LOCAL_SETUP.md         # Подробная инструкция по установке
└── README.md              # Описание проекта
```

## 🔑 Необходимые переменные окружения

```bash
DATABASE_URL=postgresql://postgres:пароль@localhost:5432/tennis_monitor
TELEGRAM_BOT_TOKEN=токен_от_BotFather
TELEGRAM_CHAT_ID=ваш_chat_id
```

**Где взять токены:**
- **Bot Token**: @BotFather в Telegram → `/newbot`
- **Chat ID**: Отправьте боту сообщение, затем откройте `https://api.telegram.org/bot<токен>/getUpdates`

## ✅ Проверка работы

После запуска:
1. Откройте http://localhost:5000/health
2. Должен вернуться JSON со статусом "running"
3. В Telegram придет уведомление о запуске
4. Проверки будут выполняться каждые 6 часов

## 📖 Подробные инструкции

См. файл [LOCAL_SETUP.md](LOCAL_SETUP.md) для:
- Автозапуска при старте системы
- Мониторинга логов
- Устранения неполадок
- Настройки разных ОС
