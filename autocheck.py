import asyncio
import random
from database import Database
from aiogram import Bot

# Ланцюжок розблокування планет
PLANET_NEXT = {"Earth": "Moon", "Moon": "Mars", "Mars": "Jupiter", "Jupiter": "Earth"}
db = Database('space.db')

async def start_autocheck(bot: Bot):
    print("✅ Autocheck: Запущено фоновий процес...")
    
    while True:
        try:
            # Перевірка оновлень та місій
            await check_upg(bot)
            await check_mis(bot)
        except Exception as e:
            print(f"❌ CRITICAL ERROR in Autocheck: {e}")
        
        await asyncio.sleep(5) 

async def notify(bot: Bot, fid, txt):
    users = db.get_family_user_ids(fid)
    if not users:
        return

    for uid in users:
        try:
            await bot.send_message(uid, txt, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Помилка надсилання {uid}: {e}")

async def check_upg(bot):
    upgrades = db.get_expired_upgrades()
    for row in upgrades:
        fid = row[0]
        planet = row[1] # Отримуємо планету, де будувалася шахта
        
        # Завершуємо апгрейд саме для цієї планети
        db.finish_upgrade(fid, planet)
        await notify(bot, fid, f"🏭 **БУДІВНИЦТВО ЗАВЕРШЕНО!**\nШахту на планеті **{planet}** успішно модернізовано.")

async def check_mis(bot):
    missions = db.get_expired_missions()
    for row in missions:
        fid, mid, lid, current_planet = row
        db.clear_mission_timer(fid)
        
        m = db.get_mission_by_id(mid)
        if not m:
            continue

        try:
            req_type = m[12] 
            req_val = m[13]
        except IndexError:
            req_type = 'speed'
            req_val = 0

        ship_stats = db.get_ship_total_stats(fid)
        current_val = ship_stats.get(req_type, 0)
        
        diff = req_val - current_val
        success = True
        fail_msg = ""

        if diff > 0:
            if diff >= 100: fail_chance = 90
            elif diff >= 50: fail_chance = 50
            else: fail_chance = 20
            
            if random.randint(1, 100) <= fail_chance:
                success = False
                fail_msg = f"\n⚠️ Недостатньо потужності: **{req_type}** {current_val}/{req_val}."

        if success:
            db.update_balance(fid, m[4])
            msg = f"✅ **МІСІЯ ЗАВЕРШЕНА!**\n💰 Прибуток: **{m[4]}** монет"
            
            is_boss = m[6]
            planet = m[5]
            
            # --- ЛОГІКА РОЗБЛОКУВАННЯ НОВОЇ ПЛАНЕТИ ---
            if is_boss and PLANET_NEXT.get(planet):
                next_p = PLANET_NEXT[planet]
                unlocked = db.get_unlocked_planets(fid)
                
                if next_p not in unlocked:
                    db.unlock_planet(fid, next_p)
                    msg += (f"\n\n🌌 **СЕКТОР ВІДКРИТО!**\n"
                            f"Ви успішно завершили фінальну місію планети {planet}!\n"
                            f"Тепер вашому кораблю доступні координати для стрибка на **{next_p}** 🚀\n"
                            f"Перейдіть у розділ Навігація.")
        else:
            msg = f"💥 **МІСІЯ ПРОВАЛЕНА!**{fail_msg}"

        await notify(bot, fid, msg)