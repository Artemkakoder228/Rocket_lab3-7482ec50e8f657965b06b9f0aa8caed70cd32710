import asyncio
from datetime import datetime, timedelta
from contextlib import suppress
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from database import Database

router = Router()
db = Database()

# --- КОНСТАНТИ ---
BASE_MINE_RATE = 0.08 
SHIELD_PRICE = 1000

RES_ICONS = {
    "res_iron": "🔩", "res_fuel": "⛽",
    "res_regolith": "🌑", "res_he3": "⚛️",
    "res_silicon": "💾", "res_oxide": "🧪",
    "res_hydrogen": "🎈", "res_helium": "🌌"
}

# --- НОВА ФУНКЦІЯ РОЗРАХУНКУ (ЗАЛЕЖИТЬ ВІД ПЛАНЕТИ) ---
def get_upgrade_cost(planet, current_lvl):
    next_lvl = current_lvl + 1
    coins = 500 * next_lvl
    minutes = 5 * next_lvl
    
    # Вимагаємо ресурс тієї планети, де будується шахта
    if planet == 'Earth':
        r_type, r_name, amt = "res_iron", "Залізо", 200 * next_lvl
    elif planet == 'Moon':
        r_type, r_name, amt = "res_regolith", "Реголіт", 150 * next_lvl
    elif planet == 'Mars':
        r_type, r_name, amt = "res_silicon", "Кремній", 100 * next_lvl
    elif planet == 'Jupiter':
        r_type, r_name, amt = "res_hydrogen", "Водень", 50 * next_lvl
    else:
        r_type, r_name, amt = "res_iron", "Залізо", 200 * next_lvl
        
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

    planet = data[11]
    upgrade_end = timers[3]
    
    # ОТРИМУЄМО ДАНІ ШАХТИ ДЛЯ ПОТОЧНОЇ ПЛАНЕТИ
    mine_info = db.get_mine_info(fid, planet)
    mine_lvl = mine_info[0] if mine_info else 0
    
    is_upgrading = False
    
    if upgrade_end:
        now = datetime.now()
        if now < upgrade_end:
            is_upgrading = True
            diff = upgrade_end - now
            mm, ss = divmod(diff.seconds, 60)
            hh = diff.seconds // 3600
            time_str = f"{hh}:{mm:02d}:{ss:02d}" if hh > 0 else f"{mm:02d}:{ss:02d}"
            finish_time = upgrade_end.strftime("%H:%M")
            status_text = f"🚧 **Модернізація до {finish_time}**"
            btn_text = f"⏳ {time_str} (Оновити)"
        else:
            status_text = "🟢 **Готово до запуску!**"
            btn_text = "🎉 ЗАВЕРШИТИ" 
    else:
        status_text = "✅ **Штатний режим**"

    text = (
        f"🏭 **ІНФРАСТРУКТУРА ({planet})**\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⛏ Рівень шахти: **{mine_lvl}**\n"
        f"⚙️ Статус: {status_text}\n"
        f"━━━━━━━━━━━━━━━━\n"
    )

    kb = InlineKeyboardBuilder()

    if upgrade_end and datetime.now() > upgrade_end:
        kb.button(text="🎉 ЗАВЕРШИТИ БУДІВНИЦТВО", callback_data="upgrade_finish")
        kb.adjust(1)
    elif is_upgrading:
        kb.button(text=btn_text, callback_data="refresh_timer")
        text += f"\n_Роботи завершаться через {time_str}_"
        kb.adjust(1)
    else:
        # Передаємо планету в калькулятор
        c_coins, c_time, r_code, r_name, r_amt = get_upgrade_cost(planet, mine_lvl)
        r_icon = RES_ICONS.get(r_code, "📦")

        # Додаємо дві кнопки для збору ресурсів
        kb.button(text="📥 Зібрати (Поточна)", callback_data="collect_resources")
        kb.button(text="🌍 Зібрати з УСІХ планет", callback_data="collect_all_resources")
        
        kb.button(
            text=f"⬆️ Lvl {mine_lvl+1} (💰{c_coins}  {r_icon} {r_amt}  ⏳{c_time}хв)", 
            callback_data="upgrade_start"
        )
        kb.button(text="🛡 Щит", callback_data="shield_menu")

        # Вирівнюємо кнопки: 2 зверху (для збору), 1 по центру (прокачка), 1 знизу (щит)
        kb.adjust(2, 1, 1)

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
    planet = data[11]
    mine_info = db.get_mine_info(fid, planet)
    mine_lvl = mine_info[0]

    coins, time_min, r_type, r_name, r_amt = get_upgrade_cost(planet, mine_lvl)
    
    cur_coins = data[0]
    res_map = {"res_iron": 1, "res_fuel": 2, "res_regolith": 3, "res_he3": 4, "res_silicon": 5, "res_oxide": 6, "res_hydrogen": 7, "res_helium": 8}
    res_idx = res_map.get(r_type, 1)
    cur_res = data[res_idx]

    if cur_coins < coins or cur_res < r_amt:
        return await call.answer(f"❌ Треба {coins} монет та {r_amt} {r_name}", show_alert=True)

    db.deduct_resources(fid, coins, r_type, r_amt)
    db.set_upgrade_timer(fid, time_min)

    await call.answer(f"✅ Будівництво почато! ({time_min} хв)")
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "upgrade_finish")
async def upgrade_finish_handler(call: types.CallbackQuery):
    fid = db.get_user_family(call.from_user.id)
    # Звертаємось до функції і вона сама підтягне поточну планету
    db.finish_upgrade(fid)
    await call.answer("🎉 Шахту покращено!")
    await render_infra_menu(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "collect_resources")
async def collect_res_handler(call: types.CallbackQuery):
    fid = db.get_user_family(call.from_user.id)
    data = db.get_family_resources(fid)
    planet = data[11]
    
    mine_info = db.get_mine_info(fid, planet)
    mine_lvl = mine_info[0]
    last_col = mine_info[1]

    if not last_col: last_col = datetime.now()
    diff = (datetime.now() - last_col).total_seconds() / 60
    
    # Збільшуємо мінімальний час до 5 хвилин, щоб не спамили кнопку
    if diff < 5:
        return await call.answer("⏳ Шахта працює... Збирати ресурси можна не частіше ніж раз на 5 хвилин.", show_alert=True)

    # Новий розрахунок на основі дробового коефіцієнта
    amount = int(diff * mine_lvl * BASE_MINE_RATE)
    
    if amount <= 0:
        return await call.answer("📦 Нових ресурсів поки не видобуто. Зачекайте ще.", show_alert=True)

    if planet == "Moon": 
        r1, r2, n1, n2, i1, i2 = "res_regolith", "res_he3", "Реголіт", "Гелій-3", "🌑", "⚛️"
    elif planet == "Mars": 
        r1, r2, n1, n2, i1, i2 = "res_silicon", "res_oxide", "Кремній", "Оксид", "💾", "🧪"
    elif planet == "Jupiter": 
        r1, r2, n1, n2, i1, i2 = "res_hydrogen", "res_helium", "Водень", "Гелій", "🎈", "🌌"
    else: 
        r1, r2, n1, n2, i1, i2 = "res_iron", "res_fuel", "Залізо", "Паливо", "🔩", "⛽"

    # Перевірка, чи склади вже були повністю забиті ДО збору
    res_map = {"res_iron": 1, "res_fuel": 2, "res_regolith": 3, "res_he3": 4, "res_silicon": 5, "res_oxide": 6, "res_hydrogen": 7, "res_helium": 8}
    cur_r1 = data[res_map.get(r1, 1)]
    cur_r2 = data[res_map.get(r2, 2)]

    if cur_r1 >= 10000 and cur_r2 >= 10000:
        return await call.answer("⚠️ Ваші склади переповнені (10 000 / 10 000)! Витратьте ресурси.", show_alert=True)

    # Передаємо в БД (вона сама обріже зайве, якщо сума перевищить 10000)
    db.collect_resources(fid, planet, r1, amount, r2, amount)
    
    await call.answer(
        f"✅ Зібрано на {planet}:\n"
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

@router.callback_query(F.data == "collect_all_resources")
async def collect_all_handler(call: types.CallbackQuery):
    fid = db.get_user_family(call.from_user.id)
    
    # Словник з даними планет для циклу
    planets_data = {
        "Earth": ("res_iron", "res_fuel", "🔩", "⛽"),
        "Moon": ("res_regolith", "res_he3", "🌑", "⚛️"),
        "Mars": ("res_silicon", "res_oxide", "💾", "🧪"),
        "Jupiter": ("res_hydrogen", "res_helium", "🎈", "🌌")
    }
    
    collected_msg = "✅ Звіт по видобутку:\n"
    total_collected = False
    
    for planet, res in planets_data.items():
        mine_info = db.get_mine_info(fid, planet)
        if not mine_info: continue
        
        mine_lvl = mine_info[0]
        if mine_lvl == 0: continue # Пропускаємо, якщо шахту ще не побудовано
        
        last_col = mine_info[1] or datetime.now()
        diff = (datetime.now() - last_col).total_seconds() / 60
        
        if diff >= 5: # Збираємо тільки якщо пройшло більше 5 хвилин
            amount = int(diff * mine_lvl * BASE_MINE_RATE)
            if amount > 0:
                r1, r2, i1, i2 = res
                
                # Записуємо в БД (вона сама обріже зайве, якщо сума перевищить 10 000)
                db.collect_resources(fid, planet, r1, amount, r2, amount)
                
                # Додаємо рядок до звіту
                collected_msg += f"\n📍 {planet}: +{amount}{i1} | +{amount}{i2}"
                total_collected = True
                
    if total_collected:
        # Показуємо спливаюче вікно з красивим звітом
        await call.answer(collected_msg, show_alert=True)
        # Оновлюємо меню, щоб скинути таймер поточної планети на екрані
        await render_infra_menu(call.message, call.from_user.id, is_edit=True)
    else:
        await call.answer("⏳ Шахти працюють... Нових ресурсів ще не накопичилося (мінімум 5 хв).", show_alert=True)