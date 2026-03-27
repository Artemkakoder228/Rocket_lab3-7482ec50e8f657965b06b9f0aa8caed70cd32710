import time
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from config import WEB_APP_URL

router = Router()
db = Database()

@router.message(Command("shop"))
@router.message(F.text == "🛒 Магазин")
async def shop_index(message: types.Message):
    family_id = db.get_user_family(message.from_user.id)
    
    if not family_id:
        await message.answer("❌ Ви не входите до складу жодної сім'ї. Створіть її через /start.")
        return

    # Формуємо посилання на окрему сторінку магазину
    base_url = WEB_APP_URL.rstrip('/')
    shop_url = f"{base_url}/shop.html?family_id={family_id}&t={int(time.time())}"

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌌 ВІДКРИТИ ЧОРНИЙ РИНОК", web_app=WebAppInfo(url=shop_url))]
    ])

    text = (
        "🛒 **ЧОРНИЙ РИНОК (Магазин)**\n\n"
        "Щодня торговці з різних куточків галактики привозять нові ресурси зі знижками.\n"
        "⏳ *Асортимент та ціни оновлюються кожні 24 години!*\n\n"
        "Натисніть кнопку нижче, щоб увійти в термінал торгівлі:"
    )
    
    await message.answer(text, reply_markup=inline_kb, parse_mode="Markdown")