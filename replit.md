# Overview

This is a tennis court booking calendar monitoring system that automatically tracks availability on yclients.com and sends Telegram notifications when new dates become available. The application runs continuously, checking for updates every 6 hours, storing historical data in PostgreSQL, and notifying users via Telegram bot when new booking slots appear.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Application Structure

**Scheduler-Based Architecture**: The system uses APScheduler with a blocking scheduler to run periodic checks every 6 hours. The main loop orchestrates the scraping, comparison, storage, and notification workflows.

**Modular Component Design**: The application is split into distinct modules:
- `main.py` - Entry point and orchestration layer with scheduling logic
- `scraper.py` - Web scraping logic using Selenium
- `database.py` - PostgreSQL data persistence layer
- `telegram_notifier.py` - Telegram Bot API integration for notifications

**Web Scraping Approach**: Uses Selenium with headless Chrome to handle JavaScript-rendered content (Angular SPA). The scraper waits 25 seconds for full page load before extracting date information, as the yclients.com site requires full JavaScript execution to display booking calendar data.

**Rationale**: The scheduled checking approach balances freshness of data with resource constraints. Selenium was chosen over simple HTTP requests because the target site is an Angular single-page application that requires full JavaScript execution. Alternative approaches like Playwright were considered but Selenium provides better Replit compatibility.

**Data Flow**: 
1. Scraper fetches current available dates
2. Database retrieves last known state
3. System compares current vs. previous state
4. New dates trigger Telegram notifications
5. Current state saved to database as new snapshot

## Data Persistence

**PostgreSQL with psycopg2**: Uses direct SQL queries via psycopg2 driver rather than an ORM. The database stores snapshots with timestamp, available dates (JSON), and date count.

**Schema Design**: Single table `booking_snapshots` with columns:
- `id` (SERIAL PRIMARY KEY)
- `check_date` (TIMESTAMP) - when the check occurred
- `available_dates` (TEXT) - JSON-serialized list of dates
- `dates_count` (INTEGER) - cached count for quick queries

**Rationale**: Simple snapshot-based approach allows historical tracking and easy comparison. JSON storage in TEXT column provides flexibility without complex schema changes. Direct SQL was chosen over ORM for simplicity given the minimal data model.

**Pros**: Easy to implement, straightforward comparison logic, historical audit trail
**Cons**: Growing table size over time (could implement cleanup), JSON querying limitations

## Notification System

**Telegram Bot API**: Uses python-telegram-bot library with async/await pattern. Notifications sent via bot to configured chat ID when new dates detected.

**Message Formatting**: HTML formatting used for rich messages with emojis, bullet lists, and clickable links to booking site.

**Rationale**: Telegram provides reliable push notifications with no infrastructure overhead. Async implementation chosen to prevent blocking the main scheduler thread.

**Error Handling**: Graceful degradation - notification failures logged but don't crash the monitoring loop.

## Web Scraping Strategy

**Selenium with Chrome**: Full browser automation using headless Chrome with various anti-detection measures:
- Custom user agent strings
- Disabled automation flags
- CDP commands to mask webdriver
- Realistic window sizing (1920x1080)

**Wait Strategy**: Fixed 25-second wait after page load to ensure Angular app fully renders. This is a compromise between reliability and speed.

**Alternatives Considered**: 
- BeautifulSoup with requests: Rejected because site requires JavaScript
- Faster wait strategies: Dynamic waits attempted but Angular rendering proved unreliable
- API reverse engineering: Not pursued due to potential authentication complexity

**Pros**: Works with complex SPAs, robust against site updates
**Cons**: Resource intensive, slower than API calls, fragile to major site redesigns

## Configuration Management

**Environment Variables**: All sensitive configuration stored in Replit Secrets:
- `TELEGRAM_BOT_TOKEN` - Bot authentication
- `TELEGRAM_CHAT_ID` - Notification target
- `DATABASE_URL` - PostgreSQL connection (auto-provided by Replit)

**URL Configuration**: Booking URL configurable via constructor parameter or defaults to hardcoded value. Users must provide full URL with query parameters for proper Angular routing.

**Rationale**: Secrets keep credentials secure, environment variables allow easy deployment across environments without code changes.

# External Dependencies

## Third-Party Services

**yclients.com**: Target website for scraping tennis court booking calendar. Angular-based SPA requiring JavaScript execution. No official API available.

**Telegram Bot API**: Message delivery platform. Requires bot token (obtained from @BotFather) and chat ID for notifications.

## Database

**PostgreSQL**: Relational database for storing booking snapshots. Connection managed via `DATABASE_URL` environment variable. Uses psycopg2 driver for direct SQL access.

## Python Libraries

**Selenium WebDriver**: Browser automation for JavaScript-rendered content scraping. Requires Chrome/Chromium browser in environment.

**python-telegram-bot**: Async Telegram Bot API wrapper for sending notifications.

**APScheduler**: Job scheduling library for periodic task execution (6-hour intervals).

**BeautifulSoup4**: HTML parsing (imported but usage depends on scraper implementation details).

**psycopg2**: PostgreSQL adapter for Python.

## Infrastructure Requirements

**Chrome/Chromium**: Required by Selenium for headless browser automation. Must be available in system PATH.

**ChromeDriver**: Selenium requires matching ChromeDriver version for Chrome automation.

**Replit Platform**: Designed to run on Replit with access to Replit Secrets and Postgres database add-on.