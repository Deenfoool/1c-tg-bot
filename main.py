import os
import json
import re
import datetime
import logging
from dotenv import load_dotenv
from telegram import (
    Message,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
    WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
import asyncio

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Константы
NOMENCLATURE_FILE = 'nomenclature.json'
CHUNK_SIZE = 5  # Количество записей на странице

# Экранирование для HTML
def escape_html(text):
    if not text:
        return ''
    html_chars = ['<', '>', '&']
    for char in html_chars:
        text = text.replace(char, f'&#{ord(char)};')
    return text

# Логирование действий
def log_user_action(user_id, action, message_text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{timestamp}] Пользователь {user_id} выполнил действие '{action}': {message_text}")

# Загрузка номенклатуры
def load_nomenclature():
    try:
        with open(NOMENCLATURE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка чтения JSON-файла: {e}")
        return []

# Сохранение номенклатуры
def save_nomenclature(nomenclature):
    try:
        with open(NOMENCLATURE_FILE, 'w', encoding='utf-8') as f:
            json.dump(nomenclature, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка сохранения файла: {e}")

# Отображение страницы списка номенклатуры
async def show_list_page(message: Message, context: ContextTypes.DEFAULT_TYPE, page_index: int):
    nomenclature = load_nomenclature()
    total_pages = (len(nomenclature) + CHUNK_SIZE - 1) // CHUNK_SIZE
    current_page = page_index + 1
    chunk = nomenclature[page_index * CHUNK_SIZE : (page_index + 1) * CHUNK_SIZE]
    message_text = f"<b>📋 Список записей</b> (страница {current_page}/{total_pages}):\n"
    for item in chunk:
        message_text += (
            f"🔹 Код: <code>{item['code']}</code>\n"
            f"🔹 Наименование: {escape_html(item['name'])}\n\n"
        )
    keyboard = []
    if current_page > 1:
        keyboard.append([InlineKeyboardButton("⬅️ Предыдущая", callback_data="prev_list")])
    if current_page < total_pages:
        keyboard.append([InlineKeyboardButton("➡️ Следующая", callback_data="next_list")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await message.edit_text(message_text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Не удалось обновить сообщение: {e}")
        await message.reply_text(message_text, reply_markup=reply_markup)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update.effective_user.id, "/start", update.message.text)
    await update.message.reply_text(
        "👋 Привет! Я ваш помощник в работе с номенклатурой.\n"
        "🔹 Используйте команды или кнопки ниже:\n"
        "/add [Код] [Наименование] – добавить новую позицию\n"
        "/list – показать первые 10 записей\n"
        "/delete [Код] – удалить запись\n"
        "/help – помощь\n"
        "/import – импортировать данные из .txt\n"
        "/webapp – открыть интерфейс управления"
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔧 Доступные команды:
/start – начать работу  
/add [Код] [Наименование] – добавить новую позицию  
/list – показать первые 10 записей  
/delete [Код] – удалить запись  
/help – эта помощь  
/import – импортировать данные из .txt  
/webapp – открыть интерфейс управления
"""
    await update.message.reply_text(help_text)
    log_user_action(update.effective_user.id, "help", update.message.text)

# Команда /import
async def import_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update.effective_user.id, "import", update.message.text)
    await update.message.reply_text("📎 Прикрепите .txt файл с данными.")

# Обработка документа (.txt)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Формат файла должен быть .txt")
        return
    new_file = await document.get_file()
    file_path = f"temp_{document.file_id}.txt"
    try:
        await new_file.download_to_drive(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        nomenclature = []
        for line in lines:
            parts = line.split(' ', 1)
            if len(parts) < 2:
                continue
            code, name = parts[0], parts[1]
            if code.isdigit():
                nomenclature.append({'code': code, 'name': name})
            else:
                logging.warning(f"Пропущена строка с некорректным кодом: {line}")
        save_nomenclature(nomenclature)
        await update.message.reply_text("✅ Данные успешно импортированы.")
    except Exception as e:
        logging.error(f"Ошибка при обработке файла: {e}")
        await update.message.reply_text(f"❌ Произошла ошибка: {str(e)}")
    finally:
        try:
            os.remove(file_path)
        except:
            pass

# Добавление новой позиции
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split(' ', 2)
    if len(parts) < 3 or parts[0] != '/add':
        await update.message.reply_text("❌ Используйте формат: /add [Код] [Наименование]")
        return
    code = parts[1]
    name = parts[2]
    if not code.isdigit():
        await update.message.reply_text("❌ Код должен содержать только цифры.")
        return
    if len(code) < 5:
        await update.message.reply_text("❌ Код слишком короткий. Минимум 5 символов.")
        return
    nomenclature = load_nomenclature()
    if any(item['code'] == code for item in nomenclature):
        await update.message.reply_text(f"❌ Запись с кодом <code>{code}</code> уже существует.")
        return
    nomenclature.append({'code': code, 'name': name})
    save_nomenclature(nomenclature)
    await update.message.reply_text("✅ Запись сохранена.")
    log_user_action(update.effective_user.id, "add", update.message.text)

# Вывод первых 10 записей
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nomenclature = load_nomenclature()
    if not nomenclature:
        await update.message.reply_text("❌ Номенклатура пуста.")
        return
    context.user_data['list_message'] = await update.message.reply_text("Загрузка...")
    context.user_data['list_page'] = 0
    await show_list_page(context.user_data['list_message'], context, 0)
    log_user_action(update.effective_user.id, "list", update.message.text)

# Удаление записи
async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split(' ')
    if len(parts) < 2 or parts[0] != '/delete':
        await update.message.reply_text("❌ Используйте формат: /delete [Код]")
        return
    code_to_delete = parts[1]
    nomenclature = load_nomenclature()
    found = any(item['code'] == code_to_delete for item in nomenclature)
    new_nomenclature = [item for item in nomenclature if item['code'] != code_to_delete]
    if found:
        save_nomenclature(new_nomenclature)
        await update.message.reply_text(f"✅ Запись с кодом <code>{code_to_delete}</code> удалена.")
    else:
        await update.message.reply_text(f"❌ Запись с кодом <code>{code_to_delete}</code> не найдена.")
    log_user_action(update.effective_user.id, "delete", update.message.text)

# Поиск по запросу + пагинация
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    nomenclature = load_nomenclature()
    results = [
        item for item in nomenclature
        if query == item['code'] or query.lower() in item['name'].lower()
    ]
    if not results:
        await update.message.reply_text("🔍 Ничего не найдено.")
        return
    context.user_data['search_results'] = results
    context.user_data['page'] = 0
    context.user_data['search_message'] = await update.message.reply_text("Загрузка...")
    await show_search_page(context.user_data['search_message'], context, 0)

# Отображение страницы результатов поиска
async def show_search_page(message: Message, context: ContextTypes.DEFAULT_TYPE, page_index: int):
    results = context.user_data.get('search_results')
    total_pages = (len(results) + CHUNK_SIZE - 1) // CHUNK_SIZE
    current_page = page_index + 1
    chunk = results[page_index * CHUNK_SIZE : (page_index + 1) * CHUNK_SIZE]
    message_text = f"<b>🔍 Результаты поиска</b> (страница {current_page}/{total_pages}):\n"
    for item in chunk:
        message_text += (
            f"🔹 Код: <code>{item['code']}</code>\n"
            f"🔹 Наименование: {escape_html(item['name'])}\n\n"
        )
    keyboard = []
    if current_page > 1:
        keyboard.append([InlineKeyboardButton("⬅️ Предыдущая", callback_data="prev")])
    if current_page < total_pages:
        keyboard.append([InlineKeyboardButton("➡️ Следующая", callback_data="next")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await message.edit_text(message_text, parse_mode='HTML', reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Не удалось обновить сообщение: {e}")
        await message.reply_text(message_text, reply_markup=reply_markup)

# Обработка кнопок пагинации
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "prev":
        current_page = context.user_data.get('page', 0)
        if current_page > 0:
            context.user_data['page'] -= 1
            await show_search_page(query.message, context, context.user_data['page'])

    elif data == "next":
        current_page = context.user_data.get('page', 0)
        results = context.user_data.get('search_results', [])
        max_page = (len(results) + CHUNK_SIZE - 1) // CHUNK_SIZE - 1
        if current_page < max_page:
            context.user_data['page'] += 1
            await show_search_page(query.message, context, context.user_data['page'])

    elif data == "prev_list":
        current_page = context.user_data.get('list_page', 0)
        if current_page > 0:
            context.user_data['list_page'] -= 1
            await show_list_page(query.message, context, context.user_data['list_page'])

    elif data == "next_list":
        current_page = context.user_data.get('list_page', 0)
        nomenclature = load_nomenclature()
        max_page = (len(nomenclature) + CHUNK_SIZE - 1) // CHUNK_SIZE - 1
        if current_page < max_page:
            context.user_data['list_page'] += 1
            await show_list_page(query.message, context, context.user_data['list_page'])

# Команда /webapp — открывает Mini App
async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = InlineKeyboardButton(
        "📦 Открыть интерфейс",
        web_app=WebAppInfo(url='https://1c-tg-bot-deenfoool.amvera.io/') 
    )
    reply_markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text("Откройте веб-интерфейс:", reply_markup=reply_markup)

# Обработка неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update.effective_user.id, "unknown", update.message.text)
    await update.message.reply_text("❓ Неизвестная команда. Используйте /help для помощи.")

# Основной функционал бота
async def main():
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("import", import_command))
    application.add_handler(CommandHandler("list", list_items))
    application.add_handler(CommandHandler("webapp", webapp_command))
    application.add_handler(MessageHandler(filters.Regex(r'^/delete '), delete_item))
    application.add_handler(MessageHandler(filters.Regex(r'^/add '), add_item))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    application.add_handler(MessageHandler(filters.Document.TEXT, handle_document))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Запуск
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
