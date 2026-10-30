from pathlib import Path
import sqlite3

DB_FILE = Path("expenses.db")


def get_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  """Создаёт таблицу и добавляет колонку user_id в старую базу, если её нет."""
  with get_connection() as conn:
    conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                user_id TEXT NOT NULL DEFAULT 'web'
            )
        """)
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(expenses)")]
    if "user_id" not in columns:
      conn.execute(
          "ALTER TABLE expenses ADD COLUMN user_id TEXT NOT NULL DEFAULT 'web'"
      )


def add_expense_db(amount, category, description, date, user_id="web"):
  with get_connection() as conn:
    cursor = conn.execute(
        """
            INSERT INTO expenses (amount, category, description, date, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
        (amount, category, description, date, user_id),
    )
    return cursor.lastrowid


def get_all_expenses(user_id=None):
  """Возвращает список расходов.

  Для каждого пользователя добавляется локальный порядковый номер row_num
  (начиная с 1).
  """
  with get_connection() as conn:
    if user_id is None:
      cursor = conn.execute("""
                SELECT *, 
                ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY id) as row_num 
                FROM expenses 
                ORDER BY user_id, id
            """)
    else:
      cursor = conn.execute(
          """
                SELECT * FROM (
                    SELECT *, 
                    ROW_NUMBER() OVER (ORDER BY id) as row_num 
                    FROM expenses 
                    WHERE user_id = ?
                ) ORDER BY id
            """,
          (user_id,),
      )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def delete_expense_db(expense_id, user_id=None):
  """Удаляет запись.

  Если передан user_id, сначала проверяет принадлежность по порядковому номеру
  (row_num), чтобы пользователь мог удалять по своим привычным номерам (1, 2, 3).
  """
  with get_connection() as conn:
    if user_id is not None:
      # Получаем список расходов пользователя в том же порядке, в каком они выводятся
      user_expenses = get_all_expenses(user_id)
      target = None
      for exp in user_expenses:
        if exp["row_num"] == int(expense_id):
          target = exp
          break

      if not target:
        return False

      cursor = conn.execute(
          "DELETE FROM expenses WHERE id = ? AND user_id = ?",
          (target["id"], user_id),
      )
      return cursor.rowcount > 0
    else:
      cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
      return cursor.rowcount > 0


def update_expense_db(expense_id, amount, category, description, user_id=None):
  with get_connection() as conn:
    if user_id is not None:
      user_expenses = get_all_expenses(user_id)
      target = None
      for exp in user_expenses:
        if exp["row_num"] == int(expense_id):
          target = exp
          break
      if not target:
        return False
      real_id = target["id"]
    else:
      real_id = expense_id

    query = """
            UPDATE expenses
            SET amount = ?, category = ?, description = ?
            WHERE id = ?
        """
    params = [amount, category, description, real_id]
    if user_id is not None:
      query += " AND user_id = ?"
      params.append(user_id)

    cursor = conn.execute(query, params)
    return cursor.rowcount > 0


if __name__ == "__main__":
  init_db()
  print(get_all_expenses())