import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from openai import AsyncOpenAI

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================
# НАСТРОЙКИ
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# =========================
# ЛОГИ
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================
# СТАРТ
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Аника 🤖\n\n"
        "Я готова отвечать на твои вопросы.\n"
        "Напиши мне что-нибудь."
    )


# =========================
# ОБРАБОТКА СООБЩЕНИЙ
# =========================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    try:
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты Аника — дружелюбный AI-помощник. "
                        "Отвечай понятно, полезно и по существу. "
                        "Отвечай на языке пользователя."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )

        answer = response.choices[0].message.content

        if not answer:
            answer = "Не удалось получить ответ."

        await update.message.reply_text(answer)

    except Exception as error:
        logger.error("Ошибка OpenAI: %s", error)

        await update.message.reply_text(
            "Произошла ошибка при получении ответа. "
            "Попробуй ещё раз."
        )


# =========================
# ПРОСТОЙ WEB-СЕРВЕР
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Anika bot is running")

    def log_message(self, format, *args):
        return


def start_web_server():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler,
    )

    logger.info("Web server started on port %s", port)

    server.serve_forever()


# =========================
# ЗАПУСК БОТА
# =========================

def main():

    if not TELEGRAM_TOKEN:
        raise ValueError(
            "TELEGRAM_TOKEN не найден в Environment Variables"
        )

    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY не найден в Environment Variables"
        )

    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    logger.info("Бот Аника запускается...")

    application.run_polling()


if __name__ == "__main__":
    main()
