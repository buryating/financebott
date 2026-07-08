# finance-bot

Telegram-бот для учёта личных финансов (на двоих, у каждого свой Google Sheet) + приём записей через шорткат iPhone.

## Стек

- Python 3.11, aiogram 3.x (long polling)
- Google Sheets как хранилище (gspread + service account)
- Gemini API (бесплатный тир) — fallback-парсинг свободного текста, только когда не сработал regex+словарь
- aiohttp.web — эндпоинт `/add` для iPhone Shortcuts, крутится в том же процессе, что и бот
- Docker / docker-compose на сервере

## Структура

```
main.py            — точка входа: поднимает aiohttp-сервер и aiogram polling в одном event loop
config.py          — .env, USERS (chat_id/spreadsheet_id/shortcut_token на каждого)
categories.py       — предопределённые категории расходов/доходов + словарь синонимов
parser.py           — строгий парсинг: "500 еда" / "+50000 зарплата" через regex + словарь
gemini_parser.py    — fallback через Gemini (structured output, response_schema), если словарь не распознал категорию
processing.py       — process_entry(): общий пайплайн (parser → gemini → запись в Sheets), используется и ботом, и сервером шортката
sheets.py           — обёртка над gspread: append_row, get_all_rows, ленивая аутентификация клиента
report.py           — build_report(): агрегация по категориям за месяц/неделю, считается в Python, не в самой таблице
handlers.py         — aiogram роутер: /start, /report месяц|неделя, обработка любого текстового сообщения
server.py           — aiohttp роут POST /add?token=... для шортката
```

## Формат сообщений

- Расход: `500 еда` → -500₽, категория "еда"
- Доход: `+50000 зарплата` → +50000₽
- Всё что не распозналось строгим парсером (нет числа в начале ИЛИ категория не нашлась в словаре синонимов) — улетает в Gemini с structured output

## Google Sheet (свой на каждого пользователя)

Лист "Операции", создаётся автоматически при первой записи если не существует.
Колонки: `Дата | Тип | Сумма | Категория | Описание | Источник`

## Переменные окружения (.env)

```env
BOT_TOKEN=...
WEBHOOK_PORT=8080

DIMAN_GOOGLE_CREDENTIALS_PATH=./credentials_diman.json
PARTNER_GOOGLE_CREDENTIALS_PATH=./credentials_partner.json

GEMINI_API_KEY=...
GEMINI_MODEL=gemini-flash-latest             # ОБЯЗАТЕЛЬНО проверить актуальное имя в aistudio.google.com

DIMAN_CHAT_ID=...
DIMAN_SPREADSHEET_ID=...
DIMAN_SHORTCUT_TOKEN=...

PARTNER_CHAT_ID=...
PARTNER_SPREADSHEET_ID=...
PARTNER_SHORTCUT_TOKEN=...
```

Два разных service account (не один общий) — изоляция: каждая таблица расшарена только на свой сервис-аккаунт.

## Настройка Google Sheets (руками, один раз)

1. Google Cloud Console → новый проект → включить Google Sheets API
2. Создать Service Account (можно 2, по одному на пользователя) → сгенерировать JSON-ключ → положить как `credentials_diman.json` / `credentials_partner.json` в корень проекта (в .gitignore)
3. Создать 2 Google Sheets (по одному на пользователя), расшарить каждый на email соответствующего сервис-аккаунта (вида `xxx@xxx.iam.gserviceaccount.com`) с правами редактора
4. ID таблицы — из URL: `docs.google.com/spreadsheets/d/<ЭТОТ_ID>/edit`

## Как узнать свой chat_id

Отправить боту `/start` без регистрации в `.env` — он ответит текущим `chat_id`. Вписать это значение в `DIMAN_CHAT_ID` / `PARTNER_CHAT_ID` и перезапустить бота.

## iPhone Shortcut (собирать руками в приложении Shortcuts, не импортировать готовый файл — иначе будет диалог "Untrusted Shortcut")

1. Действие "Ask for Input" или "Dictate Text" — получить текст трат
2. "Get Contents of URL": `POST https://<host>/add?token=<DIMAN_SHORTCUT_TOKEN или PARTNER_SHORTCUT_TOKEN>`, тело JSON `{"text": "<текст из шага 1>"}`
3. "Show Notification" с полем `message` из ответа

## Известные архитектурные решения

### Почему нет БД, только Google Sheets
Источник правды — сама таблица, чтобы можно было смотреть/редактировать руками. `/report` не использует формулы в самой таблице — считает агрегацию в Python при каждом запросе, чтобы не городить листы с формулами.

### Почему Gemini, а не Claude
Личный проект с минимальной нагрузкой (пара сообщений в день на двоих), Gemini даёт постоянный бесплатный тир без карты. В бесплатном тире Google может использовать запросы для улучшения продукта (с обезличиванием) — осознанное решение пользователя, так как fallback дёргается редко (в основном ловит regex+словарь).

### Почему один процесс на бота и HTTP-сервер шортката
aiogram polling и aiohttp.web подняты в одном asyncio event loop (`main.py`) — не нужен отдельный контейнер/процесс ради одного эндпоинта.

## Деплой

Планируется тот же VPS, что у `student-bot`, через Docker. Для публичного HTTPS-доступа к `/add` (нужно шорткату) — Cloudflare Tunnel, чтобы не возиться с доменом/сертификатами. Детали — на этапе деплоя.
