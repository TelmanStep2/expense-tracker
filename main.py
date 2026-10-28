from datetime import date

from database import (
    init_db,
    add_expense_db,
    get_all_expenses,
    delete_expense_db,
    update_expense_db,
)


def add_expense():
    try:
        amount = float(input("Сумма: ").replace(",", "."))
    except ValueError:
        print("Нужно ввести число.")
        return

    category = input("Категория (еда, транспорт...): ").strip().lower() or "другое"
    description = input("Описание: ").strip()

    add_expense_db(amount, category, description, date.today().isoformat())
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


def delete_expense():
    expenses = get_all_expenses()
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

    expense = expenses[number - 1]
    delete_expense_db(expense["id"])
    print(f"Удалено: {expense['description']}")


def edit_expense():
    expenses = get_all_expenses()
    if not expenses:
        print("Пока нет расходов.")
        return

    show_expenses(expenses)

    try:
        number = int(input("Номер расхода для редактирования: "))
    except ValueError:
        print("Нужно ввести число.")
        return

    if number < 1 or number > len(expenses):
        print("Такого номера нет.")
        return

    expense = expenses[number - 1]

    new_amount = input(f"Сумма [{expense['amount']}]: ").strip()
    new_category = input(f"Категория [{expense['category']}]: ").strip().lower()
    new_description = input(f"Описание [{expense['description']}]: ").strip()

    amount = expense["amount"]
    if new_amount:
        try:
            amount = float(new_amount.replace(",", "."))
        except ValueError:
            print("Нужно ввести число.")
            return

    category = new_category or expense["category"]
    description = new_description or expense["description"]

    update_expense_db(expense["id"], amount, category, description)
    print("Расход обновлён!")


def main():
    init_db()
    while True:
        print("\n--- Трекер расходов ---")
        print("1. Добавить расход")
        print("2. Показать все расходы")
        print("3. Сумма по категориям")
        print("4. Удалить расход")
        print("5. Редактировать расход")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            show_expenses(get_all_expenses())
        elif choice == "3":
            show_by_category(get_all_expenses())
        elif choice == "4":
            delete_expense()
        elif choice == "5":
            edit_expense()
        elif choice == "0":
            print("До встречи!")
            break
        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()