import json
from datetime import date
from pathlib import Path

FILE = Path("expenses.json")


def load_expenses():
    """Загружает расходы из файла. Если файла нет, возвращает пустой список."""
    if FILE.exists():
        return json.loads(FILE.read_text(encoding="utf-8"))
    return []


def save_expenses(expenses):
    """Сохраняет расходы в файл."""
    FILE.write_text(
        json.dumps(expenses, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_expense(expenses):
    try:
        amount = float(input("Сумма: ").replace(",", "."))
    except ValueError:
        print("Нужно ввести число.")
        return

    category = input("Категория (еда, транспорт...): ").strip().lower() or "другое"
    description = input("Описание: ").strip()

    expenses.append({
        "amount": amount,
        "category": category,
        "description": description,
        "date": date.today().isoformat(),
    })
    save_expenses(expenses)
    print("Расход добавлен!")


def show_expenses(expenses):
    if not expenses:
        print("Пока нет расходов.")
        return
    for i, e in enumerate(expenses, start=1):
        print(f"{i}. {e['date']} | {e['category']} | {e['amount']:.2f} | {e['description']}")
    total = sum(e["amount"] for e in expenses)
    print(f"\nИтого: {total:.2f}")


def show_by_category(expenses):
    if not expenses:
        print("Пока нет расходов.")
        return
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    for category, total in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        print(f"{category}: {total:.2f}")


def delete_expense(expenses):
    if not expenses:
        print("Пока нет расходов.")
        return

    show_expenses(expenses)

    try:
        number = int(input("Номер расхода для удаления: "))
    except ValueError:
        print("Нужно ввести число.")
        return

    if number < 1 or number > len(expenses):
        print("Такого номера нет.")
        return

    removed = expenses.pop(number - 1)
    save_expenses(expenses)
    print(f"Удалено: {removed['description']}")


def main():
    expenses = load_expenses()
    while True:
        print("\n--- Трекер расходов ---")
        print("1. Добавить расход")
        print("2. Показать все расходы")
        print("3. Сумма по категориям")
        print("4. Удалить расход")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            show_expenses(expenses)
        elif choice == "3":
            show_by_category(expenses)
        elif choice == "4":
            delete_expense(expenses)
        elif choice == "0":
            print("До встречи!")
            break
        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()