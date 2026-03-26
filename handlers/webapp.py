import json
from aiogram import Router, F, types
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import Database

# Імпорт клавіатури для кнопки "Назад"
from keyboards import main_keyboard

router = Router()
db = Database() # Виправлено: прибрано зайвий аргумент 'space.db'

# --- ПОСИЛАННЯ ---
ARCADE_URL = "https://artemkakoder228.github.io/Game/"
RENDER_URL = "https://rocket-lab2.onrender.com"

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

    # Формуємо персональне посилання з ID
    personal_url = f"{RENDER_URL}?family_id={family_id}"

    builder = ReplyKeyboardBuilder()
    # Передаємо personal_url замість загального RENDER_URL
    builder.button(text="🖥 ВІДКРИТИ ТЕРМІНАЛ", web_app=WebAppInfo(url=personal_url))
    builder.button(text="🔙 Назад")
    builder.adjust(1)

    await message.answer(
        "🛸 **БОРТОВИЙ КОМП'ЮТЕР**\n\n"
        "Завантаження систем керування та інвентарю...\n"
        "Натисніть кнопку нижче для входу в систему.",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode="Markdown"
    )

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