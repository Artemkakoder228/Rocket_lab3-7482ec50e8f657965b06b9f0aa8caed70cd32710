from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import WebAppInfo, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from config import WEB_APP_URL
import urllib.parse
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from keyboards import get_main_kb_with_family, get_main_kb_no_family

router = Router()
db = Database('space.db')


class FamilyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_code = State()
    waiting_for_chat_msg = State()


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
    success, status = db.join_family(message.from_user.id, message.text.upper().strip())
    
    if success:
        await state.clear()
        await message.answer("Успіх! Ви приєдналися до сім'ї.", reply_markup=get_main_kb_with_family())
    elif status == "full":
        await message.answer("❌ Помилка. У цій сім'ї вже досягнуто ліміту учасників (4/4).")
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
    
    # Якщо даних про ресурси немає, створюємо пустий список з нулями
    if not data:
        data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Earth"]

    members = db.get_family_members(fid)
    members_count = len(members)
    
    members_list_text = ""
    for m in members:
        icon = "👑" if m[1] == 'captain' else "👨‍🚀"
        name = f"@{m[0]}" if m[0] else "Анонім"
        members_list_text += f"{icon} {name}\n"

    MAX = 100000
    text = (
        f"🌌 <b>КАБІНЕТ СІМ'Ї: {family[1]}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 <b>Код:</b> <code>{family[2]}</code>\n"
        f"👥 <b>Учасники ({members_count}/4):</b>\n"
        f"{members_list_text}"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Характеристики корабля:</b>\n"
        f"┣ 🚀 Швидкість: <b>{stats.get('speed', 0)}</b>\n"
        f"┣ 🌬️ Аеродинаміка: <b>{stats.get('aerodynamics', 0)}</b>\n"
        f"┣ 🕹️ Маневреність: <b>{stats.get('handling', 0)}</b>\n"
        f"┣ 🛡️ Захист (Броня): <b>{stats.get('armor', 0)}</b>\n"
        f"┗ ⚔️ Урон (Гармати): <b>{stats.get('damage', 0)}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Склад ресурсів:</b>\n"
        f"┣ 🔩 Залізо: <b>{data[1]}/{MAX}</b>\n"
        f"┣ ⛽ Паливо: <b>{data[2]}/{MAX}</b>\n"
        f"┣ 🌑 Реголіт: <b>{data[3]}/{MAX}</b>\n"
        f"┣ ⚛️ Гелій-3: <b>{data[4]}/{MAX}</b>\n"
        f"┣ 💾 Кремній: <b>{data[5]}/{MAX}</b>\n"
        f"┣🧪 Оксид: <b>{data[6]}/{MAX}</b>\n"
        f"┣ 🌫 Водень: <b>{data[7]}/{MAX}</b>\n"
        f"┗ 🎈 Гелій: <b>{data[8]}/{MAX}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Баланс: <b>{data[0]}</b> монет\n"
        f"🌍 Локація: <b>{data[11]}</b>"
    )
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

@router.message(F.text == "💬 Чат сім'ї")
async def open_family_chat(message: types.Message):
    # Спочатку перевіряємо, чи є користувач у сім'ї
    fid = db.get_user_family(message.from_user.id)
    if not fid:
        await message.answer("❌ Ви не перебуваєте в сім'ї!")
        return
        
    # Створюємо inline-кнопку і передаємо точні параметри в URL
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📱 Відкрити Чат", 
            web_app=WebAppInfo(url=f"{WEB_APP_URL}/chat.html?user_id={message.from_user.id}&family_id={fid}")
        )]
    ])
    
    await message.answer("Натисніть кнопку нижче, щоб увійти в захищений канал зв'язку вашої сім'ї:", reply_markup=kb)

@router.message(FamilyStates.waiting_for_chat_msg)
async def broadcast_family_message(message: types.Message, state: FSMContext):
    fid = db.get_user_family(message.from_user.id)
    text = message.text
    sender = message.from_user.username or message.from_user.first_name
    
    # Отримуємо ID всіх членів сім'ї
    member_ids = db.get_family_user_ids(fid)
    
    count = 0
    for m_id in member_ids:
        if m_id != message.from_user.id: # Не шлемо самому собі
            try:
                await message.bot.send_message(
                    m_id, 
                    f"💬 <b>[Чат Сім'ї] @{sender}:</b>\n{text}", 
                    parse_mode="HTML"
                )
                count += 1
            except:
                continue # Якщо бот заблокований
                
    await state.clear()
    await message.answer(f"✅ Повідомлення доставлено іншим учасникам ({count}).")