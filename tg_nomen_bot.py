import logging
import json
import os
from flask import Flask, request
from telegram import Update
from telegram.constants import ParseMode  # ✅ Правильный импорт
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters


# --- Настройки ---
LOG_FILE = 'bot.log'
DATA_FILE = 'nomenclature.json'

# --- Инициализация логгера ---
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Загрузка данных из JSON ---
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки файла: {e}")
        return {}

# --- Обработка команды /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введите код или наименование товара.")

# --- Основная обработка сообщений ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    nomen_dict = load_data()
    
    if not nomen_dict:
        await update.message.reply_text("Не могу найти данные. Проверьте файл.")
        return
    
    # Поиск по коду
    if text.isdigit():
        code = text
        item = nomen_dict.get(code)
        if item:
            reply = (
                f"Наименование: {item['наименование']}\n"
                f"Артикул: {item['артикул']}"
            )
        else:
            reply = "Товар не найден."
        await update.message.reply_text(reply)
        return
    
    # Поиск по частичному совпадению
    matches = []
    for code, item in nomen_dict.items():
        if text.lower() in item['наименование'].lower():
            matches.append({
                "код": code,
                "наименование": item['наименование'],
                "артикул": item['артикул']
            })

    if not matches:
        await update.message.reply_text("Ничего не найдено.")
        return

    # Формируем ответ
    response = "Результаты поиска:\n\n"
    for match in matches[:5]:  # Максимум 5 результатов
        response += (
            f"Код: `{match['код']}`\n"
            f"Наименование: {match['наименование']}\n"
            f"Артикул: {match['артикул']}\n\n"
        )

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2)

# --- Главная функция ---
app = Flask(__name__)
application = None

@app.route('/')
def index():
    return 'Бот запущен!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, application.bot)
    application.process_update(update)  # <-- без await
    return '', 200

if __name__ == "__main__":
    token = '7119996029:AAGJn6MrE5bAb0MYbrQkG7C9e5-ugsAUwH4'  # Токен от BotFather

    application = ApplicationBuilder().token(token).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запуск Flask-приложения
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
