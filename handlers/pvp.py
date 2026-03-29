from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from database import Database
from config import WEB_APP_URL

router = Router()
db = Database('space.db')

@router.message(F.text == "⚔️ Рейд")
async def open_raid_radar(message: types.Message):
    user_id = message.from_user.id
    family_id = db.get_user_family(user_id)
    
    if not family_id:
        await message.answer("❌ Тільки учасники сімей (команд) можуть брати участь у рейдах!")
        return

    # Посилання на наш новий радар
    url = f"{WEB_APP_URL}/raids.html?family_id={family_id}&user_id={user_id}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Відкрити Радар Рейдів", web_app=WebAppInfo(url=url))]
    ])
    
    await message.answer(
        "⚔️ **МІЖГАЛАКТИЧНІ РЕЙДИ**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Командування готує масштабне оновлення бойової системи!\n\n"
        "Відкрийте тактичний радар, щоб слідкувати за переміщенням ворожих флотів.", 
        parse_mode="Markdown", 
        reply_markup=kb
    )