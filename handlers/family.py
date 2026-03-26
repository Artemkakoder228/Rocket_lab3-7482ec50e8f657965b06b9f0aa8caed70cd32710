from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from config import WEB_APP_URL
import urllib.parse
from keyboards import get_main_kb_with_family, get_main_kb_no_family

router = Router()
db = Database('space.db')


class FamilyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_code = State()


@router.message(F.text == "🚀 Створити сім'ю")
async def start_create_family(message: types.Message, state: FSMContext):
    await state.set_state(FamilyStates.waiting_for_name)
    await message.answer("Назва команди:")


@router.message(FamilyStates.waiting_for_name)
async def process_family_name(message: types.Message, state: FSMContext):
    db.add_user(message.from_user.id, message.from_user.username or "Cap")
    code = db.create_family(message.from_user.id, message.text)
    await state.clear()
    await message.answer(f"Створено! Код: `{code}`", parse_mode="Markdown", reply_markup=get_main_kb_with_family())


@router.message(F.text == "🔗 Приєднатися до сім'ї")
async def start_join_family(message: types.Message, state: FSMContext):
    await state.set_state(FamilyStates.waiting_for_code)
    await message.answer("Введіть код:")


@router.message(FamilyStates.waiting_for_code)
async def process_join_code(message: types.Message, state: FSMContext):
    db.add_user(message.from_user.id, message.from_user.username or "Recruit")
    if db.join_family(message.from_user.id, message.text.upper().strip()):
        await state.clear()
        await message.answer("Успіх!", reply_markup=get_main_kb_with_family())
    else:
        await message.answer("Помилка.")


@router.message(F.text == "🌌 Кабінет сім'ї")
async def family_info(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid: 
        await message.answer("Ви не в сім'ї!")
        return

    family = db.get_family(fid)
    stats = db.get_ship_total_stats(fid)
    data = db.get_family_resources(fid)
    base = db.get_family_info(fid)
    
    MAX = 10000 

    text = (
        f"🏠 **Кабінет сім'ї: {family[1]}**\n"
        f"🔑 **Код для вступу:** `{fid}`\n\n" # Відображення коду
        f"📊 **Характеристики корабля:**\n"
        f"🚀 Швидкість: **{stats['speed']}**\n"
        f"🛡️ Захист: **{stats['armor']}**\n"
        f"🌬️ Аеро: **{stats['aerodynamics']}**\n"
        f"🕹️ Маневр: **{stats['handling']}**\n"
        f"⚔️ Урон: **{stats['damage']}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **Склад ресурсів:**\n"
        f"🔩 Залізо: **{data[1]}/{MAX}** | ⛽ Паливо: **{data[2]}/{MAX}**\n"
        f"🌑 Реголіт: **{data[3]}/{MAX}** | ⚛️ Гелій-3: **{data[4]}/{MAX}**\n"
        f"💾 Кремній: **{data[5]}/{MAX}** | 🧪 Оксид: **{data[6]}/{MAX}**\n"
        f"🌫 Водень: **{data[7]}/{MAX}** | 🎈 Гелій: **{data[8]}/{MAX}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Баланс: **{data[0]}** монет\n"
        f"🌍 Локація: **{data[11]}**"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "🛸 Ангар (Веб)")
async def open_webapp(message: types.Message):
    # Отримуємо ID сім'ї користувача з бази даних
    fid = db.get_user_family(message.from_user.id)
    if not fid: 
        await message.answer("Спочатку створіть сім'ю або приєднайтеся до неї!")
        return

    res = db.get_family_resources(fid)
    info = db.get_family_info(fid)

    # Додаємо family_id у параметри URL
    params = {
        "family_id": fid,  # <--- ЦЕ НАЙВАЖЛИВІШЕ ДЛЯ ВАЛІДАЦІЇ БД
        "family": info[0], 
        "planet": res[11], 
        "balance": res[0],
        "iron": res[1], 
        "fuel": res[2], 
        "regolith": res[3], 
        "he3": res[4],
        "silicon": res[5], 
        "oxide": res[6], 
        "hydrogen": res[7], 
        "helium": res[8],
        "mine_lvl": res[9]
    }
    
    # Формуємо посилання з параметрами
    url = f"{WEB_APP_URL}?{urllib.parse.urlencode(params)}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🖥 Відкрити термінал", web_app=WebAppInfo(url=url))
    
    await message.answer(
        f"🚀 **Термінал доступу активовано**\nКоманда: {info[0]}", 
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )

@router.message(F.text == "❌ Покинути сім'ю")
async def leave(message: types.Message):
    db.leave_family(message.from_user.id)
    await message.answer("Ви вийшли.", reply_markup=get_main_kb_no_family())