import os
import secrets
from datetime import date as date_cls
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
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
        return  # защита выключена (локальная разработка, тесты)

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


def current_user(x_user_id: Optional[str] = Header(default=None)) -> str:
    """Чьи расходы показывать. Без заголовка X-User-Id это владелец 'web'."""
    value = (x_user_id or "").strip()
    if not value:
        return "web"
    if len(value) > 64:
        raise HTTPException(status_code=400, detail="Слишком длинный X-User-Id")
    return value


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
def get_expenses(user_id: str = Depends(current_user)):
    return database.get_all_expenses(user_id=user_id)


@app.post("/expenses", status_code=201, dependencies=protected)
def add_expense(expense: ExpenseSchema, user_id: str = Depends(current_user)):
    new_id = database.add_expense_db(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date or date_cls.today().isoformat(),
        user_id=user_id,
    )
    return {"id": new_id, "message": "Расход успешно добавлен"}


@app.put("/expenses/{expense_id}", dependencies=protected)
def update_expense(
    expense_id: int, expense: ExpenseSchema, user_id: str = Depends(current_user)
):
    success = database.update_expense_db(
        expense_id=expense_id,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        user_id=user_id,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Расход с таким ID не найден")
    return {"message": f"Расход {expense_id} обновлен"}


@app.delete("/expenses/{expense_id}", dependencies=protected)
def delete_expense(expense_id: int, user_id: str = Depends(current_user)):
    success = database.delete_expense_db(expense_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Расход с таким ID не найден")
    return {"message": f"Расход {expense_id} удален"}