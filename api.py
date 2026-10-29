from datetime import date as date_cls
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database

app = FastAPI()

database.init_db()


class ExpenseSchema(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    date: Optional[str] = None


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/expenses")
def get_expenses():
    return database.get_all_expenses()


@app.post("/expenses", status_code=201)
def add_expense(expense: ExpenseSchema):
    new_id = database.add_expense_db(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date or date_cls.today().isoformat(),
    )
    return {"id": new_id, "message": "Расход успешно добавлен"}


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseSchema):
    success = database.update_expense_db(
        expense_id=expense_id,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Расход с таким ID не найден")
    return {"message": f"Расход {expense_id} обновлен"}


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    success = database.delete_expense_db(expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Расход с таким ID не найден")
    return {"message": f"Расход {expense_id} удален"}