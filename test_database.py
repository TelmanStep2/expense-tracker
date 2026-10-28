import pytest

import database


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Каждый тест работает с новой пустой базой во временной папке."""
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "test.db")
    database.init_db()


def test_database_starts_empty():
    assert database.get_all_expenses() == []


def test_add_expense():
    database.add_expense_db(10, "еда", "обед", "2026-10-28")
    expenses = database.get_all_expenses()

    assert len(expenses) == 1
    assert expenses[0]["amount"] == 10
    assert expenses[0]["category"] == "еда"


def test_delete_expense():
    database.add_expense_db(10, "еда", "обед", "2026-10-28")
    expense_id = database.get_all_expenses()[0]["id"]
    database.delete_expense_db(expense_id)
    assert database.get_all_expenses() == []


def test_update_expense():
    database.add_expense_db(10, "еда", "обед", "2026-10-28")
    expense_id = database.get_all_expenses()[0]["id"]
    database.update_expense_db(expense_id, 25, "развлечения", "кино")
    expenses = database.get_all_expenses()

    assert len(expenses) == 1
    assert expenses[0]["amount"] == 25
    assert expenses[0]["category"] == "развлечения"
    assert expenses[0]["description"] == "кино"


def test_delete_one_of_two_expenses():
    database.add_expense_db(10, "еда", "обед", "2026-10-28")
    database.add_expense_db(20, "транспорт", "самокат", "2026-10-28")
    first_id = database.get_all_expenses()[0]["id"]

    database.delete_expense_db(first_id)
    expenses = database.get_all_expenses()

    assert len(expenses) == 1
    assert expenses[0]["description"] == "самокат"