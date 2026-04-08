import psycopg2
import random
import string
import datetime
import threading
import os
from config import CATALOG

# ВАШЕ ПІДКЛЮЧЕННЯ ДО NEON
# (Я прибрав 'channel_binding=require', бо він іноді викликає помилки в Python, залишив тільки sslmode)
DATABASE_URL = "postgresql://neondb_owner:npg_1PhACa8zgNmd@ep-withered-fire-aiay68rh-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

class Database:
    def __init__(self, db_file=None):
        # Підключаємось до хмари Neon
        self.connection = psycopg2.connect(DATABASE_URL)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        self.lock = threading.Lock()
        self.create_tables()

    def create_tables(self):
        with self.connection:
            # 1. Таблиця Сім'ї (Баланс + Ресурси + Прогрес)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS families (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    invite_code TEXT UNIQUE,
                    balance INTEGER DEFAULT 1000,

                    -- Прогрес корабля
                    engine_lvl INTEGER DEFAULT 1,
                    hull_lvl INTEGER DEFAULT 1,
                    current_planet TEXT DEFAULT 'Earth',
                    unlocked_planets TEXT DEFAULT 'Earth',

                    -- Шахта та таймери
                    mine_lvl INTEGER DEFAULT 0,
                    last_collection TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    mission_end_time TIMESTAMP DEFAULT NULL,
                    active_launch_id INTEGER DEFAULT NULL,
                    active_mission_id INTEGER DEFAULT NULL,
                    upgrade_end_time TIMESTAMP DEFAULT NULL,

                    last_raid_time TIMESTAMP DEFAULT NULL,
                    shield_until TIMESTAMP DEFAULT NULL,

                    -- Ресурси
                    res_iron INTEGER DEFAULT 0,
                    res_fuel INTEGER DEFAULT 0,
                    res_regolith INTEGER DEFAULT 0,
                    res_he3 INTEGER DEFAULT 0,
                    res_silicon INTEGER DEFAULT 0,
                    res_oxide INTEGER DEFAULT 0,
                    res_hydrogen INTEGER DEFAULT 0,
                    res_helium INTEGER DEFAULT 0,
                    bonus_received BOOLEAN DEFAULT FALSE
                )
            """)

            # 2. Користувачі
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    family_id INTEGER DEFAULT NULL REFERENCES families(id) ON DELETE SET NULL,
                    role TEXT DEFAULT 'recruit'
                )
            """)

            self.cursor.execute("""
                 CREATE TABLE IF NOT EXISTS missions (
                     id SERIAL PRIMARY KEY,
                     name TEXT NOT NULL,
                     description TEXT,
                     difficulty INTEGER,
                     reward INTEGER,
                     planet TEXT DEFAULT 'Earth',
                     is_boss_mission BOOLEAN DEFAULT FALSE,
                     cost_money INTEGER DEFAULT 0,
                     req_res_name TEXT DEFAULT NULL,
                     req_res_amount INTEGER DEFAULT 0,
                     flight_time INTEGER DEFAULT 10,
                     pirate_risk INTEGER DEFAULT 10,
                     req_stat_type TEXT DEFAULT 'speed',  -- НОВА КОЛОНКА
                     req_stat_value INTEGER DEFAULT 0      -- НОВА КОЛОНКА
                )
            """)

            # 4. Запуски
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS launches (
                    id SERIAL PRIMARY KEY,
                    family_id INTEGER REFERENCES families(id),
                    mission_id INTEGER REFERENCES missions(id),
                    status TEXT DEFAULT 'pending',
                    signatures TEXT DEFAULT '',
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 5. Покупки (апгрейди)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS family_upgrades (
                    id SERIAL PRIMARY KEY,
                    family_id INTEGER REFERENCES families(id),
                    module_id TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 6. Історія покупок у магазині (Щоденна)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS shop_purchases (
                    id SERIAL PRIMARY KEY,
                    family_id INTEGER REFERENCES families(id),
                    item_id TEXT,
                    purchase_date DATE DEFAULT CURRENT_DATE
                )
            """)

            # Перестворюємо таблицю з колонкою planet
            # self.cursor.execute("DROP TABLE IF EXISTS quizzes")
            # Таблиця для питань лабораторії
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    id SERIAL PRIMARY KEY,
                    planet TEXT DEFAULT 'Earth',
                    question TEXT,
                    opt1 TEXT,
                    opt2 TEXT,
                    opt3 TEXT,
                    opt4 TEXT,
                    correct_opt INTEGER,
                    reward INTEGER
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS family_messages (
                    id SERIAL PRIMARY KEY,
                    family_id INTEGER REFERENCES families(id),
                    user_id BIGINT,
                    username TEXT,
                    text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        try:
                self.cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                self.cursor.execute("ALTER TABLE families ADD COLUMN IF NOT EXISTS under_attack_until TIMESTAMP")
                self.cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_fortune TIMESTAMP")
                self.connection.commit()
        except Exception:
                self.connection.rollback()
            # --- МЕТОДИ ---

    def create_family(self, user_id, family_name):
        import random
        import string
        
        invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        with self.connection:
            # ДОДАЄМО ПОЧАТКОВІ РЕСУРСИ (res_iron, res_fuel) ПРЯМО В ТАБЛИЦЮ families
            self.cursor.execute(
                "INSERT INTO families (name, invite_code, balance, res_iron, res_fuel) VALUES (%s, %s, 1000, 100, 100) RETURNING id",
                (family_name, invite_code)
            )
            family_id = self.cursor.fetchone()[0]
            
            # ДОДАЄМО ПОЧАТКОВІ МОДУЛІ В БД (щоб JS бачив їх як owned та працював requires)
            starting_modules = [
                # Земля
                'gu1', 'nc1', 'e1', 'a1',
                # Місяць
                'root1', 'root2', 'root3',
                # Марс
                'g1_1', 'g2_1', 'g3_a1', 'g3_b1',
                # Юпітер
                'hull_start', 'eng_start', 'nose_start', 'cannons'
            ]
            for m_id in starting_modules:
                self.cursor.execute(
                    "INSERT INTO family_upgrades (family_id, module_id) VALUES (%s, %s)",
                    (family_id, m_id)
                )
                
            self.cursor.execute(
                "UPDATE users SET family_id = %s, role = 'captain' WHERE user_id = %s",
                (family_id, user_id)
            )
            return invite_code

    def get_family_resources(self, family_id):
        with self.connection:
            self.cursor.execute("""
                SELECT 
                    balance, 
                    res_iron, res_fuel, res_regolith, res_he3, 
                    res_silicon, res_oxide, res_hydrogen, res_helium, 
                    mine_lvl, last_collection, current_planet 
                FROM families 
                WHERE id = %s
            """, (family_id,))
            return self.cursor.fetchone()

    def deduct_resources(self, family_id, money, res_name=None, res_amount=0):
        with self.connection:
            if money > 0:
                self.cursor.execute("UPDATE families SET balance = balance - %s WHERE id = %s", (money, family_id))
            
            if res_name and res_amount > 0:
                query = f"UPDATE families SET {res_name} = {res_name} - %s WHERE id = %s"
                self.cursor.execute(query, (res_amount, family_id))

    def collect_resources(self, family_id, planet, res1_col, amount1, res2_col, amount2):
        p = planet.lower()
        with self.connection:
            # Функція LEAST(x, 10000) бере менше з двох значень.
            # Якщо сума стане 10500, база запише рівно 10000.
            query = f"""
                UPDATE families 
                SET {res1_col} = LEAST({res1_col} + %s, 10000), 
                    {res2_col} = LEAST({res2_col} + %s, 10000), 
                    last_coll_{p} = CURRENT_TIMESTAMP 
                WHERE id = %s
            """
            self.cursor.execute(query, (amount1, amount2, family_id))

    def admin_add_resources(self, family_id):
        with self.connection:
            self.cursor.execute("""
                UPDATE families SET 
                balance = balance + 100000,
                res_iron = res_iron + 100000, res_fuel = res_fuel + 100000,
                res_regolith = res_regolith + 100000, res_he3 = res_he3 + 100000,
                res_silicon = res_silicon + 100000, res_oxide = res_oxide + 100000,
                res_hydrogen = res_hydrogen + 100000, res_helium = res_helium + 100000
                WHERE id = %s
            """, (family_id,))

    def claim_bonus(self, family_id, amount=100):
        with self.connection:
            self.cursor.execute("SELECT bonus_received FROM families WHERE id = %s", (family_id,))
            res = self.cursor.fetchone()
            if res and res[0]: 
                return False
            
            self.cursor.execute(f"""
                UPDATE families SET 
                res_iron = res_iron + %s, res_fuel = res_fuel + %s,
                res_regolith = res_regolith + %s, res_he3 = res_he3 + %s,
                res_silicon = res_silicon + %s, res_oxide = res_oxide + %s,
                res_hydrogen = res_hydrogen + %s, res_helium = res_helium + %s,
                bonus_received = TRUE
                WHERE id = %s
            """, (amount, amount, amount, amount, amount, amount, amount, amount, family_id))
            return True

    def user_exists(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            return bool(self.cursor.fetchone())

    def add_user(self, user_id, username):
        if not self.user_exists(user_id):
            with self.connection:
                self.cursor.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username))

    def get_ship_total_stats(self, family_id):
        with self.connection:
            self.cursor.execute("SELECT module_id FROM family_upgrades WHERE family_id = %s", (family_id,))
            owned_ids = [row[0] for row in self.cursor.fetchall()]

            total = {"speed": 0, "armor": 0, "aerodynamics": 0, "handling": 0, "damage": 0}

            from config import CATALOG 
            for m_id in owned_ids:
                if m_id in CATALOG:
                    stats = CATALOG[m_id].get('stats', {})
                    for s_name, s_val in stats.items():
                        if s_name in total:
                            total[s_name] += s_val
            return total

    def get_user_family(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT family_id FROM users WHERE user_id = %s", (user_id,))
            res = self.cursor.fetchone()
            return res[0] if res else None

    def get_family_mine_level(self, family_id, planet_name):
        """Отримує реальний рівень шахти сім'ї для поточної планети"""
        column_name = f"mine_lvl_{planet_name.lower()}"
        
        # Перевірка на всяк випадок, щоб не було SQL-ін'єкцій
        if planet_name.lower() not in ['earth', 'moon', 'mars', 'jupiter']:
            return 1
            
        with self.lock:
            with self.connection:
                try:
                    self.cursor.execute(f"SELECT COALESCE({column_name}, 1) FROM families WHERE id = %s", (family_id,))
                    res = self.cursor.fetchone()
                    return res[0] if res else 1
                except Exception as e:
                    self.connection.rollback()
                    print(f"Помилка отримання шахти: {e}")
                    return 1

    def join_family(self, user_id, invite_code):
        with self.connection:
            self.cursor.execute("SELECT id FROM families WHERE invite_code = %s", (invite_code,))
            family = self.cursor.fetchone()
            if family:
                fid = family[0]
                # Перевірка поточної кількості учасників
                self.cursor.execute("SELECT COUNT(*) FROM users WHERE family_id = %s", (fid,))
                count = self.cursor.fetchone()[0]
                
                if count >= 4:
                    return False, "full" # Повертаємо статус "повна сім'я"
                
                self.cursor.execute("UPDATE users SET family_id = %s WHERE user_id = %s", (fid, user_id))
                return True, "success"
            return False, "not_found"

    def get_family_info(self, family_id):
        with self.connection:
            self.cursor.execute(
                "SELECT name, invite_code, balance, engine_lvl, hull_lvl, current_planet FROM families WHERE id = %s",
                (family_id,))
            return self.cursor.fetchone()

    def get_family_members(self, family_id):
        with self.connection:
            self.cursor.execute("SELECT username, role FROM users WHERE family_id = %s", (family_id,))
            return self.cursor.fetchall()

    def leave_family(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET family_id = NULL, role = 'recruit' WHERE user_id = %s", (user_id,))

    def update_balance(self, family_id, amount):
        with self.connection:
            self.cursor.execute("UPDATE families SET balance = balance + %s WHERE id = %s", (amount, family_id))

    def move_family_to_planet(self, family_id, new_planet):
        with self.connection:
            self.cursor.execute("UPDATE families SET current_planet = %s, mine_lvl = 0 WHERE id = %s", (new_planet, family_id))

    def update_upgrade(self, family_id, upgrade_type):
        with self.connection:
            if upgrade_type not in ['engine_lvl', 'hull_lvl']: return
            query = f"UPDATE families SET {upgrade_type} = {upgrade_type} + 1 WHERE id = %s"
            self.cursor.execute(query, (family_id,))

    def add_mission(self, name, description, difficulty, reward, planet, is_boss, cost_money=0, req_res=None, req_amt=0, flight_time=10, pirate_risk=10, req_stat_type='speed', req_stat_value=0):
        with self.connection:
            self.cursor.execute("""
                INSERT INTO missions (name, description, difficulty, reward, planet, is_boss_mission, cost_money, req_res_name, req_res_amount, flight_time, pirate_risk, req_stat_type, req_stat_value) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, description, difficulty, reward, planet, is_boss, cost_money, req_res, req_amt, flight_time, pirate_risk,req_stat_type,req_stat_value))

    def get_missions_by_planet(self, planet):
        """Отримує всі місії для конкретної планети"""
        with self.connection:
            self.cursor.execute("SELECT * FROM missions WHERE planet = %s", (planet,))
            return self.cursor.fetchall()

    def get_mission_by_id(self, mission_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM missions WHERE id = %s", (mission_id,))
            return self.cursor.fetchone()

    def start_launch(self, family_id, mission_id):
        with self.connection:
            self.cursor.execute("INSERT INTO launches (family_id, mission_id) VALUES (%s, %s) RETURNING id", (family_id, mission_id))
            return self.cursor.fetchone()[0]

    def sign_launch(self, launch_id, user_id):
        with self.connection:
            self.cursor.execute("SELECT signatures FROM launches WHERE id = %s", (launch_id,))
            row = self.cursor.fetchone()
            if not row: return False
            sigs = row[0].split(',') if row[0] else []
            if str(user_id) in sigs: return False
            sigs.append(str(user_id))
            new_sigs = ",".join(filter(None, sigs))
            self.cursor.execute("UPDATE launches SET signatures = %s WHERE id = %s", (new_sigs, launch_id))
            return len(sigs)

    def update_launch_status(self, launch_id, status):
        with self.connection:
            self.cursor.execute("UPDATE launches SET status = %s WHERE id = %s", (status, launch_id))

    def get_timers(self, family_id):
        with self.connection:
            self.cursor.execute("SELECT mission_end_time, active_launch_id, active_mission_id, upgrade_end_time FROM families WHERE id = %s", (family_id,))
            return self.cursor.fetchone()

    def set_mission_timer(self, family_id, minutes, launch_id, mission_id):
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        with self.connection:
            self.cursor.execute("UPDATE families SET mission_end_time = %s, active_launch_id = %s, active_mission_id = %s WHERE id = %s", 
                                (end_time, launch_id, mission_id, family_id))

    def clear_mission_timer(self, family_id):
        with self.connection:
            self.cursor.execute("UPDATE families SET mission_end_time = NULL, active_launch_id = NULL, active_mission_id = NULL WHERE id = %s", (family_id,))

    def set_upgrade_timer(self, family_id, minutes):
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        with self.connection:
            self.cursor.execute("UPDATE families SET upgrade_end_time = %s WHERE id = %s", (end_time, family_id))

    def finish_upgrade(self, family_id, planet=None):
        with self.connection:
            if not planet:
                self.cursor.execute("SELECT current_planet FROM families WHERE id = %s", (family_id,))
                planet = self.cursor.fetchone()[0]
                
            p = planet.lower()
            self.cursor.execute(f"UPDATE families SET mine_lvl_{p} = mine_lvl_{p} + 1, last_coll_{p} = CURRENT_TIMESTAMP, upgrade_end_time = NULL WHERE id = %s", (family_id,))

    def get_expired_missions(self):
        import datetime
        # Беремо час бота, а не бази даних, щоб уникнути проблем з часовими поясами
        now = datetime.datetime.now()
        with self.connection:
            # ДЛЯ POSTGRESQL (psycopg2) ВИКОРИСТОВУЄМО %s
            self.cursor.execute("""
                SELECT id, active_mission_id, active_launch_id, current_planet 
                FROM families 
                WHERE mission_end_time IS NOT NULL AND mission_end_time <= %s
            """, (now,))
            return self.cursor.fetchall()

    def get_expired_upgrades(self):
        import datetime
        now = datetime.datetime.now()
        with self.connection:
            # ДЛЯ POSTGRESQL (psycopg2) ВИКОРИСТОВУЄМО %s
            self.cursor.execute("""
                SELECT id, current_planet, mine_lvl 
                FROM families 
                WHERE upgrade_end_time IS NOT NULL AND upgrade_end_time <= %s
            """, (now,))
            return self.cursor.fetchall()
    
    def get_family(self, family_id):
        """Отримує дані сім'ї за її ID"""
        with self.connection:
            self.cursor.execute("SELECT * FROM families WHERE id = %s", (family_id,))
            return self.cursor.fetchone()
        
    def get_mission_by_name(self, name):
        """Отримує місію за назвою"""
        with self.connection:
            self.cursor.execute("SELECT * FROM missions WHERE name = %s", (name,))
            return self.cursor.fetchone()

    def get_family_user_ids(self, family_id):
        with self.connection:
            # ВИПРАВЛЕНО: Було "SELECT id", стало "SELECT user_id"
            self.cursor.execute("SELECT user_id FROM users WHERE family_id = %s", (family_id,))
            result = self.cursor.fetchall()
            return [row[0] for row in result]
            
    def admin_skip_timers(self, family_id):
        with self.connection:
            past_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
            self.cursor.execute("UPDATE families SET mission_end_time = %s WHERE id = %s AND mission_end_time IS NOT NULL", (past_time, family_id))
            self.cursor.execute("UPDATE families SET upgrade_end_time = %s WHERE id = %s AND upgrade_end_time IS NOT NULL", (past_time, family_id))

    def get_family_power(self, family_id):
        with self.connection:
            self.cursor.execute("SELECT engine_lvl, hull_lvl, mine_lvl_earth FROM families WHERE id = %s", (family_id,))
            row = self.cursor.fetchone()
            if row: return row[0] + row[1] + int(row[2] / 2)
            return 0
        
    def get_random_enemy(self, my_family_id):
        with self.connection:
            self.cursor.execute("""
                SELECT id, name, balance, hull_lvl, current_planet 
                FROM families 
                WHERE id != %s 
                  AND current_planet NOT IN ('Earth', 'Moon')
                  AND (shield_until IS NULL OR shield_until <= CURRENT_TIMESTAMP)
                ORDER BY RANDOM() LIMIT 1
            """, (my_family_id,))
            return self.cursor.fetchone()

    def get_all_families_for_events(self):
        with self.connection:
            self.cursor.execute("SELECT id, current_planet, hull_lvl, engine_lvl, balance FROM families")
            return self.cursor.fetchall()

    def set_raid_cooldown(self, fid, mins):
        t = datetime.datetime.now() + datetime.timedelta(minutes=mins)
        with self.connection: 
            self.cursor.execute("UPDATE families SET last_raid_time = %s WHERE id = %s", (t, fid))

    def get_last_raid(self, fid):
        with self.connection:
            self.cursor.execute("SELECT last_raid_time FROM families WHERE id = %s", (fid,))
            r = self.cursor.fetchone()
            return r[0] if r else None

    def set_shield(self, fid, mins):
        t = datetime.datetime.now() + datetime.timedelta(minutes=mins)
        with self.connection: 
            self.cursor.execute("UPDATE families SET shield_until = %s WHERE id = %s", (t, fid))

    def get_family_unlocked_modules(self, family_id):
        with self.connection:
            self.cursor.execute(
                "SELECT module_id FROM family_upgrades WHERE family_id = %s", 
                (family_id,)
            )
            res = self.cursor.fetchall()
            return [row[0] for row in res]

    def buy_module_upgrade(self, family_id, module_data):
        m_id = module_data['id']
        costs = module_data.get('cost', {})
        requires_id = module_data.get('requires') # <--- Читаємо залежність

        with self.connection:
            # 1. Перевірка чи вже куплено
            self.cursor.execute("SELECT id FROM family_upgrades WHERE family_id = %s AND module_id = %s", (family_id, m_id))
            if self.cursor.fetchone(): return False, "Вже досліджено"

            # 2. ПЕРЕВІРКА: ЧИ КУПЛЕНО ПОПЕРЕДНІЙ МОДУЛЬ? (НОВЕ)
            if requires_id:
                self.cursor.execute("SELECT id FROM family_upgrades WHERE family_id = %s AND module_id = %s", (family_id, requires_id))
                if not self.cursor.fetchone():
                    return False, "❌ Спочатку дослідіть попередній модуль у гілці!"

            # 3. Отримуємо всі ресурси сім'ї
            self.cursor.execute("SELECT balance, res_iron, res_fuel, res_regolith, res_he3, res_silicon, res_oxide, res_hydrogen, res_helium FROM families WHERE id = %s", (family_id,))
            res_row = self.cursor.fetchone()
            
            # Мапа для зручного доступу
            user_res = {
                'coins': res_row[0], 'iron': res_row[1], 'fuel': res_row[2],
                'regolith': res_row[3], 'he3': res_row[4], 'silicon': res_row[5],
                'oxide': res_row[6], 'hydrogen': res_row[7], 'helium': res_row[8]
            }

            # 4. Перевірка чи вистачає ресурсів
            for res_name, amount in costs.items():
                if user_res.get(res_name, 0) < amount:
                    return False, f"Недостатньо {res_name}"

            # 5. Знімаємо ресурси
            for res_name, amount in costs.items():
                db_col = f"res_{res_name}" if res_name != 'coins' else "balance"
                self.cursor.execute(f"UPDATE families SET {db_col} = {db_col} - %s WHERE id = %s", (amount, family_id))

            # 6. Додаємо в список куплених
            self.cursor.execute("INSERT INTO family_upgrades (family_id, module_id) VALUES (%s, %s)", (family_id, m_id))
            
            return True, "Успішно досліджено!"
        
    def get_full_inventory(self, family_id):
        try:
            with self.connection:
                self.cursor.execute("""
                    SELECT 
                        balance, res_iron, res_fuel, res_regolith, 
                        res_he3, res_silicon, res_oxide, res_hydrogen, res_helium,
                        unlocked_planets
                    FROM families
                    WHERE id = %s
                """, (family_id,))
                res = self.cursor.fetchone()

                self.cursor.execute("SELECT module_id FROM family_upgrades WHERE family_id = %s", (family_id,))
                upgrades = self.cursor.fetchall()
                owned_ids = [row[0] for row in upgrades]

                if not res: return None
                
                # Обробка списку планет
                unlocked_str = res[9]
                unlocked_list = unlocked_str.split(',') if unlocked_str else ['Earth']

                return {
                    "resources": {
                        "coins": res[0], "iron": res[1], "fuel": res[2], "regolith": res[3],
                        "he3": res[4], "silicon": res[5], "oxide": res[6], "hydrogen": res[7], "helium": res[8]
                    },
                    "owned_modules": owned_ids,
                    "unlocked_planets": unlocked_list # <--- ДОДАЛИ СЮДИ
                }
        except Exception as e:
            print(f"DB Inventory Error: {e}")
            return None
    # --- НАВІГАЦІЯ ---

    def get_todays_purchases(self, family_id):
        """Отримує список ID товарів, які сім'я вже купила сьогодні"""
        self.cursor.execute("""
            SELECT item_id FROM shop_purchases 
            WHERE family_id = %s AND purchase_date = CURRENT_DATE
        """, (family_id,))
        return [row[0] for row in self.cursor.fetchall()]
    def buy_shop_item(self, family_id, item_id, cost, res_name, res_amount):
        """Здійснює покупку, перевіряючи, чи не купили цей товар сьогодні"""
        # 1. Перевіряємо, чи вже купували СЬОГОДНІ
        self.cursor.execute("""
            SELECT id FROM shop_purchases 
            WHERE family_id = %s AND item_id = %s AND purchase_date = CURRENT_DATE
        """, (family_id, item_id))
        
        if self.cursor.fetchone():
            return False, "Ви вже придбали цей товар сьогодні!"
            
        # 2. Перевіряємо баланс
        self.cursor.execute("SELECT balance FROM families WHERE id = %s", (family_id,))
        balance = self.cursor.fetchone()[0]
        
        if balance < cost:
            return False, "Недостатньо Спейскоїнів!"
        
        # 3. Списуємо гроші та видаємо ресурс
        db_col = f"res_{res_name}"
        self.cursor.execute(f"""
            UPDATE families 
            SET balance = balance - %s, 
                {db_col} = {db_col} + %s 
            WHERE id = %s
        """, (cost, res_amount, family_id))
        
        # 4. ЗАПИСУЄМО ПОКУПКУ В ІСТОРІЮ
        self.cursor.execute("""
            INSERT INTO shop_purchases (family_id, item_id) 
            VALUES (%s, %s)
        """, (family_id, item_id))
        
        return True, f"Успішно придбано {res_amount} {res_name.upper()}!"
    def get_unlocked_planets(self, family_id):
        with self.connection:
            self.cursor.execute("SELECT unlocked_planets FROM families WHERE id = %s", (family_id,))
            res = self.cursor.fetchone()
            # Повертаємо список ['Earth', 'Moon']
            return res[0].split(',') if res and res[0] else ['Earth']

    def unlock_planet(self, family_id, new_planet):
        # Спочатку отримуємо поточні
        current = self.get_unlocked_planets(family_id)
        if new_planet not in current:
            current.append(new_planet)
            new_str = ",".join(current)
            with self.connection:
                self.cursor.execute("UPDATE families SET unlocked_planets = %s WHERE id = %s", (new_str, family_id))

    def travel_to_planet(self, family_id, planet_name):
        with self.connection:
            self.cursor.execute("UPDATE families SET current_planet = %s WHERE id = %s", (planet_name, family_id))
    def get_mine_info(self, family_id, planet):
        """Отримує рівень шахти та таймер збору для конкретної планети"""
        p = planet.lower() # 'earth', 'moon', 'mars', 'jupiter'
        with self.connection:
            self.cursor.execute(f"SELECT mine_lvl_{p}, last_coll_{p} FROM families WHERE id = %s", (family_id,))
            return self.cursor.fetchone()
    
    # --- ДОСЛІДНИЦЬКА ЛАБОРАТОРІЯ ---
    def add_quiz(self, planet, question, opt1, opt2, opt3, opt4, correct_opt, reward):
        with self.connection:
            self.cursor.execute("""
                INSERT INTO quizzes (planet, question, opt1, opt2, opt3, opt4, correct_opt, reward)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (planet, question, opt1, opt2, opt3, opt4, correct_opt, reward))

    def get_random_quiz(self, planet, difficulty):
        # Визначаємо складність на основі нагороди
        if difficulty == 'easy':
            condition = "reward <= 1000"
        elif difficulty == 'medium':
            condition = "reward > 1000 AND reward <= 2000"
        else: # hard
            condition = "reward > 2000"
            
        self.cursor.execute(f"SELECT * FROM quizzes WHERE planet = %s AND {condition} ORDER BY RANDOM() LIMIT 1", (planet,))
        return self.cursor.fetchone()

    def get_quiz_by_id(self, quiz_id):
        self.cursor.execute("SELECT * FROM quizzes WHERE id = %s", (quiz_id,))
        return self.cursor.fetchone()

    def give_quiz_reward(self, family_id, reward_coins, planet):
        # Зменшені ресурси: 5% (основний) та 2% (рідкісний) від суми монет
        res_main = int(reward_coins * 0.05)
        res_rare = int(reward_coins * 0.02)
        
        query = "UPDATE families SET balance = balance + %s, "
        params = [reward_coins]
        
        # Видаємо ресурси залежно від планети
        if planet.lower() == 'earth':
            query += "res_iron = res_iron + %s, res_fuel = res_fuel + %s"
        elif planet.lower() == 'moon':
            query += "res_regolith = res_regolith + %s, res_he3 = res_he3 + %s"
        elif planet.lower() == 'mars':
            query += "res_silicon = res_silicon + %s, res_oxide = res_oxide + %s"
        elif planet.lower() == 'jupiter':
            query += "res_hydrogen = res_hydrogen + %s, res_helium = res_helium + %s"
        else:
            query += "res_iron = res_iron + %s, res_fuel = res_fuel + %s" # Запасний варіант
            
        params.extend([res_main, res_rare])
        query += " WHERE id = %s"
        params.append(family_id)
        
        with self.connection:
            self.cursor.execute(query, tuple(params))

    def check_quiz_attempts(self, family_id):
        import datetime
        with self.connection:
            self.cursor.execute("SELECT quiz_attempts, last_quiz_date FROM families WHERE id = %s", (family_id,))
            res = self.cursor.fetchone()
            if not res: return False, 0
            
            attempts, last_date = res[0], res[1]
            today = datetime.date.today()
            
            if last_date != today:
                # Скидаємо лічильник на новий день
                self.cursor.execute("UPDATE families SET quiz_attempts = 0, last_quiz_date = %s WHERE id = %s", (today, family_id))
                return True, 5
            
            if attempts >= 5:
                return False, 0
            return True, 5 - attempts

    def increment_quiz_attempt(self, family_id):
        import datetime
        with self.connection:
            today = datetime.date.today()
            self.cursor.execute("UPDATE families SET quiz_attempts = quiz_attempts + 1, last_quiz_date = %s WHERE id = %s", (today, family_id))

    # --- КОЛЕСО ФОРТУНИ ---
    def check_fortune(self, user_id):
        """Перевіряє, чи може КОНКРЕТНИЙ ГРАВЕЦЬ крутити рулетку (раз на 24 години)"""
        with self.lock:
            with self.connection:
                self.cursor.execute("SELECT last_fortune FROM users WHERE user_id = %s", (user_id,))
                res = self.cursor.fetchone()
                if not res or not res[0]:
                    return True, None
                
                last_time = res[0]
                now = datetime.datetime.now()
                diff = now - last_time
                if diff.total_seconds() >= 86400: # 86400 секунд = 24 години
                    return True, None
                
                left = 86400 - diff.total_seconds()
                hours = int(left // 3600)
                minutes = int((left % 3600) // 60)
                return False, f"{hours}г {minutes}хв"

    def claim_fortune(self, family_id, user_id, reward_type, amount):
        """Видає нагороду на баланс сім'ї, але таймер вішає на конкретного гравця"""
        with self.lock:
            with self.connection:
                # 1. Оновлюємо таймер ГРАВЦЯ
                now = datetime.datetime.now()
                self.cursor.execute("UPDATE users SET last_fortune = %s WHERE user_id = %s", (now, user_id))
                
                # 2. Видаємо нагороду СІМ'Ї
                if reward_type == 'coins':
                    self.cursor.execute("UPDATE families SET balance = balance + %s WHERE id = %s", (amount, family_id))
                else:
                    column = f"res_{reward_type}"
                    self.cursor.execute(f"UPDATE families SET {column} = {column} + %s WHERE id = %s", (amount, family_id))
                
                self.connection.commit()
    # --- СІМЕЙНИЙ ВЕБ-ЧАТ ---
    def get_family_members_status(self, family_id):
        with self.lock: # <- ДОДАНО
            with self.connection:
                self.cursor.execute("""
                    SELECT user_id, username, role, 
                           (CURRENT_TIMESTAMP - last_active) < INTERVAL '2 minutes' AS is_online
                    FROM users 
                    WHERE family_id = %s
                """, (family_id,))
                return self.cursor.fetchall()
            
    def ping_user_activity(self, user_id):
        with self.lock: # <- ДОДАНО
            with self.connection:
                self.cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = %s", (user_id,))

    def add_chat_message(self, family_id, user_id, username, text):
        with self.lock: # <- ДОДАНО
            with self.connection:
                self.cursor.execute("""
                    INSERT INTO family_messages (family_id, user_id, username, text)
                    VALUES (%s, %s, %s, %s)
                """, (family_id, user_id, username, text))

    def get_chat_messages(self, family_id, limit=50):
        with self.lock: # <- ДОДАНО
            with self.connection:
                self.cursor.execute("""
                    SELECT user_id, username, text, created_at
                    FROM (
                        SELECT user_id, username, text, created_at
                        FROM family_messages
                        WHERE family_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    ) AS sub
                    ORDER BY created_at ASC
                """, (family_id, limit))
                return self.cursor.fetchall()