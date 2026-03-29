from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import WebAppInfo, CallbackQuery
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
        await message.answer("Помилка. Перевірте правильність коду.")


@router.message(F.text == "🌌 Кабінет сім'ї")
async def family_info(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid: 
        await message.answer("❌ Ви не перебуваєте в сім'ї!")
        return

    family = db.get_family(fid)
    stats = db.get_ship_total_stats(fid)
    data = db.get_family_resources(fid)
    
    MAX = 10000 

    # Використовуємо HTML для створення ефекту спойлера <tg-spoiler> та копіювання <code>
    text = (
        f"🌌 <b>КАБІНЕТ СІМ'Ї: {family[1]}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 <b>Код для вступу:</b> <tg-spoiler><code>{family[2]}</code></tg-spoiler>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Характеристики корабля:</b>\n"
        f"🚀 Швидкість: <b>{stats['speed']}</b>\n"
        f"🛡️ Захист: <b>{stats['armor']}</b>\n"
        f"🌬️ Аеро: <b>{stats['aerodynamics']}</b>\n"
        f"🕹️ Маневр: <b>{stats['handling']}</b>\n"
        f"⚔️ Урон: <b>{stats['damage']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Склад ресурсів:</b>\n"
        f"🔩 Залізо: <b>{data[1]}/{MAX}</b> | ⛽ Паливо: <b>{data[2]}/{MAX}</b>\n"
        f"🌑 Реголіт: <b>{data[3]}/{MAX}</b> | ⚛️ Гелій-3: <b>{data[4]}/{MAX}</b>\n"
        f"💾 Кремній: <b>{data[5]}/{MAX}</b> | 🧪 Оксид: <b>{data[6]}/{MAX}</b>\n"
        f"🌫 Водень: <b>{data[7]}/{MAX}</b> | 🎈 Гелій: <b>{data[8]}/{MAX}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Баланс: <b>{data[0]}</b> монет\n"
        f"🌍 Локація: <b>{data[11]}</b>"
    )
    # Обов'язково вказуємо parse_mode="HTML"
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🛸 Ангар (Веб)")
async def open_webapp(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid: 
        await message.answer("Спочатку створіть сім'ю або приєднайтеся до неї!")
        return

    res = db.get_family_resources(fid)
    info = db.get_family_info(fid)

    params = {
        "family_id": fid,
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
    
    url = f"{WEB_APP_URL}?{urllib.parse.urlencode(params)}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🖥 Відкрити термінал", web_app=WebAppInfo(url=url))
    
    await message.answer(
        f"🚀 **Термінал доступу активовано**\nКоманда: {info[0]}", 
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )


# === ПІДТВЕРДЖЕННЯ ДЛЯ ВИХОДУ З СІМ'Ї ===

@router.message(F.text == "❌ Покинути сім'ю")
async def ask_leave_family(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid:
        await message.answer("❌ Ви не перебуваєте в сім'ї.")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Так, покинути", callback_data="confirm_leave")
    kb.button(text="❌ Скасувати", callback_data="cancel_leave")

    await message.answer(
        "⚠️ **Ви дійсно хочете покинути сім'ю?**\n"
        "Ви втратите доступ до спільної бази, лабораторії та ресурсів.",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "cancel_leave")
async def cancel_leave_action(call: CallbackQuery):
    await call.message.edit_text("✅ Дію скасовано. Ви залишаєтесь у сім'ї! 🚀")
    await call.answer()

@router.callback_query(F.data == "confirm_leave")
async def execute_leave_action(call: CallbackQuery):
    db.leave_family(call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        "🚪 Ви успішно покинули сім'ю. Тепер ви вільний вовк!", 
        reply_markup=get_main_kb_no_family()
    )
    await call.answer()