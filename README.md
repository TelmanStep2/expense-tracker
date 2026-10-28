[English](#expense-tracker) | [Русский](#трекер-расходов)

 Expense Tracker

A command-line Python app for tracking personal expenses. Data is saved to a JSON file, so nothing is lost when you close the program.

 Features

- Add an expense: amount, category, description, date (set automatically)
- View all expenses and the total amount
- View totals by category
- Automatic saving to `expenses.json`

 Tech stack

- Python 3.12+
- Standard library only: `json`, `datetime`, `pathlib`

 Getting started

```bash
git clone https://github.com/TelmanStep2/expense-tracker.git
cd expense-tracker
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
python main.py
```

## Example

The interface is currently in Russian:

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

 Roadmap

- [x] Delete and edit expenses
- [X] Switch from JSON to SQLite
- [X] Tests with `pytest`
- [ ] REST API with FastAPI
- [ ] Web interface or Telegram bot

---

 Трекер расходов

Консольная программа на Python для учёта личных расходов. Данные сохраняются в JSON-файл, поэтому не пропадают после закрытия программы.

 Возможности

- Добавление расхода: сумма, категория, описание, дата (ставится автоматически)
- Просмотр всех расходов и общей суммы
- Сумма расходов по категориям
- Автоматическое сохранение данных в `expenses.json`

 Технологии

- Python 3.12+
- Только стандартная библиотека: `json`, `datetime`, `pathlib`

 Как запустить

```bash
git clone https://github.com/TelmanStep2/expense-tracker.git
cd expense-tracker
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
python main.py
```

 Пример работы

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

 Планы развития

- [x] Удаление и редактирование расходов
- [X] Переход с JSON на SQLite
- [X] Тесты на `pytest`
- [ ] REST API на FastAPI
- [ ] Веб-интерфейс или Telegram-бот