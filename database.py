import sqlite3
from pathlib import Path

DB_FILE = Path("expenses.db")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Создаёт таблицу, если её ещё нет."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
        """)


def add_expense_db(amount, category, description, date):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO expenses (amount, category, description, date)
            VALUES (?, ?, ?, ?)
            """,
            (amount, category, description, date),
        )


def get_all_expenses():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM expenses ORDER BY id")
        rows = cursor.fetchall()
        # Превращаем каждую строку SQLite в обычный словарь Python
        return [dict(row) for row in rows]


def delete_expense_db(expense_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))


def update_expense_db(expense_id, amount, category, description):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE expenses
            SET amount = ?, category = ?, description = ?
            WHERE id = ?
            """,
            (amount, category, description, expense_id),
        )


if __name__ == "__main__":
    init_db()
    print(get_all_expenses())