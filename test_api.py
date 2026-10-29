import pytest
from fastapi.testclient import TestClient

import database
from api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "test.db")
    database.init_db()
    return TestClient(app)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_expenses_empty(client):
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_add_and_get_expense(client):
    response = client.post(
        "/expenses",
        json={"amount": 50, "category": "food", "description": "обед", "date": "2026-10-28"},
    )
    assert response.status_code == 201
    new_id = response.json()["id"]
    assert new_id is not None

    expenses = client.get("/expenses").json()
    assert len(expenses) == 1
    assert expenses[0]["id"] == new_id
    assert expenses[0]["amount"] == 50
    assert expenses[0]["category"] == "food"
    assert expenses[0]["date"] == "2026-10-28"


def test_add_expense_without_date_uses_today(client):
    response = client.post("/expenses", json={"amount": 70, "category": "transport"})
    assert response.status_code == 201

    expense = client.get("/expenses").json()[0]
    assert expense["date"]  


def test_add_expense_invalid_data(client):
    response = client.post("/expenses", json={"amount": 10})
    assert response.status_code == 422


def test_add_expense_negative_amount(client):
    response = client.post("/expenses", json={"amount": -100, "category": "food"})
    assert response.status_code == 422


def test_add_expense_zero_amount(client):
    response = client.post("/expenses", json={"amount": 0, "category": "food"})
    assert response.status_code == 422


def test_add_expense_empty_category(client):
    response = client.post("/expenses", json={"amount": 10, "category": ""})
    assert response.status_code == 422


def test_update_expense(client):
    new_id = client.post(
        "/expenses", json={"amount": 50, "category": "food"}
    ).json()["id"]

    response = client.put(
        f"/expenses/{new_id}",
        json={"amount": 99, "category": "cafe", "description": "ужин"},
    )
    assert response.status_code == 200

    expense = client.get("/expenses").json()[0]
    assert expense["amount"] == 99
    assert expense["category"] == "cafe"
    assert expense["description"] == "ужин"


def test_update_missing_expense(client):
    response = client.put("/expenses/9999", json={"amount": 1, "category": "x"})
    assert response.status_code == 404


def test_delete_expense(client):
    new_id = client.post(
        "/expenses", json={"amount": 50, "category": "food"}
    ).json()["id"]

    assert client.delete(f"/expenses/{new_id}").status_code == 200
    assert client.get("/expenses").json() == []
    assert client.delete(f"/expenses/{new_id}").status_code == 404


def test_delete_missing_expense(client):
    response = client.delete("/expenses/9999")
    assert response.status_code == 404