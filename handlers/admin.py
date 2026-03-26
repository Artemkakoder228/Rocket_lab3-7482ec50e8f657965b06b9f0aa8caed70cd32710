from aiogram import Router, F, types
from database import Database
router = Router(); db = Database('space.db')

@router.message(F.text == "!skip")
async def skip(m: types.Message):
    fid = db.get_user_family(m.from_user.id)
    if fid: db.admin_skip_timers(fid); await m.answer("⏩ Час пропущено")

@router.message(F.text == "!rich")
async def rich(m: types.Message):
    fid = db.get_user_family(m.from_user.id)
    if fid: db.admin_add_resources(fid); await m.answer("🤑 +Ресурси")