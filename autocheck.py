import asyncio
import random
import httpx
from database import Database
from aiogram import Bot

# Ланцюжок планет
PLANET_NEXT = {"Earth": "Moon", "Moon": "Mars", "Mars": "Jupiter", "Jupiter": "Earth"}
db = Database('space.db')

async def start_autocheck(bot: Bot):
    print("✅ Autocheck: Запущено фоновий процес...")
    
    # ЗАПУСК ПІНГЕРА: створюємо фонове завдання, щоб воно працювало паралельно з циклом перевірок
    asyncio.create_task(keep_alive_ping())
    
    while True:
        try:
            # Перевірка оновлень та місій
            await check_upg(bot)
            await check_mis(bot)
        except Exception as e:
            print(f"❌ CRITICAL ERROR in Autocheck: {e}")
        
        await asyncio.sleep(5) 

async def keep_alive_ping():
    """Функція для запобігання 'засинанню' сервера на Render"""
    url = "https://rocket-lab2.onrender.com"
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Надсилаємо GET-запит на головну сторінку
                response = await client.get(url)
                print(f"✅ Ping: {url} | Статус: {response.status_code}")
            except Exception as e:
                print(f"❌ Помилка пінгу: {e}")
            
            # Чекаємо 10 хвилин (600 секунд)
            await asyncio.sleep(600)

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
        db.finish_upgrade(fid)
        await notify(bot, fid, "🏭 **БУДІВНИЦТВО ЗАВЕРШЕНО!**\nШахту успішно модернізовано.")

async def check_mis(bot):
    missions = db.get_expired_missions()
    for row in missions:
        fid, mid, lid, planet = row
        db.clear_mission_timer(fid)
        
        m = db.get_mission_by_id(mid)
        if not m:
            continue

        try:
            req_type = m[12] 
            req_val = m[13]
        except:
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
            msg = f"✅ **МІСІЯ ЗАВЕРШЕНА!**\n💰 Прибуток: **{m[4]}**"
            if m[6] and PLANET_NEXT.get(m[5]):
                next_p = PLANET_NEXT[m[5]]
                unlocked = db.get_unlocked_planets(fid)
                if next_p not in unlocked:
                    db.unlock_planet(fid, next_p)
                    msg += f"\n\n🎉 **ВІДКРИТО НОВИЙ СЕКТОР: {next_p}!**"
        else:
            msg = f"💥 **МІСІЯ ПРОВАЛЕНА!**{fail_msg}"

        await notify(bot, fid, msg)