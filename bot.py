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
