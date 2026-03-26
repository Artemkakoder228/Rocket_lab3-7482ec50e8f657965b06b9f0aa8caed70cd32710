import asyncio
from datetime import datetime, timedelta
from contextlib import suppress
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from database import Database

router = Router()
db = Database('space.db')

# --- КОНСТАНТИ (БАЛАНС) ---
MINING_RATE = 2   # Було 10. Тепер 2 ресурси за хвилину на 1 рівні шахти.
SHIELD_PRICE = 1000 

# Словник з іконками для ресурсів
RES_ICONS = {
    "res_iron": "🔩",
    "res_fuel": "⛽",
    "res_regolith": "🌑",
    "res_he3": "⚛️",
    "res_silicon": "💾",
    "res_oxide": "🧪",
    "res_hydrogen": "🎈",
    "res_helium": "🌌"
}

# --- ФУНКЦІЯ РОЗРАХУНКУ ---
def get_upgrade_cost(current_lvl):
    next_lvl = current_lvl + 1
    
    # 1. Гроші: 500 * рівень
    coins = 500 * next_lvl
    
    # 2. Час: 5 хвилин * рівень
    minutes = 5 * next_lvl
    
    # 3. Ресурс: Змінюється кожні 3 рівні
    if current_lvl < 3:
        r_type, r_name, amt = "res_iron", "Залізо", 200 * next_lvl
    elif current_lvl < 6:
        r_type, r_name, amt = "res_fuel", "Паливо", 150 * next_lvl
    elif current_lvl < 9:
        r_type, r_name, amt = "res_regolith", "Реголіт", 100 * next_lvl
    else:
        r_type, r_name, amt = "res_he3", "Гелій-3", 50 * next_lvl
        
    return coins, minutes, r_type, r_name, amt


# --- ВІДОБРАЖЕННЯ МЕНЮ ---
async def render_infra_menu(target_msg: types.Message, user_id: int, is_edit: bool = False):
    fid = db.get_user_family(user_id)
    if not fid:
        if not is_edit: await target_msg.answer("Спочатку створіть сім'ю!")
        return

    data = db.get_family_resources(fid)
    timers = db.get_timers(fid)
    
    if not data: return

    mine_lvl = data[9]
    planet = data[11]
    upgrade_end = timers[3]
    
    # --- ЛОГІКА ТАЙМЕРА ---
    is_upgrading = False
    
    if upgrade_end:
        now = datetime.now()
        if now < upgrade_end:
            is_upgrading = True
            diff = upgrade_end - now
            mm, ss = divmod(diff.seconds, 60)
            hh = diff.seconds // 3600
            
            if hh > 0:
                time_str = f"{hh}:{mm:02d}:{ss:02d}"
            else:
                time_str = f"{mm:02d}:{ss:02d}"

            finish_time = upgrade_end.strftime("%H:%M")
            status_text = f"🚧 **Модернізація до {finish_time}**"
            btn_text = f"⏳ {time_str} (Оновити)"
        else:
            status_text = "🟢 **Готово до запуску!**"
            btn_text = "🎉 ЗАВЕРШИТИ" 
    else:
        status_text = "✅ **Штатний режим**"

    text = (
        f"🏭 **ІНФРАСТРУКТУРА**\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📍 База: **{planet}**\n"
        f"⛏ Рівень: **{mine_lvl}**\n"
        f"⚙️ Статус: {status_text}\n"
        f"━━━━━━━━━━━━━━━━\n"
    )

    kb = InlineKeyboardBuilder()

    if upgrade_end and datetime.now() > upgrade_end:
        kb.button(text="🎉 ЗАВЕРШИТИ БУДІВНИЦТВО", callback_data="upgrade_finish")
    
    elif is_upgrading:
        kb.button(text=btn_text, callback_data="refresh_timer")
        text += f"\n_Роботи завершаться через {time_str}_"

    else:
        c_coins, c_time, r_code, r_name, r_amt = get_upgrade_cost(mine_lvl)
        
        # Отримуємо іконку ресурсу
        r_icon = RES_ICONS.get(r_code, "📦")

        kb.button(text="📥 Зібрати ресурси", callback_data="collect_resources")
        # Формуємо кнопку з нормальним смайликом замість букви
        kb.button(
            text=f"⬆️ Lvl {mine_lvl+1} (💰{c_coins}  {r_icon} {r_amt}  ⏳{c_time}хв)", 
            callback_data="upgrade_start"
        )
        kb.button(text="🛡 Щит", callback_data="shield_menu")

    kb.adjust(1)

    if is_edit:
        with suppress(TelegramBadRequest):
            await target_msg.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    else:
        await target_msg.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")


# --- ХЕНДЛЕРИ ---

@router.message(F.text == "🏭 Інфраструктура")
async def infrastructure_cmd(message: types.Message):
    await render_infra_menu(message, message.from_user.id, is_edit=False)

@router.callback_query(F.data == "back_infra")
async def back_infra(call: types.CallbackQuery):
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "refresh_timer")
async def refresh_timer_handler(call: types.CallbackQuery):
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)
    await call.answer() 

@router.callback_query(F.data == "upgrade_start")
async def upgrade_start_handler(call: types.CallbackQuery):
    fid = db.get_user_family(call.from_user.id)
    data = db.get_family_resources(fid)
    mine_lvl = data[9]

    coins, time_min, r_type, r_name, r_amt = get_upgrade_cost(mine_lvl)
    
    cur_coins = data[0]
    res_map = {"res_iron": 1, "res_fuel": 2, "res_regolith": 3, "res_he3": 4}
    res_idx = res_map.get(r_type, 1)
    cur_res = data[res_idx]

    if cur_coins < coins or cur_res < r_amt:
        return await call.answer(f"❌ Треба {coins} монет та {r_amt} {r_name}", show_alert=True)

    db.deduct_resources(fid, coins, r_type, r_amt)
    db.set_upgrade_timer(fid, time_min)

    await call.answer(f"✅ Почали! ({time_min} хв)")
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "upgrade_finish")
async def upgrade_finish_handler(call: types.CallbackQuery):
    fid = db.get_user_family(call.from_user.id)
    db.finish_upgrade(fid)
    await call.answer("🎉 Шахту покращено!")
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "collect_resources")
async def collect_res_handler(call: types.CallbackQuery):
    fid = db.get_user_family(call.from_user.id)
    data = db.get_family_resources(fid)
    
    last_col = data[10]
    mine_lvl = data[9]
    planet = data[11]

    if not last_col: last_col = datetime.now()
    diff = (datetime.now() - last_col).total_seconds() / 60
    
    if diff < 1:
        return await call.answer("⏳ Рано! Ще накопичується (мін. 1 хв).", show_alert=True)

    amount = int(diff * mine_lvl * MINING_RATE)
    if amount <= 0:
        return await call.answer("Склади порожні.", show_alert=True)

    # Визначаємо типи ресурсів та їх назви/іконки для повідомлення
    if planet == "Moon": 
        r1, r2 = "res_regolith", "res_he3"
        n1, n2 = "Реголіт", "Гелій-3"
        i1, i2 = "🌑", "⚛️"
    elif planet == "Mars": 
        r1, r2 = "res_silicon", "res_oxide"
        n1, n2 = "Кремній", "Оксид"
        i1, i2 = "💾", "🧪"
    elif planet == "Jupiter": 
        r1, r2 = "res_hydrogen", "res_helium"
        n1, n2 = "Водень", "Гелій"
        i1, i2 = "🎈", "🌌"
    else: 
        r1, r2 = "res_iron", "res_fuel"
        n1, n2 = "Залізо", "Паливо"
        i1, i2 = "🔩", "⛽"

    db.collect_resources(fid, r1, amount, r2, amount)
    
    # Красиве повідомлення з іконками та назвами
    await call.answer(
        f"✅ Успішно зібрано:\n"
        f"+{amount} {i1} {n1}\n"
        f"+{amount} {i2} {n2}", 
        show_alert=True
    )
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "shield_menu")
async def shield_menu_handler(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"🛡 Купити (24г) - {SHIELD_PRICE}💰", callback_data="buy_shield")
    kb.button(text="🔙 Назад", callback_data="back_infra")
    kb.adjust(1)

    await call.message.edit_text(
        f"🛡 **Система 'ЕГІДА'**\n"
        f"Захист від атак на 24 години.", 
        reply_markup=kb.as_markup(), parse_mode="Markdown"
    )

@router.callback_query(F.data == "buy_shield")
async def buy_shield_handler(call: types.CallbackQuery):
    fid = db.get_user_family(call.from_user.id)
    res = db.get_family_resources(fid)
    if res[0] < SHIELD_PRICE: return await call.answer("❌ Брак коштів!", show_alert=True)

    db.deduct_resources(fid, SHIELD_PRICE)
    db.set_shield(fid, 1440) 

    await call.answer("✅ Щит увімкнено!", show_alert=True)
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)