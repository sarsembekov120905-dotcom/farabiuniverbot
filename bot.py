import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

FAQ = {
    "как узнать расписание": "Расписание можно посмотреть в личном кабинете студента.",
    "где посмотреть оценки": "Оценки можно посмотреть в системе Univer.",
    "как получить справку": "Справку можно заказать через портал студентов или в деканате.",
    "как восстановить пароль": "Нажмите 'Забыли пароль' на странице входа.",
    "как подать на общежитие": "Подать заявку можно через студенческий портал.",
    "wifi казну": "Данные для WiFi можно найти во вкладке Бакалавр в личном кабинете."
}

SYSTEM_PROMPT = """
Ты помощник для студентов Farabi University.
Отвечай кратко, понятно и по делу.
Если ты не уверен в точности ответа, честно скажи об этом и посоветуй уточнить в деканате,
офисе регистратора, службе поддержки или на официальном сайте университета.
Не выдумывай даты, кабинеты, ссылки и контакты.
Отвечай на том языке, на котором написал студент.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Как узнать расписание", "Где посмотреть оценки"],
        ["Как получить справку", "Как восстановить пароль"],
        ["Как подать на общежитие", "WiFi КазНУ"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я бот для студентов Farabi University.\n"
        "Выбери вопрос кнопкой или напиши свой.",
        reply_markup=reply_markup
    )

def ask_deepseek(user_text: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    normalized = text.lower()

    if normalized in FAQ:
        await update.message.reply_text(FAQ[normalized])
        return

    if not DEEPSEEK_API_KEY:
        await update.message.reply_text(
            "Умный режим пока не настроен. Попробуй задать вопрос иначе."
        )
        return

    try:
        ai_answer = ask_deepseek(text)
        if not ai_answer:
            ai_answer = "Не получилось подготовить ответ. Попробуй ещё раз."
        await update.message.reply_text(ai_answer)
    except Exception:
        await update.message.reply_text(
            "Сейчас не получается обратиться к ИИ. Попробуй чуть позже."
        )

def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
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
