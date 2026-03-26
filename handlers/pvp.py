from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from datetime import datetime
import random, asyncio

router = Router()
db = Database('space.db')
TACTICS = {
    "agg": {"n": "Атака", "b": "man", "e": "🔴"},
    "man": {"n": "Маневр", "b": "def", "e": "🔵"},
    "def": {"n": "Захист", "b": "agg", "e": "🟢"}
}


@router.message(F.text == "⚔️ Рейд")
async def raid_menu(message: types.Message):
    fid = db.get_user_family(message.from_user.id)
    if not fid: return
    fam = db.get_family_info(fid)
    if fam[5] in ["Earth", "Moon"]:
        return await message.answer("🛡 **ЩИТ ПОЯСУ АСТЕРОЇДІВ**\nАтаки заборонені в цій зоні.")

    enemy = db.get_random_enemy(fid)
    if not enemy: return await message.answer("🔭 Немає цілей.")

    kb = InlineKeyboardBuilder()
    kb.button(text="🔴 Атака", callback_data=f"bat:{enemy[0]}:agg")
    kb.button(text="🔵 Маневр", callback_data=f"bat:{enemy[0]}:man")
    kb.button(text="🟢 Захист", callback_data=f"bat:{enemy[0]}:def")
    kb.adjust(1)
    await message.answer(f"🎯 Ціль: **{enemy[1]}**\nСила: {db.get_family_power(enemy[0])}", reply_markup=kb.as_markup(),
                         parse_mode="Markdown")


@router.callback_query(F.data.startswith("bat:"))
async def battle(cb: types.CallbackQuery):
    _, eid, my_tac = cb.data.split(":")
    my_fid = db.get_user_family(cb.from_user.id)
    db.set_raid_cooldown(my_fid, 60)

    en_tac = random.choice(["agg", "man", "def"])
    bonus = 20 if TACTICS[my_tac]["b"] == en_tac else (-10 if TACTICS[en_tac]["b"] == my_tac else 0)

    await cb.message.edit_text(f"⚔️ {TACTICS[my_tac]['e']} VS {TACTICS[en_tac]['e']}")
    await asyncio.sleep(2)

    mp = db.get_family_power(my_fid)
    ep = db.get_family_power(int(eid))
    chance = max(5, min(95, 50 + (mp - ep) * 5 + bonus))

    if random.randint(1, 100) <= chance:
        loot = int(db.get_family_resources(int(eid))[0] * 0.15)
        db.deduct_resources(int(eid), loot)
        db.update_balance(my_fid, loot)
        db.set_shield(int(eid), 120)
        await cb.message.edit_text(f"🏆 Перемога! Вкрадено 💰{loot}")
    else:
        db.deduct_resources(my_fid, 100)
        await cb.message.edit_text(f"🔥 Поразка. Ремонт -100💰")