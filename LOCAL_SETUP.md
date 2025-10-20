# Установка на локальной машине

## Шаг 1: Скачивание проекта

### Вариант A: Export as ZIP (самый простой)
1. В Replit нажмите на три точки `⋮` рядом с названием проекта
2. Выберите **"Download as zip"**
3. Распакуйте архив на вашей машине

### Вариант B: Git Clone
Если проект подключен к Git:
```bash
git clone https://github.com/ваш-репозиторий/tennis-monitor.git
cd tennis-monitor
```

## Шаг 2: Установка зависимостей

### Требования
- Python 3.11 или выше
- PostgreSQL 16 или выше

### Установка Python зависимостей

#### Вариант 1: uv (рекомендуется - быстрее)
```bash
# Установите uv, если еще не установлен
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установите зависимости
uv sync
```

#### Вариант 2: pip + venv
```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install apscheduler beautifulsoup4 psycopg2-binary python-telegram-bot requests
```

## Шаг 3: Настройка базы данных PostgreSQL

### Установка PostgreSQL (если еще не установлен)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Windows:**
Скачайте установщик с https://www.postgresql.org/download/windows/

### Создание базы данных

```bash
# Подключитесь к PostgreSQL
sudo -u postgres psql

# Создайте базу данных
CREATE DATABASE tennis_monitor;

# Создайте пользователя (опционально)
CREATE USER tennis_user WITH PASSWORD 'ваш_пароль';
GRANT ALL PRIVILEGES ON DATABASE tennis_monitor TO tennis_user;

# Выход
\q
```

### Создание таблицы

```bash
# Подключитесь к базе
psql -U postgres -d tennis_monitor

# Выполните SQL
CREATE TABLE booking_snapshots (
    id SERIAL PRIMARY KEY,
    check_date TIMESTAMP NOT NULL,
    available_dates TEXT NOT NULL,
    dates_count INTEGER NOT NULL
);

# Выход
\q
```

## Шаг 4: Настройка переменных окружения

Создайте файл `.env` в корневой папке проекта:

```bash
# .env
DATABASE_URL=postgresql://postgres:ваш_пароль@localhost:5432/tennis_monitor
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_CHAT_ID=ваш_chat_id

# Для PostgreSQL (если используются отдельные переменные)
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=ваш_пароль
PGDATABASE=tennis_monitor
```

### Получение Telegram токенов

**Bot Token:**
1. Напишите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

**Chat ID:**
1. Напишите вашему боту любое сообщение
2. Откройте: `https://api.telegram.org/bot<ваш_токен>/getUpdates`
3. Найдите `"chat":{"id":123456789}`
4. Скопируйте это число

## Шаг 5: Обновление кода для локального запуска

Установите python-dotenv для загрузки переменных окружения:

```bash
pip install python-dotenv
```

Добавьте в начало `database.py`, `telegram_notifier.py` и `scraper.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Шаг 6: Запуск приложения

```bash
# Если используете uv
uv run python main.py

# Если используете venv
source venv/bin/activate  # активируйте venv
python main.py
```

## Шаг 7: Проверка работы

Приложение должно:
1. Запустить health check сервер на `http://localhost:5000`
2. Выполнить первую проверку календаря
3. Отправить уведомление в Telegram
4. Запланировать следующую проверку через 6 часов

Проверьте статус:
```bash
curl http://localhost:5000/health
```

## Автоматический запуск при старте системы

### Linux (systemd)

Создайте файл `/etc/systemd/system/tennis-monitor.service`:

```ini
[Unit]
Description=Tennis Court Booking Monitor
After=network.target postgresql.service

[Service]
Type=simple
User=ваш_пользователь
WorkingDirectory=/путь/к/проекту
Environment="PATH=/путь/к/проекту/venv/bin"
ExecStart=/путь/к/проекту/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tennis-monitor
sudo systemctl start tennis-monitor
sudo systemctl status tennis-monitor
```

### macOS (launchd)

Создайте файл `~/Library/LaunchAgents/com.tennis.monitor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tennis.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/путь/к/python</string>
        <string>/путь/к/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/путь/к/проекту</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Загрузите:
```bash
launchctl load ~/Library/LaunchAgents/com.tennis.monitor.plist
```

### Windows (Task Scheduler)

1. Откройте Task Scheduler
2. Создайте новую задачу
3. Триггер: При запуске системы
4. Действие: Запуск программы
5. Программа: `C:\путь\к\python.exe`
6. Аргументы: `C:\путь\к\main.py`
7. Рабочая папка: `C:\путь\к\проекту`

## Устранение неполадок

### Ошибка подключения к PostgreSQL
```bash
# Проверьте, что PostgreSQL запущен
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Проверьте параметры подключения
psql -U postgres -d tennis_monitor
```

### Ошибка Telegram Bot
- Проверьте правильность токена
- Убедитесь, что отправили боту хотя бы одно сообщение
- Проверьте Chat ID

### API токен устарел
Если API возвращает 404 или 401:
1. Откройте https://n911781.yclients.com в браузере
2. Developer Tools → Network
3. Найдите запрос к `search-timeslots`
4. Скопируйте новый токен из `Authorization: Bearer ...`
5. Обновите в `scraper.py` строку 17

## Мониторинг логов

```bash
# Просмотр логов в реальном времени
tail -f nohup.out  # если запущено через nohup

# Через systemd
sudo journalctl -u tennis-monitor -f

# Через launchd (macOS)
tail -f /tmp/com.tennis.monitor.log
```

## Остановка приложения

```bash
# Если запущено в терминале
Ctrl+C

# Через systemd
sudo systemctl stop tennis-monitor

# Через launchd
launchctl unload ~/Library/LaunchAgents/com.tennis.monitor.plist
```
