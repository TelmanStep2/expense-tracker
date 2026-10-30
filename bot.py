import logging
import os

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
# Не выводим в лог полные URL запросов: в них есть токен бота
logging.getLogger("httpx").setLevel(logging.WARNING)

HELP_TEXT = (
    "Команды:\n"
    "/add 50 food обед — добавить расход (сумма, категория, описание)\n"
    "/list — последние расходы\n"
    "/total — итоги по категориям\n"
    "/delete 5 — удалить расход с номером 5\n"
    "/myid — показать ваш Telegram ID"
)


# ---------- чистые функции (их проверяют тесты) ----------

def parse_add_args(args):
    """Разбирает аргументы /add: сумма, категория, необязательное описание."""
    if len(args) < 2:
        raise ValueError("Формат: /add сумма категория [описание]")
    try:
        amount = float(args[0].replace(",", "."))
    except ValueError:
        raise ValueError("Сумма должна быть числом, например 50 или 12.5")
    if amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")
    category = args[1]
    description = " ".join(args[2:]) or None
    return amount, category, description


def format_expenses(expenses, limit=30):
    if not expenses:
        return "Расходов пока нет."
    shown = expenses[-limit:]
    lines = []
    for e in shown:
        line = f'{e["id"]}. {e["date"]} | {e["category"]} | {e["amount"]:.2f}'
        if e.get("description"):
            line += f' | {e["description"]}'
        lines.append(line)
    text = "\n".join(lines)
    if len(expenses) > limit:
        text = f"Показаны последние {limit} из {len(expenses)}:\n" + text
    return text


def format_total(expenses):
    if not expenses:
        return "Расходов пока нет."
    by_category = {}
    for e in expenses:
        by_category[e["category"]] = by_category.get(e["category"], 0) + e["amount"]
    lines = [f"{cat}: {total:.2f}" for cat, total in sorted(by_category.items())]
    return "\n".join(lines) + f"\n\nИтого: {sum(by_category.values()):.2f}"


def user_key(telegram_id):
    """Ключ владельца расходов в API.

    Если задана OWNER_USER_ID и это ваш Telegram ID, бот работает с общими
    данными веб-страницы и консоли ('web'). Остальные получают свои расходы.
    """
    owner = os.getenv("OWNER_USER_ID", "")
    if owner.isdigit() and int(owner) == telegram_id:
        return "web"
    return f"tg:{telegram_id}"


# ---------- работа с API ----------

def get_api_url():
    return os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


async def call_api(method, path, user_id, **kwargs):
    auth = None
    user, password = os.getenv("APP_USER"), os.getenv("APP_PASSWORD")
    if user and password:
        auth = (user, password)
    async with httpx.AsyncClient(
        base_url=get_api_url(),
        auth=auth,
        timeout=10,
        headers={"X-User-Id": user_id},
    ) as client:
        return await client.request(method, path, **kwargs)


def api_error_text(response):
    if response.status_code == 401:
        return "API отклонил логин или пароль (проверьте APP_USER и APP_PASSWORD)."
    return f"Ошибка API: {response.status_code}"


# ---------- доступ только для разрешённых ----------

def allowed_user_ids():
    """Список разрешённых Telegram ID через запятую: ALLOWED_USER_IDS=111,222."""
    raw = os.getenv("ALLOWED_USER_IDS") or os.getenv("ALLOWED_USER_ID", "")
    return {int(x) for x in raw.replace(" ", "").split(",") if x.isdigit()}


async def check_access(update: Update) -> bool:
    allowed = allowed_user_ids()
    if not allowed or update.effective_user.id in allowed:
        return True
    await update.message.reply_text("Нет доступа.")
    return False


# ---------- команды ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    await update.message.reply_text("Привет! Я бот-трекер расходов.\n\n" + HELP_TEXT)


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Работает для всех: нужна, чтобы узнать свой ID для ALLOWED_USER_IDS
    await update.message.reply_text(f"Ваш Telegram ID: {update.effective_user.id}")


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    try:
        amount, category, description = parse_add_args(context.args)
    except ValueError as error:
        await update.message.reply_text(str(error))
        return
    uid = user_key(update.effective_user.id)
    try:
        response = await call_api(
            "POST",
            "/expenses",
            uid,
            json={"amount": amount, "category": category, "description": description},
        )
    except httpx.HTTPError:
        await update.message.reply_text("API недоступен. Запущен ли сервер?")
        return
    if response.status_code == 201:
        await update.message.reply_text(
            f"Добавлено: {amount:.2f} | {category} (№{response.json()['id']})"
        )
    else:
        await update.message.reply_text(api_error_text(response))


async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    uid = user_key(update.effective_user.id)
    try:
        response = await call_api("GET", "/expenses", uid)
    except httpx.HTTPError:
        await update.message.reply_text("API недоступен. Запущен ли сервер?")
        return
    if response.status_code != 200:
        await update.message.reply_text(api_error_text(response))
        return
    await update.message.reply_text(format_expenses(response.json()))


async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    uid = user_key(update.effective_user.id)
    try:
        response = await call_api("GET", "/expenses", uid)
    except httpx.HTTPError:
        await update.message.reply_text("API недоступен. Запущен ли сервер?")
        return
    if response.status_code != 200:
        await update.message.reply_text(api_error_text(response))
        return
    await update.message.reply_text(format_total(response.json()))


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Формат: /delete номер (номер смотрите в /list)")
        return
    expense_id = int(context.args[0])
    uid = user_key(update.effective_user.id)
    try:
        response = await call_api("DELETE", f"/expenses/{expense_id}", uid)
    except httpx.HTTPError:
        await update.message.reply_text("API недоступен. Запущен ли сервер?")
        return
    if response.status_code == 200:
        await update.message.reply_text(f"Расход №{expense_id} удалён.")
    elif response.status_code == 404:
        await update.message.reply_text("Расхода с таким номером нет.")
    else:
        await update.message.reply_text(api_error_text(response))


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Не задана переменная окружения BOT_TOKEN")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_expenses))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("delete", delete))
    app.run_polling()


if __name__ == "__main__":
    main()