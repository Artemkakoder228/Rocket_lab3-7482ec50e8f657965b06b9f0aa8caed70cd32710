from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database

router = Router()
db = Database('space.db')

# Список усіх планет у грі та їх опис
ALL_PLANETS = {
    "Earth": {"icon": "🌍", "name": "Земля", "res": "Залізо, Паливо"},
    "Moon": {"icon": "🌑", "name": "Місяць", "res": "Реголіт, Гелій-3"},
    "Mars": {"icon": "🔴", "name": "Марс", "res": "Кремній, Оксид"},
    "Jupiter": {"icon": "⚡", "name": "Юпітер", "res": "Водень, Гелій"}
}

@router.message(F.text == "🚀 Навігація")
async def navigation_menu(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid:
        return await message.answer("Спочатку створіть сім'ю!")

    # Отримуємо дані
    fam = db.get_family_info(fid) # fam[5] = current_planet
    current_planet = fam[5]
    
    # Отримуємо список розблокованих
    unlocked = db.get_unlocked_planets(fid)

    text = (
        f"🗺 **ЗОРЯНА МАПА**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 Поточна локація: **{ALL_PLANETS.get(current_planet, {}).get('name', current_planet)}**\n"
        f"🔓 Відкрито секторів: **{len(unlocked)}/{len(ALL_PLANETS)}**\n\n"
        f"Оберіть планету для перельоту:"
    )

    kb = InlineKeyboardBuilder()

    for p_code, p_data in ALL_PLANETS.items():
        name = p_data['name']
        icon = p_data['icon']
        
        if p_code == current_planet:
            # Кнопка поточної планети (неактивна візуально)
            btn_text = f"✅ {icon} {name} (Тут)"
            callback = "nav_stay"
        elif p_code in unlocked:
            # Кнопка доступної планети
            btn_text = f"✈️ {icon} {name}"
            callback = f"nav_to_{p_code}"
        else:
            # Кнопка заблокованої планети
            btn_text = f"🔒 {icon} {name} (Закрито)"
            callback = "nav_locked"
            
        kb.button(text=btn_text, callback_data=callback)

    kb.adjust(1)
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")


# --- ОБРОБКА КЛІКІВ ---

@router.callback_query(F.data.startswith("nav_to_"))
async def travel_handler(call: types.CallbackQuery):
    target_planet = call.data.split("_")[2]
    fid = db.get_user_family(call.from_user.id)
    
    # Перевірка безпеки (чи справді розблоковано?)
    unlocked = db.get_unlocked_planets(fid)
    
    if target_planet not in unlocked:
        return await call.answer("❌ Доступ заборонено! Виконайте сюжетну місію.", show_alert=True)
    
    # Переліт
    db.travel_to_planet(fid, target_planet)
    
    p_name = ALL_PLANETS[target_planet]['name']
    await call.message.edit_text(
        f"🚀 **ГІПЕРСТРИБОК ЗАВЕРШЕНО**\n\n"
        f"Ви прибули на орбіту: **{p_name}**.\n"
        f"Шахти переналаштовано на видобуток місцевих ресурсів.",
        parse_mode="Markdown"
    )
    # Оновлюємо меню після перельоту
    # await navigation_menu(call.message) # Можна викликати знову, якщо треба

@router.callback_query(F.data == "nav_locked")
async def locked_handler(call: types.CallbackQuery):
    await call.answer("🔒 Планета недоступна.\nПроходьте 'Бос-місії' у розділі Місій, щоб отримати координати.", show_alert=True)

@router.callback_query(F.data == "nav_stay")
async def stay_handler(call: types.CallbackQuery):
    await call.answer("📍 Ви вже знаходитесь тут.", show_alert=False)