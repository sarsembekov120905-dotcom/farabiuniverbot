import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("8643950667:AAGfKOG1ETx6w5WABIWKIkOrv1N8ZU9-MPI")

FAQ = {
    "как узнать расписание": "Расписание можно посмотреть в личном кабинете студента или на официальных ресурсах университета.",
    "где посмотреть оценки": "Оценки можно посмотреть в личном кабинете студента.",
    "как получить справку": "Справку можно заказать через студенческий портал или в офисе обслуживания студентов.",
    "как восстановить пароль": "Для восстановления пароля воспользуйтесь страницей входа и нажмите 'Забыли пароль?'.",
    "как подать на общежитие": "Информацию по общежитию можно уточнить в студенческом отделе или на портале университета.",
    "подключение к корпоративной сети казну": "Нужно перейти во вкладку Бакалавр. В разделе Логин и пароль для системы print.kaznu.kz и WiFi-сети КазНУ будут данные от WiFi-сети КазНУ."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Как узнать расписание", "Где посмотреть оценки"],
        ["Как получить справку", "Как восстановить пароль"],
        ["Как подать на общежитие", "Подключение к корпоративной сети КазНУ"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я бот для студентов Farabi University.\nВыбери вопрос кнопкой или напиши его сам.",
        reply_markup=reply_markup
    )

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()

    if text in FAQ:
        await update.message.reply_text(FAQ[text])
    else:
        await update.message.reply_text("Я пока не знаю точный ответ на этот вопрос. Попробуй написать иначе.")

def main():
    if not TOKEN:
        raise ValueError("Не найдена переменная окружения TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()