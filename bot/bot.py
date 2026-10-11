import os
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from dotenv import load_dotenv

load_dotenv()

# .env fayldan yoki muhit o'zgaruvchilaridan token va api url ni olish
API_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
# Paxtagram API url i agar farq qilsa, shu yerda o'zgartiriladi.
# Masalan: PAXTAGRAM_API_URL = "https://paxta.online/bot{token}/{method}"
# Hozircha aiogram uchun default telegram api ishlatiladi, lekin
# agar custom api bo'lsa uni aiogram server konfiguratsiyasi orqali o'zgartirish mumkin.

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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
    keyboard = InlineKeyboardMarkup(row_width=1)
    web_app = types.WebAppInfo(url="https://paxta.online/webapp/") # Loyiha deploy qilingach URL o'zgartiriladi
    keyboard.add(
        InlineKeyboardButton(texts.get('btn_open_app', "Open App"), web_app=web_app)
    )
    return keyboard

# Inline klaviaturani yaratish (Fallback)
def get_main_keyboard(texts):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(texts['btn_buy'], callback_data='buy'),
        InlineKeyboardButton(texts['btn_sell'], callback_data='sell'),
        InlineKeyboardButton(texts['btn_deposit'], callback_data='deposit'),
        InlineKeyboardButton(texts['btn_withdraw'], callback_data='withdraw')
    )
    return keyboard

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    # Foydalanuvchi tilini aniqlash (default uz)
    lang = message.from_user.language_code if message.from_user.language_code in ['uz', 'ru', 'en'] else 'uz'
    texts = load_locale(lang)

    # Asosiy variant - Web App orqali ochish.
    # Chat interfeysi bo'lishi so'ralgani uchun, WebApp ko'proq mos keladi.
    keyboard = get_webapp_keyboard(texts)
    await message.reply(texts['welcome'], reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ['buy', 'sell', 'deposit', 'withdraw'])
async def process_callback(callback_query: types.CallbackQuery):
    lang = callback_query.from_user.language_code if callback_query.from_user.language_code in ['uz', 'ru', 'en'] else 'uz'
    texts = load_locale(lang)

    action = callback_query.data
    text_key = f"{action}_text"

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, texts.get(text_key, "Unknown action"))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
