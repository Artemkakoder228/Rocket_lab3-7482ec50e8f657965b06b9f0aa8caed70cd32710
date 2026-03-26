import json
from aiogram import Router, F, types
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import Database
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

from keyboards import main_keyboard
# Імпортуємо актуальне посилання з вашого config.py
from config import WEB_APP_URL

router = Router()
db = Database()

# --- ПОСИЛАННЯ ---
ARCADE_URL = "https://artemkakoder228.github.io/Game/"

# ==========================================
# 1. ОБРОБНИК ДЛЯ "КОСМІЧНИЙ БІЙ" (СТАРА ГРА)
# ==========================================
@router.message(F.text == "👾 Космічний бій")
async def open_arcade_game(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚀 ПОЧАТИ БІЙ", web_app=WebAppInfo(url=ARCADE_URL))
    builder.button(text="🔙 Назад")
    builder.adjust(1)

    await message.answer(
        "🎮 **АРКАДНИЙ РЕЖИМ**\n\n"
        "Знищуйте ворогів, щоб заробити кредити!\n"
        "1 збитий ворог = **10 монет**.",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode="Markdown"
    )

# ==========================================
# 2. ОБРОБНИК ДЛЯ "ПОЛІТ (ВЕБ)" (НОВИЙ САЙТ)
# ==========================================
@router.message(F.text == "🛸 Політ (Веб)")
async def open_render_app(message: types.Message):
    user_id = message.from_user.id
    family_id = db.get_user_family(user_id)

    if not family_id:
        await message.answer("⚠️ У вас немає сім'ї! Створіть її через /start.", reply_markup=main_keyboard())
        return

    # 1. Отримуємо планету та ОБОВ'ЯЗКОВО прибираємо зайві пробіли (.strip())
    family_info = db.get_family_info(family_id)
    current_planet = family_info[5].strip() if family_info and family_info[5] else 'Earth'

    # 2. Визначаємо сторінку
    planet_pages = {
        'Earth': '',            # index.html
        'Moon': 'Moon.html',
        'Mars': 'Mars.html',
        'Jupiter': 'Jupiter.html'
    }
    
    # Якщо планети немає в словнику, за замовчуванням відкриваємо Землю
    page = planet_pages.get(current_planet, '')

    # 3. Формуємо посилання без подвійних слешів
    base_url = WEB_APP_URL.rstrip('/') # Прибираємо слеш в кінці, якщо він є в config.py
    
    if page:
        personal_url = f"{base_url}/{page}?family_id={family_id}&t={int(time.time())}"
    else:
        personal_url = f"{base_url}/?family_id={family_id}&t={int(time.time())}"

    print(f"[DEBUG] Planeta з БД: '{current_planet}' | Згенерований URL: {personal_url}")

    # 4. Створюємо Inline-кнопку під повідомленням
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖥 ВІДКРИТИ ТЕРМІНАЛ", web_app=WebAppInfo(url=personal_url))]
    ])

    await message.answer(
        f"🛸 **БОРТОВИЙ КОМП'ЮТЕР**\n\n"
        f"📍 Поточна локація: **{current_planet}**\n"
        f"Завантаження систем...\n"
        f"Натисніть кнопку нижче для входу:",
        reply_markup=inline_kb,
        parse_mode="Markdown"
    )
    
    # Оновлюємо нижню клавіатуру, щоб була кнопка "Назад"
    await message.answer("Навігація:", reply_markup=builder.as_markup(resize_keyboard=True))
# ==========================================
# 3. КНОПКА "НАЗАД"
# ==========================================
@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Головне меню", reply_markup=main_keyboard())

# ==========================================
# 4. ОБРОБКА ДАНИХ (SCORE)
# ==========================================
@router.message(F.web_app_data)
async def process_game_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        if data.get('action') == 'game_score':
            score = int(data.get('amount', 0))

            if score <= 0:
                await message.answer("Ви нікого не збили. Спробуйте ще раз!", reply_markup=main_keyboard())
                return

            fid = db.get_user_family(message.from_user.id)
            if fid:
                db.update_balance(fid, score)
                await message.answer(
                    f"🏁 **РЕЗУЛЬТАТ:**\n"
                    f"💰 Зароблено: **{score}** монет",
                    reply_markup=main_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await message.answer("У вас немає сім'ї для нарахування монет.", reply_markup=main_keyboard())

    except Exception as e:
        print(f"Web App Error: {e}")
        await message.answer("Дані отримано, але сталася помилка обробки.", reply_markup=main_keyboard())