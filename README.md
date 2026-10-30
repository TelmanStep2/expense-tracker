[English](#expense-tracker) | [Русский](#трекер-расходов)

# Expense Tracker

A Python app for tracking personal expenses: a command-line interface, a REST API built with FastAPI and a simple web interface. Data is stored in a SQLite database, so nothing is lost when you close the program.

## Features

- Add an expense: amount, category, description, date (set automatically)
- View all expenses and the total amount
- View totals by category
- Edit and delete expenses
- REST API with interactive documentation (Swagger UI)
- Web interface: add, view and delete expenses in the browser
- Optional password protection (HTTP Basic) for the API and the web interface
- Data is stored in SQLite (`expenses.db`)
- Input validation (positive amount, non-empty category)
- Automated tests with `pytest`

## Tech stack

- Python 3.12+
- SQLite (`sqlite3` from the standard library)
- FastAPI + Uvicorn
- HTML, CSS and vanilla JavaScript for the web interface
- pytest + httpx

## Getting started

```bash
git clone https://github.com/TelmanStep2/expense-tracker.git
cd expense-tracker
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### Console app

```bash
python main.py
```

### REST API

```bash
uvicorn api:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive documentation.

| Method | Path | Description |
|---|---|---|
| GET | `/expenses` | List all expenses |
| POST | `/expenses` | Add an expense |
| PUT | `/expenses/{id}` | Update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |

Example request body for `POST /expenses` (the date is optional, today's date is used by default):

```json
{"amount": 50, "category": "food", "description": "lunch"}
```

### Web interface

With the server running, open http://127.0.0.1:8000/app to add, view and delete expenses in the browser.

![Web interface](docs/screenshot.png)

### Authentication (optional)

If the `APP_USER` and `APP_PASSWORD` environment variables are set, the API and the web interface ask for a login and password (HTTP Basic). If they are not set, authentication is disabled. The `/` health-check endpoint is always open.

```bash
set APP_USER=admin          # Windows (cmd)
set APP_PASSWORD=secret123
uvicorn api:app --reload
```

On Mac/Linux use `export APP_USER=admin` and `export APP_PASSWORD=secret123`.

### Tests

```bash
pytest -v
```

## Example (console app)

The console interface is currently in Russian:

```
--- Трекер расходов ---
1. Добавить расход
2. Показать все расходы
3. Сумма по категориям
0. Выход
Выберите действие: 1
Сумма: 15
Категория (еда, транспорт...): еда
Описание: обед
Расход добавлен!

Выберите действие: 2
1. 2026-10-27 | еда | 15.00 | обед

Итого: 15.00
```

## Roadmap

- [x] Delete and edit expenses
- [x] Switch from JSON to SQLite
- [x] Tests with `pytest`
- [x] REST API with FastAPI
- [x] Web interface
- [x] Optional authentication
- [ ] Telegram bot
- [ ] Deployment

---

# Трекер расходов

Приложение на Python для учёта личных расходов: консольный интерфейс, REST API на FastAPI и простой веб-интерфейс. Данные хранятся в базе SQLite, поэтому не пропадают после закрытия программы.

## Возможности

- Добавление расхода: сумма, категория, описание, дата (ставится автоматически)
- Просмотр всех расходов и общей суммы
- Сумма расходов по категориям
- Редактирование и удаление расходов
- REST API с интерактивной документацией (Swagger UI)
- Веб-интерфейс: добавление, просмотр и удаление расходов в браузере
- Необязательная защита паролем (HTTP Basic) для API и веб-интерфейса
- Хранение данных в SQLite (`expenses.db`)
- Проверка входных данных (положительная сумма, непустая категория)
- Автоматические тесты на `pytest`

## Технологии

- Python 3.12+
- SQLite (модуль `sqlite3` из стандартной библиотеки)
- FastAPI + Uvicorn
- HTML, CSS и JavaScript без фреймворков для веб-интерфейса
- pytest + httpx

## Как запустить

```bash
git clone https://github.com/TelmanStep2/expense-tracker.git
cd expense-tracker
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### Консольное приложение

```bash
python main.py
```

### REST API

```bash
uvicorn api:app --reload
```

После запуска откройте http://127.0.0.1:8000/docs, там интерактивная документация.

| Метод | Путь | Описание |
|---|---|---|
| GET | `/expenses` | Список всех расходов |
| POST | `/expenses` | Добавить расход |
| PUT | `/expenses/{id}` | Изменить расход |
| DELETE | `/expenses/{id}` | Удалить расход |

Пример тела запроса для `POST /expenses` (дата необязательна, по умолчанию ставится сегодняшняя):

```json
{"amount": 50, "category": "food", "description": "обед"}
```

### Веб-интерфейс

При запущенном сервере откройте http://127.0.0.1:8000/app: там можно добавлять, смотреть и удалять расходы в браузере.

![Веб-интерфейс](docs/screenshot.png)

### Авторизация (необязательно)

Если заданы переменные окружения `APP_USER` и `APP_PASSWORD`, API и веб-интерфейс запрашивают логин и пароль (HTTP Basic). Если они не заданы, защита выключена. Адрес `/` для проверки работоспособности всегда открыт.

```bash
set APP_USER=admin          # Windows (cmd)
set APP_PASSWORD=secret123
uvicorn api:app --reload
```

На Mac/Linux используйте `export APP_USER=admin` и `export APP_PASSWORD=secret123`.

### Тесты

```bash
pytest -v
```

## Пример работы (консоль)

```
--- Трекер расходов ---
1. Добавить расход
2. Показать все расходы
3. Сумма по категориям
0. Выход
Выберите действие: 1
Сумма: 15
Категория (еда, транспорт...): еда
Описание: обед
Расход добавлен!

Выберите действие: 2
1. 2026-10-27 | еда | 15.00 | обед

Итого: 15.00
```

## Планы развития

- [x] Удаление и редактирование расходов
- [x] Переход с JSON на SQLite
- [x] Тесты на `pytest`
- [x] REST API на FastAPI
- [x] Веб-интерфейс
- [x] Необязательная авторизация
- [ ] Telegram-бот
- [ ] Деплой