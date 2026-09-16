Enter file contents here 
import os
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Аника 🤖\n\nНапиши мне свой вопрос."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    try:
        response = client.responses.create(
            model="gpt-5.6",
            input=[
                {
                    "role": "developer",
                    "content": "Ты полезный Telegram-помощник по имени Аника. Отвечай понятно, дружелюбно и по делу."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        answer = response.output_text

        await update.message.reply_text(answer)

    except Exception as e:
        print("Ошибка:", e)
        await update.message.reply_text(
            "Произошла ошибка. Попробуй ещё раз."
        )


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    print("Аника запущена!")
    application.run_polling()


if __name__ == "__main__":
    main()
