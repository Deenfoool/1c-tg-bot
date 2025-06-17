import logging
import json
import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.constants import ParseMode 
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# --- Настройки ---
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

# --- Создаем FastAPI приложение ---
app = FastAPI()

# --- Создаем экземпляр бота ---
application = None

@app.on_event("startup")
async def startup_event():
    global application
    token = '7119996029:AAGJn6MrE5bAb0MYbrQkG7C9e5-ugsAUwH4'  # Токен от BotFather

    application = ApplicationBuilder().token(token).build()
    await application.initialize()  # 🔧 ВАЖНО: Не забудьте это!

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.post("/webhook")
async def webhook(request: Request):
    logger.info("Поступил запрос на /webhook")
    try:
        data = await request.json()
        logger.debug(f"Данные: {data}")
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return "", 200
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return {"error": str(e)}, 500

@app.get("/")
async def root():
    return {"status": "Бот запущен!"}
