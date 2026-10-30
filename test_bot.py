import pytest

from bot import format_expenses, format_total, parse_add_args


def test_parse_add_args_full():
    assert parse_add_args(["50", "food", "обед", "с", "друзьями"]) == (
        50.0,
        "food",
        "обед с друзьями",
    )


def test_parse_add_args_without_description():
    assert parse_add_args(["12,5", "taxi"]) == (12.5, "taxi", None)


def test_parse_add_args_too_few():
    with pytest.raises(ValueError):
        parse_add_args(["50"])


def test_parse_add_args_not_a_number():
    with pytest.raises(ValueError):
        parse_add_args(["abc", "food"])


def test_parse_add_args_non_positive():
    with pytest.raises(ValueError):
        parse_add_args(["-5", "food"])


def test_format_expenses_empty():
    assert format_expenses([]) == "Расходов пока нет."


def test_format_expenses_lines():
    expenses = [
        {"id": 1, "date": "2026-10-30", "category": "food", "amount": 50, "description": "обед"},
        {"id": 2, "date": "2026-10-30", "category": "taxi", "amount": 12.5, "description": None},
    ]
    text = format_expenses(expenses)
    assert "1. 2026-10-30 | food | 50.00 | обед" in text
    assert "2. 2026-10-30 | taxi | 12.50" in text


def test_format_expenses_limit():
    expenses = [
        {"id": i, "date": "2026-10-30", "category": "x", "amount": 1, "description": None}
        for i in range(1, 41)
    ]
    text = format_expenses(expenses, limit=30)
    assert "Показаны последние 30 из 40" in text
    assert "\n40. " in text
    assert "\n10. " not in text


def test_format_total():
    expenses = [
        {"id": 1, "category": "food", "amount": 50},
        {"id": 2, "category": "food", "amount": 25},
        {"id": 3, "category": "taxi", "amount": 12.5},
    ]
    text = format_total(expenses)
    assert "food: 75.00" in text
    assert "taxi: 12.50" in text
    assert "Итого: 87.50" in text