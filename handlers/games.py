from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from config import WEB_APP_URL
import random
import asyncio

router = Router()
db = Database('space.db')

@router.message(F.text == "🎲 Розваги")
async def menu(msg: types.Message):
    user_id = msg.from_user.id
    fid = db.get_user_family(user_id)
    
    if not fid:
        await msg.answer("❌ Для доступу до розваг потрібно перебувати в сім'ї!")
        return

    fortune_url = f"{WEB_APP_URL}/fortune.html?family_id={fid}&user_id={user_id}"

    kb = InlineKeyboardBuilder()
    kb.button(text="🎡 Колесо Фортуни", web_app=WebAppInfo(url=fortune_url))
    kb.button(text="🎰 Казино: 100 🪙", callback_data="slot:100")
    kb.button(text="🎰 Казино: 1000 🪙", callback_data="slot:1000")
    
    kb.adjust(1, 2)

    await msg.answer(
        "🎪 **ЦЕНТР РОЗВАГ**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Оберіть гру:\n\n"
        "🎡 **Колесо Фортуни** — безкоштовна щоденна лотерея.\n"
        "🎰 **Казино** — ризикуй монетами та вигравай джекпот!", 
        reply_markup=kb.as_markup(), 
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("slot:"))
async def play(cb: types.CallbackQuery):
    bet = int(cb.data.split(":")[1])
    fid = db.get_user_family(cb.from_user.id)
    
    if db.get_family_resources(fid)[0] < bet: 
        await cb.answer("❌ Недостатньо монет для ставки!", show_alert=True)
        return

    # Знімаємо гроші одразу перед початком прокрутки
    db.deduct_resources(fid, bet)
    await cb.answer() # Прибираємо стан "завантаження" з кнопки
    
    # Відправляємо початкове повідомлення з "крутілками"
    spin_msg = await cb.message.answer(
        f"🎰 **СЛОТИ** (Ставка: {bet} 🪙)\n"
        f"━━━━━━━━━━\n"
        f"| 🌀 | 🌀 | 🌀 |\n"
        f"━━━━━━━━━━\n"
        f"🔄 Обертання...",
        parse_mode="Markdown"
    )

    sym = ["🍒", "🍋", "🍉", "🔔", "💎", "7️⃣"]
    
    # Створюємо ефект обертання (змінюємо повідомлення 3 рази з паузою)
    for _ in range(3):
        await asyncio.sleep(0.5)
        t1, t2, t3 = random.choice(sym), random.choice(sym), random.choice(sym)
        try:
            await spin_msg.edit_text(
                f"🎰 **СЛОТИ** (Ставка: {bet} 🪙)\n"
                f"━━━━━━━━━━\n"
                f"| {t1} | {t2} | {t3} |\n"
                f"━━━━━━━━━━\n"
                f"🔄 Обертання...",
                parse_mode="Markdown"
            )
        except Exception:
            pass # Ігноруємо помилки, якщо повідомлення не встигло оновитися

    await asyncio.sleep(0.5)
    
    # Генеруємо фінальний результат
    r1, r2, r3 = random.choice(sym), random.choice(sym), random.choice(sym)
    
    win = 0
    # Якщо випали всі три однакові
    if r1 == r2 == r3:
        if r1 == "7️⃣":
            win = bet * 50    # Супер-Джекпот
        elif r1 == "💎":
            win = bet * 20    # Великий виграш
        else:
            win = bet * 10    # Стандартні 3 в ряд
    # Якщо випали два поруч (шанс набагато менший, ніж будь-які два)
    elif r1 == r2 or r2 == r3:
        win = int(bet * 1.5)

    # Нараховуємо виграш
    if win > 0: 
        db.update_balance(fid, win)
        if win >= bet * 10:
            res_text = f"🔥 ДЖЕКПОТ! Виграш: +{win} 🪙"
        else:
            res_text = f"✨ Виграш: +{win} 🪙"
    else:
        res_text = "💨 Пусто, пощастить наступного разу!"
        
    # Виводимо фінальний результат
    try:
        await spin_msg.edit_text(
            f"🎰 **СЛОТИ** (Ставка: {bet} 🪙)\n"
            f"━━━━━━━━━━\n"
            f"| {r1} | {r2} | {r3} |\n"
            f"━━━━━━━━━━\n"
            f"{res_text}",
            parse_mode="Markdown"
        )
    except Exception:
        pass