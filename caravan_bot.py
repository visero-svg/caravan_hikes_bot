import asyncio
import json
import os
import threading
import http.server
import socketserver

from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto

# Токен бота — обязательно из переменных окружения (безопасно)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Укажите BOT_TOKEN в переменных окружения Render!")

# Список каналов для публикации
CHANNELS = [
    "@caravan_hobby",          # Замени на свои каналы
    "@your_second_channel",
    # "-1001234567890",        # Приватные — через ID
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик данных из Web App (aiogram 3.x)
@dp.message(lambda message: message.web_app_data is not None)
async def handle_web_app(message: types.Message):
    try:
        payload = json.loads(message.web_app_data.data)
    except json.JSONDecodeError:
        await message.answer("Ошибка обработки данных из формы.")
        return

    if payload.get("action") == "publish_hike":
        if "media" in payload:
            for channel in CHANNELS:
                media_group = []
                for item in payload["media"]:
                    media_group.append(InputMediaPhoto(
                        media=item["media"],
                        caption=item.get("caption"),
                        parse_mode="HTML"
                    ))
                await bot.send_media_group(channel, media_group)
        else:
            text = payload.get("text", "Новый поход")
            for channel in CHANNELS:
                await bot.send_message(
                    channel,
                    text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
        
        await message.answer("✅ Поход успешно опубликован во всех каналах!")
    else:
        await message.answer("Неизвестное действие.")

# Простой HTTP-сервер, чтобы Render видел открытый порт
def run_http_server():
    port = int(os.getenv("PORT", 8000))  # Render передаёт порт через $PORT
    handler = http.server.SimpleHTTPRequestHandler
    
    # Создаём сервер, который отвечает простым сообщением
    class QuietHandler(handler):
        def log_message(self, format, *args):
            pass  # Отключаем логи в консоль, чтобы не засорять

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Caravan Hikes Bot is running! 🚴‍♂️")

    with socketserver.TCPServer(("0.0.0.0", port), QuietHandler) as httpd:
        print(f"HTTP-сервер запущен на порту {port} (для Render)")
        httpd.serve_forever()

async def main():
    # Запускаем HTTP-сервер в отдельном потоке (не блокирует polling)
    thread = threading.Thread(target=run_http_server, daemon=True)
    thread.start()

    print("Бот запущен и работает 24/7...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())