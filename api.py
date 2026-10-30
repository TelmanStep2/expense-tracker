import os
import secrets
from datetime import date as date_cls
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import database

app = FastAPI()

database.init_db()

security = HTTPBasic(auto_error=False)


def require_auth(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    """Если заданы APP_USER и APP_PASSWORD, требуем логин и пароль."""
    username = os.getenv("APP_USER")
    password = os.getenv("APP_PASSWORD")
    if not username or not password:
        return  
    is_valid = (
        credentials is not None
        and secrets.compare_digest(credentials.username.encode(), username.encode())
        and secrets.compare_digest(credentials.password.encode(), password.encode())
    )
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )


protected = [Depends(require_auth)]


class ExpenseSchema(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    description: Optional[str] = None
    date: Optional[str] = None


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/app", include_in_schema=False, dependencies=protected)
def frontend():
    return FileResponse(Path(__file__).parent / "index.html")


@app.get("/expenses", dependencies=protected)
def get_expenses():
    return database.get_all_expenses()


@app.post("/expenses", status_code=201, dependencies=protected)
def add_expense(expense: ExpenseSchema):
    new_id = database.add_expense_db(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date or date_cls.today().isoformat(),
    )
    return {"id": new_id, "message": "Расход успешно добавлен"}


@app.put("/expenses/{expense_id}", dependencies=protected)
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


@app.delete("/expenses/{expense_id}", dependencies=protected)
def delete_expense(expense_id: int):
    success = database.delete_expense_db(expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Расход с таким ID не найден")
    return {"message": f"Расход {expense_id} удален"}