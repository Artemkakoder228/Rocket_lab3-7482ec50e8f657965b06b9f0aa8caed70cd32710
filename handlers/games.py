from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
import asyncio, random

router = Router()
db = Database('space.db')


@router.message(F.text == "🎲 Розваги")
async def menu(msg: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎰 100💰", callback_data="slot:100")
    kb.button(text="🎰 1000💰", callback_data="slot:1000")
    await msg.answer("🎰 **КАЗИНО**", reply_markup=kb.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("slot:"))
async def play(cb: types.CallbackQuery):
    bet = int(cb.data.split(":")[1])
    fid = db.get_user_family(cb.from_user.id)
    if db.get_family_resources(fid)[0] < bet: return await cb.answer("Брак грошей!")

    db.deduct_resources(fid, bet)
    sym = ["🍒", "🍋", "7️⃣"]
    r1, r2, r3 = random.choice(sym), random.choice(sym), random.choice(sym)

    win = 0
    if r1 == r2 == r3:
        win = bet * 10
    elif r1 == r2 or r2 == r3 or r1 == r3:
        win = int(bet * 1.5)

    if win: db.update_balance(fid, win)
    await cb.message.answer(f"| {r1} | {r2} | {r3} |\n{'🎉 Виграш: ' + str(win) if win else '💨 Пусто'}")