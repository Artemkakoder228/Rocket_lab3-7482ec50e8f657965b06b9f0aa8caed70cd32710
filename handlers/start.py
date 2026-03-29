from aiogram import Router, types, F
from aiogram.filters import Command
from database import Database
from keyboards import get_main_kb_no_family, get_main_kb_with_family
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from config import WEB_APP_URL

router = Router()
db = Database('space.db')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "SpaceTraveller"

    db.add_user(user_id, username)
    family_id = db.get_user_family(user_id)

    if family_id:
        info = db.get_family_info(family_id)
        # info: 0=name, ..., 5=planet

        text = (
            f"🟢 **СИСТЕМА ІДЕНТИФІКАЦІЇ: УСПІХ**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пілот: **{username}**\n"
            f"🚀 Екіпаж: **{info[0]}**\n"
            f"📍 Поточна база: **{info[5]}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Очікую ваших вказівок через бортовий комп'ютер 👇"
        )
        await message.answer(text, parse_mode="Markdown", reply_markup=get_main_kb_with_family())
    else:
        text = (
            f"🌌 **ЛАСКАВО ПРОСИМО ДО ROCKET LAB** 🌌\n\n"
            f"Ви — новий учасник космічної програми. Ваша мета — підкорити Сонячну систему, від Землі до Юпітера.\n\n"
            f"⚠️ **ВАЖЛИВО:** Одинакам тут не вижити. Вам потрібно:\n"
            f"1️⃣ Створити власну космічну сім'ю (екіпаж).\n"
            f"2️⃣ Або приєднатися до друзів за кодом.\n\n"
            f"👇 **Оберіть дію для початку:**"
        )
        await message.answer(text, parse_mode="Markdown", reply_markup=get_main_kb_no_family())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Допомога")
async def cmd_help(message: types.Message):
    text = (
        "📘 **БОРТОВИЙ ЖУРНАЛ: ІНСТРУКЦІЯ**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 **МІСІЇ**\n"
        "Відправляйте ракети за ресурсами. Увага на **Ризик** (☠️)! Якщо ризик високий, на вас можуть напасти пірати. Качайте **Корпус**, щоб захиститись.\n\n"
        "🏭 **ІНФРАСТРУКТУРА**\n"
        "Будуйте шахти для пасивного видобутку. Ресурси потрібні для крафту та польотів.\n\n"
        "⚔️ **ВІЙНА (PvP)**\n"
        "На Марсі та Юпітері немає законів. Ви можете атакувати інші сім'ї та грабувати їхні склади. Використовуйте тактику!\n\n"
        "🛸 **АНГАР (WEB)**\n"
        "Натисніть кнопку «Ангар», щоб відкрити візуальний термінал керування.\n\n"
        "🛒 **МАГАЗИН**\n"
        "Тут можна покращити двигун (швидкість/атака) та корпус (захист)."
    )
    # Тут використовуємо answer, бо це довідка, яку користувач хоче бачити окремо
    await message.answer(text, parse_mode="Markdown")

# Переконайтеся, що імпортували db: from database import db (або Database)

@router.message(F.text == "🔬 Лабораторія")
async def open_research_lab(message: types.Message):
    user_id = message.from_user.id
    family_id = db.get_user_family(user_id)
    
    if not family_id:
        await message.answer("❌ Для доступу до лабораторії потрібна сім'я!")
        return
        
    # Отримуємо список відкритих планет (наприклад: ['Earth', 'Mars'])
    unlocked_planets = db.get_unlocked_planets(family_id)
    
    buttons = []
    # Генеруємо кнопку для кожної відкритої планети
    for planet in unlocked_planets:
        url = f"{WEB_APP_URL}/lab.html?family_id={family_id}&planet={planet}&user_id={user_id}"
        buttons.append([InlineKeyboardButton(text=f"🔬 Лабораторія: {planet}", web_app=WebAppInfo(url=url))])
        
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(
        "🔬 **ДОСЛІДНИЦЬКИЙ ЦЕНТР**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Оберіть філію лабораторії. Доступні лише ті планети, які ви вже дослідили:", 
        parse_mode="Markdown", 
        reply_markup=kb
    )