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
    # Тут має бути ваша перевірка на адміна, наприклад:
    # if message.from_user.id not in ADMIN_IDS: return

    # Формат: /addquiz Яка планета найбільша? | Марс | Земля | Юпітер | Венера | 3 | 500
    try:
        # Відрізаємо команду і ділимо текст по символу "|"
        args_text = message.text.split(maxsplit=1)[1]
        args = [x.strip() for x in args_text.split('|')]
        
        if len(args) != 7:
            raise ValueError
        
        question, o1, o2, o3, o4, correct, reward = args
        db.add_quiz(question, o1, o2, o3, o4, int(correct), int(reward))
        
        await message.answer(f"✅ Питання успішно додано!\n\n❓ {question}\n💰 Нагорода: {reward} монет")
    except Exception as e:
        await message.answer(
            "❌ Помилка! Правильний формат:\n"
            "`/addquiz Питання | Відповідь 1 | Відповідь 2 | Відповідь 3 | Відповідь 4 | Номер правильної (1-4) | Нагорода`\n\n"
            "Приклад:\n`/addquiz Скільки планет у Сонячній системі? | 7 | 8 | 9 | 10 | 2 | 1000`",
            parse_mode="Markdown"
        )