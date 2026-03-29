from aiogram import Router, F, types
from database import Database
from aiogram.filters import Command
from aiogram.types import Message
router = Router(); db = Database('space.db')

@router.message(F.text == "!skip")
async def skip(m: types.Message):
    fid = db.get_user_family(m.from_user.id)
    if fid: db.admin_skip_timers(fid); await m.answer("⏩ Час пропущено")

@router.message(F.text == "!rich")
async def rich(m: types.Message):
    fid = db.get_user_family(m.from_user.id)
    if fid: db.admin_add_resources(fid); await m.answer("🤑 +Ресурси")

@router.message(Command("addquiz"))
async def admin_add_quiz(message: Message):
    # Формат: /addquiz Mars | Яка гора найвища? | Олімп | Еверест | Говерла | Афон | 1 | 1500
    try:
        args_text = message.text.split(maxsplit=1)[1]
        args = [x.strip() for x in args_text.split('|')]
        
        if len(args) != 8: # Тепер у нас 8 аргументів (додалася планета)
            raise ValueError
        
        planet, question, o1, o2, o3, o4, correct, reward = args
        db.add_quiz(planet, question, o1, o2, o3, o4, int(correct), int(reward))
        
        await message.answer(f"✅ Питання для планети {planet} успішно додано!\n\n❓ {question}\n💰 База: {reward} 🪙")
    except Exception as e:
        await message.answer(
            "❌ Помилка! Формат:\n`/addquiz Планета | Питання | Відповідь 1 | Відповідь 2 | Відповідь 3 | Відповідь 4 | Номер правильної (1-4) | Нагорода`",
            parse_mode="Markdown"
        )