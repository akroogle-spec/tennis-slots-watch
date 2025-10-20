# Overview

This is a tennis court booking calendar monitoring system that automatically tracks availability on yclients.com and sends Telegram notifications when new dates become available. The application runs continuously, checking for updates every 6 hours, storing historical data in PostgreSQL, and notifying users via Telegram bot when new booking slots appear.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Application Structure

**Scheduler-Based Architecture**: The system uses APScheduler with a background scheduler to run periodic checks every 6 hours. Additionally, a health check HTTP server runs on port 5000 to monitor application status and enable deployment on Replit Reserved VM. The main loop orchestrates the scraping, comparison, storage, and notification workflows.

**Modular Component Design**: The application is split into distinct modules:
- `main.py` - Entry point, orchestration layer with scheduling logic, and health check HTTP server (port 5000)
- `scraper.py` - API integration for fetching booking availability data
- `database.py` - PostgreSQL data persistence layer
- `telegram_notifier.py` - Telegram Bot API integration for notifications

**API Integration Approach**: Uses direct HTTP requests to yclients.com internal API endpoint (`platform.yclients.com/api/v1/b2c/booking/availability/search-timeslots`). The scraper queries each day individually for the next 30 days to determine availability.

**Rationale**: Direct API access is 10x faster and more reliable than browser automation. Authentication uses Bearer token and specific application headers extracted from the Angular SPA's network traffic. This approach is lightweight, efficient, and avoids anti-bot detection issues.

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

## API Integration Strategy

**Direct API Requests**: Uses Python `requests` library to query yclients.com internal booking API. The system makes POST requests to `/api/v1/b2c/booking/availability/search-timeslots` with location context and date filter.

**Authentication**: Requires Bearer token and application-specific headers:
- `Authorization: Bearer <token>` - Authentication token
- `x-yclients-application-name: client.booking` - App identifier
- `x-yclients-application-platform: angular-18.2.13` - Platform version
- `x-yclients-application-version: 293699.50aeb64b` - App version

**Date Scanning**: Iterates through next 30 days, making individual API requests for each date. Filters results to include only dates with `is_bookable: true` slots.

**Performance**: Completes 30-day scan in ~50 seconds vs 5+ minutes with browser automation. No browser overhead, faster startup, and more reliable execution.

**Pros**: Fast, lightweight, reliable, no browser dependencies
**Cons**: Requires valid authentication token (may need periodic refresh), dependent on API stability

## Configuration Management

**Environment Variables**: All sensitive configuration stored in Replit Secrets:
- `TELEGRAM_BOT_TOKEN` - Bot authentication
- `TELEGRAM_CHAT_ID` - Notification target
- `DATABASE_URL` - PostgreSQL connection (auto-provided by Replit)

**URL Configuration**: Booking URL configurable via constructor parameter or defaults to hardcoded value. Users must provide full URL with query parameters for proper Angular routing.

**Rationale**: Secrets keep credentials secure, environment variables allow easy deployment across environments without code changes.

# External Dependencies

## Third-Party Services

**yclients.com**: Target platform for tennis court booking calendar monitoring. Uses internal API endpoint for availability queries (company/location ID: 1168982).

**Telegram Bot API**: Message delivery platform. Requires bot token (obtained from @BotFather) and chat ID for notifications.

## Database

**PostgreSQL**: Relational database for storing booking snapshots. Connection managed via `DATABASE_URL` environment variable. Uses psycopg2 driver for direct SQL access.

## Python Libraries

**requests**: HTTP client for making API calls to yclients.com booking endpoints.

**python-telegram-bot**: Async Telegram Bot API wrapper for sending notifications.

**APScheduler**: Job scheduling library for periodic task execution (6-hour intervals).

**BeautifulSoup4**: HTML parsing library (available but not actively used with API approach).

**psycopg2**: PostgreSQL adapter for Python database access.

## Infrastructure Requirements

**Replit Platform**: Designed to run on Replit with access to Replit Secrets and Postgres database add-on. No additional system dependencies required beyond Python runtime.