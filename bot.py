import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FAQ = {
    "как узнать расписание": "Расписание можно посмотреть в личном кабинете студента.",
    "где посмотреть оценки": "Оценки можно посмотреть в системе Univer.",
    "как получить справку": "Справку можно заказать через портал студентов или в деканате.",
    "как восстановить пароль": "Нажмите 'Забыли пароль' на странице входа.",
    "как подать на общежитие": "Подать заявку можно через студенческий портал.",
    "wifi казну": "Данные для WiFi можно найти во вкладке Бакалавр в личном кабинете."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Как узнать расписание", "Где посмотреть оценки"],
        ["Как получить справку", "Как восстановить пароль"],
        ["Как подать на общежитие", "WiFi КазНУ"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я бот для студентов Farabi University.\n"
        "Выберите вопрос кнопкой или напишите свой.",
        reply_markup=reply_markup
    )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()

    if text in FAQ:
        await update.message.reply_text(FAQ[text])
    else:
        await update.message.reply_text(
            "Пока не знаю точного ответа. Попробуй задать вопрос иначе."
        )

def run_bot():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    print("Бот запущен...")
    app.run_polling()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Web server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    run_bot()
