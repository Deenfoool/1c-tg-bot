import logging
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

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
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Введите код или название товара.")

# --- Основная обработка сообщений ---
def echo(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    
    nomen_dict = load_data()
    
    if not nomen_dict:
        update.message.reply_text("Не могу найти данные. Проверьте файл.")
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
        update.message.reply_text(reply)
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
        update.message.reply_text("Ничего не найдено.")
        return

    # Формируем ответ
    response = "Результаты поиска:\n\n"
    for match in matches[:5]:  # Максимум 5 результатов
        response += (
            f"Код: `{match['код']}`\n"
            f"Наименование: {match['наименование']}\n"
            f"Артикул: {match['артикул']}\n\n"
        )

    update.message.reply_text(response, parse_mode='Markdown')

# --- Главная функция ---
def main():
    token = '7119996029:AAGJn6MrE5bAb0MYbrQkG7C9e5-ugsAUwH4'

    updater = Updater(token)
    dispatcher = updater.dispatcher

    # Регистрация обработчиков
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
