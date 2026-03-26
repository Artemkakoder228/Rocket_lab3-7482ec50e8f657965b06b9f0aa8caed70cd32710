from aiogram import Router, F, types
from database import Database

router = Router()
db = Database('space.db')

@router.message(F.text == "🎁 Вітальний бонус")
async def get_bonus(message: types.Message):
    user_id = message.from_user.id
    fid = db.get_user_family(user_id)
    
    if not fid:
        return await message.answer("❌ Спочатку вступіть у сім'ю!")

    # Викликаємо метод нарахування з оновленого database.py
    if db.claim_bonus(fid, 1000):
        await message.answer(
            f"🎉 **БОНУС ОТРИМАНО!**\n\n"
            f"У базу завантажено:\n"
            f"📦 **+1000 кожного ресурсу**\n\n"
            f"Тепер ви готові до перших польотів!",
            parse_mode="Markdown"
        )
    else:
        await message.answer("🚫 Ваша сім'я вже отримала цей бонус.")