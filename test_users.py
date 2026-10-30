import sqlite3

import pytest
from fastapi.testclient import TestClient

import database
from api import app
from bot import user_key


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "test.db")
    monkeypatch.delenv("APP_USER", raising=False)
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    database.init_db()
    return TestClient(app)


USER_1 = {"X-User-Id": "tg:1"}
USER_2 = {"X-User-Id": "tg:2"}


def test_users_see_only_their_own_expenses(client):
    client.post("/expenses", json={"amount": 10, "category": "a"}, headers=USER_1)
    client.post("/expenses", json={"amount": 20, "category": "b"}, headers=USER_2)

    first = client.get("/expenses", headers=USER_1).json()
    second = client.get("/expenses", headers=USER_2).json()

    assert [e["category"] for e in first] == ["a"]
    assert [e["category"] for e in second] == ["b"]
    # без заголовка это владелец "web": чужих записей он не видит
    assert client.get("/expenses").json() == []


def test_cannot_delete_other_users_expense(client):
    new_id = client.post(
        "/expenses", json={"amount": 10, "category": "a"}, headers=USER_1
    ).json()["id"]

    assert client.delete(f"/expenses/{new_id}", headers=USER_2).status_code == 404
    assert len(client.get("/expenses", headers=USER_1).json()) == 1
    assert client.delete(f"/expenses/{new_id}", headers=USER_1).status_code == 200


def test_cannot_update_other_users_expense(client):
    new_id = client.post(
        "/expenses", json={"amount": 10, "category": "a"}, headers=USER_1
    ).json()["id"]

    response = client.put(
        f"/expenses/{new_id}",
        json={"amount": 99, "category": "hacked"},
        headers=USER_2,
    )
    assert response.status_code == 404
    assert client.get("/expenses", headers=USER_1).json()[0]["category"] == "a"


def test_default_user_is_web(client):
    client.post("/expenses", json={"amount": 5, "category": "web-expense"})
    expenses = database.get_all_expenses(user_id="web")
    assert len(expenses) == 1
    assert expenses[0]["category"] == "web-expense"


def test_migration_adds_user_id_to_old_database(tmp_path, monkeypatch):
    db_file = tmp_path / "old.db"
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT INTO expenses (amount, category, description, date) "
        "VALUES (50, 'food', 'старая запись', '2026-10-28')"
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(database, "DB_FILE", db_file)
    database.init_db()
    database.init_db()  # повторный запуск ничего не ломает

    expenses = database.get_all_expenses(user_id="web")
    assert len(expenses) == 1
    assert expenses[0]["description"] == "старая запись"


def test_user_key_default(monkeypatch):
    monkeypatch.delenv("OWNER_USER_ID", raising=False)
    assert user_key(123) == "tg:123"


def test_user_key_owner_shares_web_data(monkeypatch):
    monkeypatch.setenv("OWNER_USER_ID", "123")
    assert user_key(123) == "web"
    assert user_key(456) == "tg:456"