import json
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Константы
NOMENCLATURE_FILE = 'nomenclature.json'
CHUNK_SIZE = 5  # Количество записей на странице

# Функция для экранирования специальных символов MarkdownV2
def escape_markdown(text):
    """Экранирует символы, которые могут вызвать ошибку в MarkdownV2."""
    return text.replace('*', r'\*') \
               .replace('_', r'\_') \
               .replace('`', r'\`') \
               .replace('[', r'\[') \
               .replace(']', r'\]') \
               .replace('(', r'\(') \
               .replace(')', r'\)') \
               .replace('~', r'\~') \
               .replace('>', r'\>') \
               .replace('#', r'\#') \
               .replace('+', r'\+') \
               .replace('=', r'\=') \
               .replace('|', r'\|') \
               .replace('{', r'\{') \
               .replace('}', r'\}') \
               .replace('!', r'\!')

# Загрузка номенклатуры из файла
def load_nomenclature():
    try:
        with open(NOMENCLATURE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        logging.error("Ошибка чтения JSON-файла.")
        return []

# Сохранение номенклатуры в файл
def save_nomenclature(nomenclature):
    with open(NOMENCLATURE_FILE, 'w', encoding='utf-8') as f:
        json.dump(nomenclature, f, ensure_ascii=False, indent=4)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Для поиска позиции введите Код или Наименование или Артикул\n"
                                    "Вы можете использовать команды:\n"
                                    "/add [Код] [Наименование] [Артикул] - добавить новую позицию\n"
                                    "/list - показать первые 10 записей\n"
                                    "/delete [Код] - удалить запись")

# Поиск по запросу (по коду, артикулу, наименованию)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    nomenclature = load_nomenclature()

    results = []
    for item in nomenclature:
        if (query == item['code'] or 
            query.lower() in item['name'].lower() or 
            query.lower() in item['article'].lower()):
            results.append(item)

    if not results:
        await update.message.reply_text("Ничего не найдено.")
        return

    message_chunks = []
    for i in range(0, len(results), CHUNK_SIZE):
        chunk = results[i:i+CHUNK_SIZE]
        chunk_message = "По вашему запросу я нашел, это:\n\n"
        for result in chunk:
            chunk_message += (
                f"🔹 *Код:* `{result['code']}`\n"
                f"🔹 *Наименование:* {escape_markdown(result['name'])}\n"
                f"🔹 *Артикул:* `{result['article']}`\n\n"
            )
        message_chunks.append(chunk_message)

    for chunk in message_chunks:
        try:
            await update.message.reply_text(chunk, parse_mode='MarkdownV2')
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение в Markdown: {e}")
            await update.message.reply_text(chunk)

# Добавление новой позиции
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split(' ', 3)
    if len(parts) < 4 or parts[0] != '/add':
        await update.message.reply_text("Используйте формат: /add [Код] [Наименование] [Артикул]")
        return

    code = parts[1]
    name = parts[2]
    article = parts[3]

    nomenclature = load_nomenclature()
    
    # Проверка на дубликат по коду
    for item in nomenclature:
        if item['code'] == code:
            await update.message.reply_text(f"❌ Запись с кодом `{code}` уже существует.")
            return

    nomenclature.append({'code': code, 'name': name, 'article': article})
    save_nomenclature(nomenclature)

    await update.message.reply_text("✅ Запись сохранена.")

# Вывод первых 10 записей
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nomenclature = load_nomenclature()
    if not nomenclature:
        await update.message.reply_text("❌ Номенклатура пуста.")
        return

    message = "📋 Первые 10 записей:\n\n"
    for item in nomenclature[:10]:
        message += (
            f"🔹 Код: {item['code']}\n"
            f"🔹 Наименование: {escape_markdown(item['name'])}\n"
            f"🔹 Артикул: {item['article']}\n\n"
        )

    try:
        await update.message.reply_text(message, parse_mode='MarkdownV2')
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение в Markdown: {e}")
        await update.message.reply_text(message)

# Удаление записи по коду
async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split(' ')
    if len(parts) < 2 or parts[0] != '/delete':
        await update.message.reply_text("Используйте формат: /delete [Код]")
        return

    code_to_delete = parts[1]
    nomenclature = load_nomenclature()

    found = False
    new_nomenclature = []
    for item in nomenclature:
        if item['code'] == code_to_delete:
            found = True
        else:
            new_nomenclature.append(item)

    if found:
        save_nomenclature(new_nomenclature)
        await update.message.reply_text(f"✅ Запись с кодом `{code_to_delete}` удалена.")
    else:
        await update.message.reply_text(f"❌ Запись с кодом `{code_to_delete}` не найдена.")

# Основная функция
def main():
    application = ApplicationBuilder().token("7119996029:AAGJn6MrE5bAb0MYbrQkG7C9e5-ugsAUwH4").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_items))
    application.add_handler(MessageHandler(filters.Regex(r'^/delete '), delete_item))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    application.add_handler(MessageHandler(filters.Regex(r'^/add '), add_item))

    application.run_polling()

if __name__ == "__main__":
    main()
