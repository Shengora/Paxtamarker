import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

from dotenv import load_dotenv

load_dotenv()

# .env fayldan yoki muhit o'zgaruvchilaridan token va api url ni olish
API_TOKEN = os.getenv('BOT_TOKEN', '973:27RN6mvIdmW-qjzL-WiUOM9cGWDfVzQOrIH')
PAXTAGRAM_URL = os.getenv('PAXTAGRAM_URL', 'https://paxta.online')

logging.basicConfig(level=logging.INFO)

# Paxtagram server konfiguratsiyasi
session = AiohttpSession(
    api=TelegramAPIServer.from_base(PAXTAGRAM_URL)
)

bot = Bot(token=API_TOKEN, session=session)
dp = Dispatcher()

# Tillarni yuklash
def load_locale(lang_code):
    try:
        with open(f'bot/locales/{lang_code}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('bot/locales/uz.json', 'r', encoding='utf-8') as f:
            return json.load(f)

# Web App klaviaturasini yaratish
def get_webapp_keyboard(texts):
    builder = InlineKeyboardBuilder()
    web_app = types.WebAppInfo(url="https://paxta.online/") # Loyiha deploy qilingach URL o'zgartiriladi
    builder.button(text=texts.get('btn_open_app', "Open App"), web_app=web_app)
    return builder.as_markup()

# Inline klaviaturani yaratish (Fallback)
def get_main_keyboard(texts):
    builder = InlineKeyboardBuilder()
    builder.button(text=texts['btn_buy'], callback_data='buy')
    builder.button(text=texts['btn_sell'], callback_data='sell')
    builder.button(text=texts['btn_deposit'], callback_data='deposit')
    builder.button(text=texts['btn_withdraw'], callback_data='withdraw')
    builder.adjust(2)
    return builder.as_markup()

@dp.message(CommandStart())
@dp.message(Command("help"))
async def send_welcome(message: types.Message):
    # Foydalanuvchi tilini aniqlash (default uz)
    lang = message.from_user.language_code if message.from_user.language_code in ['uz', 'ru', 'en'] else 'uz'
    texts = load_locale(lang)

    # Asosiy variant - Web App orqali ochish.
    # Chat interfeysi bo'lishi so'ralgani uchun, WebApp ko'proq mos keladi.
    keyboard = get_webapp_keyboard(texts)
    await message.reply(texts['welcome'], reply_markup=keyboard)

@dp.callback_query(F.data.in_({'buy', 'sell', 'deposit', 'withdraw'}))
async def process_callback(callback_query: types.CallbackQuery):
    lang = callback_query.from_user.language_code if callback_query.from_user.language_code in ['uz', 'ru', 'en'] else 'uz'
    texts = load_locale(lang)

    action = callback_query.data
    text_key = f"{action}_text"

    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, texts.get(text_key, "Unknown action"))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
