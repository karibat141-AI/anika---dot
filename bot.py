import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from openai import AsyncOpenAI


# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY не найден")


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
# ОТВЕТ AI
# =========================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    try:
        await update.message.chat.send_action("typing")

        response = await client.responses.create(
            model="gpt-4.1-mini",
            input=[
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

        answer = response.output_text

        if not answer:
            answer = "Не удалось получить ответ. Попробуй ещё раз."

        await update.message.reply_text(answer)

    except Exception as error:
        logger.exception("Ошибка AI: %s", error)

        await update.message.reply_text(
            "Произошла ошибка при обращении к AI. Попробуй ещё раз."
        )


# =========================
# ПРОВЕРКА RENDER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Anika bot is running!")

    def log_message(self, format, *args):
        return


def start_web_server():
    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    logger.info("Web server started on port %s", port)

    server.serve_forever()


# =========================
# ЗАПУСК
# =========================

def main():

    application = (
        Application.builder()
        .token(BOT_TOKEN)
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
    import threading

    web_thread = threading.Thread(
        target=start_web_server,
        daemon=True
    )

    web_thread.start()

    main()
