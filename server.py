from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import Database
import datetime
import random
import os
import requests
import math
from config import BOT_TOKEN

# Вказуємо, що статичні файли (html, css, js) лежать прямо тут ('.')
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Підключення до бази (залишається як було)
db = Database() 

CATALOG = {
    # ==========================================
    # --- ЗЕМЛЯ (Earth) ---
    # ==========================================
    
    # Гілка: Ніс
    'gu1': {'name': 'Конус-верхівка', 'type': 'nose', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'aerodynamics': 10}},
    'gu2': {'name': 'Сенсорний шпиль', 'type': 'nose', 'tier': 'II', 'cost': {'iron': 400, 'fuel': 150, 'coins': 250}, 'stats': {'aerodynamics': 25}, 'requires': 'gu1'},
    
    # Гілка: Корпус
    'nc1': {'name': 'Корпус', 'type': 'body', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'armor': 50}},
    'h1': {'name': 'Сталевий Корпус', 'type': 'body', 'tier': 'II', 'cost': {'iron': 600, 'fuel': 200, 'coins': 400}, 'stats': {'armor': 120}, 'requires': 'nc1'},
    
    # Гілка: Двигун
    'e1': {'name': 'Турбіна', 'type': 'engine', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'speed': 30}},
    'e2': {'name': 'Турбо-нагнітач', 'type': 'engine', 'tier': 'II', 'cost': {'iron': 500, 'fuel': 300, 'coins': 500}, 'stats': {'speed': 75}, 'requires': 'e1'},
    
    # Гілка: Стабілізатори
    'a1': {'name': 'Надкрилки', 'type': 'fins', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'handling': 15}},
    'a2': {'name': 'Активні закрилки', 'type': 'fins', 'tier': 'II', 'cost': {'iron': 300, 'fuel': 150, 'coins': 350}, 'stats': {'handling': 40}, 'requires': 'a1'},

    # ==========================================
    # --- МІСЯЦЬ (Moon) ---
    # ==========================================
    
    # Гілка 1: Корпус та додаткові модулі
    'root1': {'name': 'Сталевий Корпус', 'type': 'body', 'tier': 'II', 'cost': {'regolith': 0, 'he3': 0, 'coins': 0}, 'stats': {'armor': 120}},
    'branch1_up1': {'name': 'Вантажний Відсік', 'type': 'cargo', 'tier': 'III', 'cost': {'regolith': 500, 'he3': 200, 'coins': 800}, 'stats': {'armor': 200}, 'requires': 'root1'},
    'branch1_up2': {'name': 'Сонячні Панелі', 'type': 'solar', 'tier': 'IV', 'cost': {'regolith': 700, 'he3': 400, 'coins': 1200}, 'stats': {'armor': 250}, 'requires': 'branch1_up1'},
    'branch1_down1': {'name': 'Аеро-надкрилки', 'type': 'fins', 'tier': 'III', 'cost': {'regolith': 400, 'he3': 150, 'coins': 900}, 'stats': {'handling': 65}, 'requires': 'root1'},

    # Гілка 2: Двигуни
    'root2': {'name': 'Турбо-нагнітач', 'type': 'engine', 'tier': 'II', 'cost': {'regolith': 0, 'he3': 0, 'coins': 0}, 'stats': {'speed': 75}},
    'branch2_up': {'name': 'Турбо-Форсаж', 'type': 'engine', 'tier': 'III', 'cost': {'regolith': 800, 'he3': 600, 'coins': 1500}, 'stats': {'speed': 150}, 'requires': 'root2'},
    'branch2_down': {'name': 'Бокові Рушії', 'type': 'booster', 'tier': 'II', 'cost': {'regolith': 600, 'he3': 400, 'coins': 1000}, 'stats': {'speed': 100}, 'requires': 'root2'},

    # Гілка 3: Кабіна та Ніс
    'root3': {'name': 'Кабіна Екіпажу', 'type': 'cabin', 'tier': 'II', 'cost': {'regolith': 0, 'he3': 0, 'coins': 0}, 'stats': {'aerodynamics': 25}},
    'branch3': {'name': 'Керамічний Щит', 'type': 'nose', 'tier': 'III', 'cost': {'regolith': 500, 'he3': 300, 'coins': 1100}, 'stats': {'aerodynamics': 55}, 'requires': 'root3'},

    # ==========================================
    # --- МАРС (Mars) ---
    # ==========================================
    
    # Гілка 1: Корпус, Панелі та Відсіки
    'g1_1': {'name': 'Вантажний Відсік', 'type': 'cargo', 'tier': 'III', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'armor': 200}},
    'g1_2': {'name': 'Герметизація', 'type': 'body', 'tier': 'IV', 'cost': {'silicon': 900, 'oxide': 500, 'coins': 2500}, 'stats': {'armor': 450}, 'requires': 'g1_1'},
    
    'g1_up': {'name': 'Панель Оновлення', 'type': 'cabin', 'tier': 'III', 'cost': {'silicon': 1200, 'oxide': 800, 'coins': 3500}, 'stats': {'armor': 350}, 'requires': 'g1_1'},
    'g1_up2': {'name': 'Лабораторний Модуль', 'type': 'cargo', 'tier': 'IV', 'cost': {'silicon': 2000, 'oxide': 1200, 'coins': 5000}, 'stats': {'armor': 600}, 'requires': 'g1_up'},
    
    'g1_down': {'name': 'Сонячні Панелі', 'type': 'solar', 'tier': 'V', 'cost': {'silicon': 1000, 'oxide': 600, 'coins': 3000}, 'stats': {'armor': 600}, 'requires': 'g1_1'},
    'g1_end': {'name': 'Нові Панелі MK-II', 'type': 'solar', 'tier': 'VI', 'cost': {'silicon': 1500, 'oxide': 1000, 'coins': 5000}, 'stats': {'armor': 900}, 'requires': 'g1_down'},

    # Гілка 2: Двигуни та Стабілізація
    'g2_1': {'name': 'Турбо-Форсаж', 'type': 'engine', 'tier': 'III', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'speed': 150}},
    'g2_up': {'name': 'Покращений Форсаж', 'type': 'engine', 'tier': 'IV', 'cost': {'silicon': 1800, 'oxide': 1200, 'coins': 4500}, 'stats': {'speed': 320}, 'requires': 'g2_1'},
    
    'g2_down': {'name': 'Бокові Турбіни', 'type': 'booster', 'tier': 'III', 'cost': {'silicon': 1200, 'oxide': 800, 'coins': 3200}, 'stats': {'speed': 210}, 'requires': 'g2_1'},
    'g2_down2': {'name': 'Аеро-Стабілізатори', 'type': 'fins', 'tier': 'IV', 'cost': {'silicon': 1600, 'oxide': 900, 'coins': 3800}, 'stats': {'handling': 85}, 'requires': 'g2_down'},

    # Гілка 3: Ніс та Зброя
    'g3_a1': {'name': 'Керамічний Щит', 'type': 'nose', 'tier': 'III', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'aerodynamics': 55}},
    'g3_a2': {'name': 'Нова Верхівка', 'type': 'nose', 'tier': 'IV', 'cost': {'silicon': 1100, 'oxide': 600, 'coins': 2800}, 'stats': {'aerodynamics': 90}, 'requires': 'g3_a1'},
    
    'g3_b1': {'name': 'Бластер', 'type': 'weapons', 'tier': 'I', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'damage': 40}},
    'g3_b2': {'name': 'Покращений Бластер', 'type': 'weapons', 'tier': 'II', 'cost': {'silicon': 2000, 'oxide': 1500, 'coins': 5000}, 'stats': {'damage': 110}, 'requires': 'g3_b1'},

    # ==========================================
    # --- ЮПІТЕР (Jupiter) ---
    # ==========================================
    
    # Гілка: Корпус, Панелі та Зброя
    'hull_start': {'name': 'Герметизація', 'type': 'body', 'tier': 'IV', 'cost': {'hydrogen': 0, 'helium': 0, 'coins': 0}, 'stats': {'armor': 450}},
    'hull_mk2': {'name': 'Композитний Корпус', 'type': 'body', 'tier': 'V', 'cost': {'hydrogen': 3000, 'helium': 2000, 'coins': 8000}, 'stats': {'armor': 1200}, 'requires': 'hull_start'},
    
    'solar_upg': {'name': 'Фотоелементи MK-2', 'type': 'solar', 'tier': 'VII', 'cost': {'hydrogen': 4000, 'helium': 2500, 'coins': 10000}, 'stats': {'armor': 1800}, 'requires': 'hull_start'},
    'solar_max': {'name': 'Квантові Панелі', 'type': 'solar', 'tier': 'VIII', 'cost': {'hydrogen': 6000, 'helium': 4000, 'coins': 15000}, 'stats': {'armor': 3000}, 'requires': 'solar_upg'},
    
    'aux_bay': {'name': 'Допоміжні Відсіки', 'type': 'cargo', 'tier': 'V', 'cost': {'hydrogen': 3500, 'helium': 2500, 'coins': 7500}, 'stats': {'armor': 1000}, 'requires': 'hull_start'},
    'combat_bay': {'name': 'Бойовий Модуль', 'type': 'cargo', 'tier': 'VI', 'cost': {'hydrogen': 5500, 'helium': 4500, 'coins': 12000}, 'stats': {'armor': 1500}, 'requires': 'aux_bay'},
    
    'cannons': {'name': 'Плазмові Гармати', 'type': 'weapons', 'tier': 'I', 'cost': {'hydrogen': 8000, 'helium': 6000, 'coins': 20000}, 'stats': {'damage': 350}, 'requires': 'combat_bay'},

    # Гілка: Двигуни
    'eng_start': {'name': 'Форсаж', 'type': 'engine', 'tier': 'IV', 'cost': {'hydrogen': 0, 'helium': 0, 'coins': 0}, 'stats': {'speed': 320}},
    'eng_ultimate': {'name': 'Гіпер-Турбіна', 'type': 'engine', 'tier': 'V', 'cost': {'hydrogen': 9000, 'helium': 7000, 'coins': 18000}, 'stats': {'speed': 800}, 'requires': 'eng_start'},
    'eng_side': {'name': 'Бокові Рушії', 'type': 'booster', 'tier': 'IV', 'cost': {'hydrogen': 2500, 'helium': 1500, 'coins': 7000}, 'stats': {'speed': 450}, 'requires': 'eng_start'},

    # Гілка: Ніс
    'nose_start': {'name': 'Титановий Конус', 'type': 'nose', 'tier': 'IV', 'cost': {'hydrogen': 0, 'helium': 0, 'coins': 0}, 'stats': {'aerodynamics': 90}},
    'nose_adv': {'name': 'Аеро-Композит', 'type': 'nose', 'tier': 'V', 'cost': {'hydrogen': 4500, 'helium': 3000, 'coins': 9000}, 'stats': {'aerodynamics': 200}, 'requires': 'nose_start'},
}
# --- НОВІ МАРШРУТИ ДЛЯ САЙТУ ---

@app.route('/')
def index():
    # Головна сторінка
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Будь-які інші файли (CSS, JS, картинки, інші HTML)
    return send_from_directory('.', path)

# -------------------------------

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        family_id = request.args.get('family_id')
        if not family_id:
            return jsonify({'error': 'No family_id provided'}), 400

        data = db.get_family_resources(family_id)
        if not data:
            return jsonify({'error': 'Family not found'}), 404

        resources_data = {
            'coins': data[0],
            'iron': data[1],
            'fuel': data[2],
            'regolith': data[3],
            'he3': data[4],
            'silicon': data[5],
            'oxide': data[6],
            'hydrogen': data[7],
            'helium': data[8]
        }

        owned_ids = db.get_family_unlocked_modules(family_id)
        
        modules_list = []
        for uid in owned_ids:
            if uid in CATALOG:
                mod_info = CATALOG[uid].copy()
                mod_info['id'] = uid
                modules_list.append(mod_info)

        # --- НОВИЙ КОД: Отримуємо розблоковані планети ---
        try:
            unlocked_planets = db.get_unlocked_planets(family_id)
        except Exception:
            unlocked_planets = ['Earth'] # Захист від помилок, якщо колонки ще немає
        # --------------------------------------------------

        return jsonify({
            'resources': resources_data,
            'modules': modules_list,
            'unlocked_planets': unlocked_planets # Відправляємо на сайт
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

SHOP_ITEMS_POOL = [
    {'id': 'iron_pack', 'name': 'Пакет Заліза', 'res_name': 'iron', 'base_amount': 500, 'base_cost': 200, 'icon': '🔩'},
    {'id': 'fuel_pack', 'name': 'Кріо-паливо', 'res_name': 'fuel', 'base_amount': 300, 'base_cost': 250, 'icon': '⛽'},
    {'id': 'regolith_pack', 'name': 'Місячний Реголіт', 'res_name': 'regolith', 'base_amount': 200, 'base_cost': 400, 'icon': '🌑'},
    {'id': 'he3_pack', 'name': 'Ізотоп Гелій-3', 'res_name': 'he3', 'base_amount': 150, 'base_cost': 500, 'icon': '☣️'},
    {'id': 'silicon_pack', 'name': 'Кремній', 'res_name': 'silicon', 'base_amount': 300, 'base_cost': 350, 'icon': '💠'},
]

@app.route('/api/daily_offers', methods=['GET'])
def get_daily_offers():
    # Отримуємо family_id, щоб перевірити їхні покупки
    family_id = request.args.get('family_id')
    purchased_today = []
    
    if family_id:
        purchased_today = db.get_todays_purchases(family_id)

    today = datetime.date.today()
    random.seed(today.toordinal())
    
    daily_items = random.sample(SHOP_ITEMS_POOL, min(4, len(SHOP_ITEMS_POOL)))
    offers = []
    
    has_free_item = random.random() < 0.20 
    discount_count = random.randint(1, 2)
    
    for i, item in enumerate(daily_items):
        discount = 0
        
        if has_free_item and i == 0:
            discount = 100
            discount_count -= 1
        elif discount_count > 0:
            discount = random.randint(10, 40)
            discount_count -= 1
            
        final_cost = int(item['base_cost'] * (1 - discount / 100))
        amount = item['base_amount']
        if discount == 100:
            amount = max(10, int(item['base_amount'] * 0.3)) 
            
        offers.append({
            'id': item['id'],
            'name': item['name'],
            'res_name': item['res_name'],
            'amount': amount,
            'old_price': item['base_cost'],
            'price': final_cost,
            'discount': discount,
            'icon': item['icon'],
            # НОВИЙ ПАРАМЕТР: Перевіряємо, чи є цей товар у куплених
            'purchased': item['id'] in purchased_today 
        })
        
    random.shuffle(offers)
    random.seed()
    
    return jsonify({'offers': offers})

@app.route('/api/buy_shop_item', methods=['POST'])
def buy_shop_item():
    try:
        data = request.json
        family_id = data.get('family_id')
        item_data = data.get('item')

        if not family_id or not item_data:
            return jsonify({'error': 'Недійсні дані'}), 400

        success, msg = db.buy_shop_item(
            family_id, 
            item_data['id'],       # ТЕПЕР ПЕРЕДАЄМО ID ТОВАРУ
            item_data['price'], 
            item_data['res_name'], 
            item_data['amount']
        )

        if success:
            return jsonify({'message': msg}), 200
        else:
            return jsonify({'error': msg}), 400
            
    except Exception as e:
        print(f"SHOP ERROR: {e}")
        return jsonify({'error': 'Помилка транзакції'}), 500
    
@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    family_id = request.args.get('family_id')
    planet = request.args.get('planet', 'Earth').capitalize() 
    difficulty = request.args.get('difficulty', 'easy')
    
    if not family_id: return jsonify({'error': 'Не вказано ID сім\'ї'}), 400

    # ПЕРЕВІРКА НА 5 СПРОБ В ДЕНЬ
    can_play, attempts_left = db.check_quiz_attempts(family_id)
    if not can_play:
        return jsonify({'error': '⏳ Ви використали всі 5 спроб на сьогодні. Повертайтесь завтра!'}), 403

    unlocked = db.get_unlocked_planets(family_id)
    if planet not in unlocked: return jsonify({'error': '❌ Ця планета ще не досліджена!'}), 403

    quiz = db.get_random_quiz(planet, difficulty)
    if not quiz:
        return jsonify({'error': f'Питань ({difficulty}) для бази {planet} поки немає'}), 404
    
    reward_coins = quiz[8] 
    res_main = int(reward_coins * 0.05)
    res_rare = int(reward_coins * 0.02)
    
    if planet.lower() == 'earth': res_text = f"{res_main} 🪨 | {res_rare} ⛽"
    elif planet.lower() == 'moon': res_text = f"{res_main} 🌑 | {res_rare} 💨"
    elif planet.lower() == 'mars': res_text = f"{res_main} 💠 | {res_rare} 🔴"
    elif planet.lower() == 'jupiter': res_text = f"{res_main} 💧 | {res_rare} 🎈"
    else: res_text = ""
    
    return jsonify({
        'id': quiz[0], 'planet': quiz[1], 'question': quiz[2],
        'options': [quiz[3], quiz[4], quiz[5], quiz[6]],
        'reward_text': f"{reward_coins} 🪙 | {res_text}",
        'attempts_left': attempts_left # <--- Передаємо кількість спроб
    })

# В роуті /api/quiz/answer потрібно змінити індекси:
@app.route('/api/quiz/answer', methods=['POST'])
def submit_quiz_answer():
    data = request.json
    family_id, quiz_id, user_answer_index = data.get('family_id'), data.get('quiz_id'), data.get('answer')
    
    # ЗБІЛЬШУЄМО ЛІЧИЛЬНИК СПРОБ, КОЛИ ГРАВЕЦЬ ДАВ ВІДПОВІДЬ
    db.increment_quiz_attempt(family_id)

    quiz = db.get_quiz_by_id(quiz_id)
    if not quiz: return jsonify({'success': False, 'message': 'Питання не знайдено'})
    
    correct_index = quiz[7] - 1 
    
    if user_answer_index == correct_index:
        reward_coins = quiz[8]
        planet = quiz[1]
        db.give_quiz_reward(family_id, reward_coins, planet)
        
        res_main = int(reward_coins * 0.05)
        res_rare = int(reward_coins * 0.02)
        
        if planet.lower() == 'earth': res_text = f"{res_main} Заліза та {res_rare} Палива"
        elif planet.lower() == 'moon': res_text = f"{res_main} Реголіту та {res_rare} Гелію-3"
        elif planet.lower() == 'mars': res_text = f"{res_main} Кремнію та {res_rare} Оксиду"
        elif planet.lower() == 'jupiter': res_text = f"{res_main} Водню та {res_rare} Гелію"
        else: res_text = ""
        
        return jsonify({
            'success': True, 
            'correct': True, 
            'reward_text': f"{reward_coins} 🪙, {res_text}!",
            'reward_coins': reward_coins,
            'res_main': res_main,
            'res_rare': res_rare
        })
    else:
        return jsonify({'success': True, 'correct': False, 'correct_index': correct_index})
    
@app.route('/api/quiz/leave', methods=['POST'])
def leave_quiz():
    data = request.json
    user_id = data.get('user_id')
    planet = data.get('planet', 'Earth')
    coins = data.get('coins', 0)
    main = data.get('main', 0)
    rare = data.get('rare', 0)

    # Якщо гравець нічого не заробив або ID загубився - просто ігноруємо
    if not user_id or coins == 0:
        return jsonify({'success': True})

    # Формуємо красивий текст під кожну планету
    if planet.lower() == 'earth': res_text = f"🪨 {main} Заліза\n⛽ {rare} Палива"
    elif planet.lower() == 'moon': res_text = f"🌑 {main} Реголіту\n💨 {rare} Гелію-3"
    elif planet.lower() == 'mars': res_text = f"💠 {main} Кремнію\n🔴 {rare} Оксиду"
    elif planet.lower() == 'jupiter': res_text = f"💧 {main} Водню\n🎈 {rare} Гелію"
    else: res_text = ""

    text = f"🧪 **Звіт з лабораторії ({planet.upper()})**\n━━━━━━━━━━━━━━━━━━━━━\nВи успішно завершили дослідження!\n\n**Ваш заробіток:**\n🪙 {coins} Монет\n{res_text}"

    # Відправляємо повідомлення напряму через Telegram API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": user_id, "text": text, "parse_mode": "Markdown"})

    return jsonify({'success': True})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    text = data.get('text')

    # ⚠️ ВАШ ОСОБИСТИЙ TELEGRAM ID (щоб бот знав, куди писати)
    ADMIN_ID = "1709621202" 

    if not text:
        return jsonify({'success': False, 'message': 'Порожній текст'}), 400

    # Формуємо красиве повідомлення для вас
    msg = (
        f"📩 <b>НОВИЙ РАПОРТ ВІД ГРАВЦЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Пілот: <b>@{username}</b> (ID: <code>{user_id}</code>)\n"
        f"💬 Повідомлення:\n<i>{text}</i>"
    )

    # Відправляємо повідомлення через API Telegram напряму вам
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": ADMIN_ID, "text": msg, "parse_mode": "HTML"})

    return jsonify({'success': True})

# --- АПІ ДЛЯ КОЛЕСА ФОРТУНИ ---
@app.route('/api/fortune/check', methods=['GET'])
def fortune_check():
    # Тепер беремо user_id замість family_id
    user_id_raw = request.args.get('user_id')
    if not user_id_raw or user_id_raw == 'null':
        return jsonify({'error': 'No user_id'}), 400
        
    user_id = int(user_id_raw)
    
    can_spin, time_left = db.check_fortune(user_id)
    
    if can_spin:
        return jsonify({'can_spin': True})
    else:
        return jsonify({'can_spin': False, 'time_left': time_left})

@app.route('/api/fortune/spin', methods=['POST'])
def fortune_spin():
    data = request.json
    user_id = data.get('user_id')
    family_id = data.get('family_id')
    username = data.get('username', 'Гравець')
    reward_type = data.get('type')
    amount = data.get('amount')
    
    if not user_id or not family_id:
        return jsonify({'error': 'Missing data'}), 400
        
    # Перевірка на бекенді для безпеки
    can_spin, _ = db.check_fortune(user_id)
    if not can_spin:
        return jsonify({'error': 'Ви вже крутили колесо сьогодні!'}), 403
        
    try:
        # Викликаємо нову функцію (передаємо і family_id і user_id)
        db.claim_fortune(family_id, user_id, reward_type, amount)
        
        # Відправляємо сповіщення в бот
        translations = {
            'coins': 'Монет 🪙', 'iron': 'Заліза 🔩', 'fuel': 'Палива ⛽', 
            'silicon': 'Кремнію 💾', 'oxide': 'Оксиду 🧪', 'regolith': 'Реголіту 🌑',
            'he3': 'Гелію-3 ⚛️', 'hydrogen': 'Водню 🌫', 'helium': 'Гелію 🎈'
        }
        item_name = translations.get(reward_type, reward_type)
        
        msg = f"🎁 <b>Колесо Фортуни!</b>\nГравець <b>{username}</b> виграв для сім'ї <b>{amount} {item_name}</b>!"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        # Сповіщаємо всіх членів сім'ї (як ви хотіли раніше)
        with db.lock:
            with db.connection:
                db.cursor.execute("SELECT user_id FROM users WHERE family_id = %s", (family_id,))
                members = db.cursor.fetchall()
        for m in members:
            try: requests.post(url, json={"chat_id": str(m[0]), "text": msg, "parse_mode": "HTML"})
            except: pass
            
        return jsonify({'success': True})
    except Exception as e:
        print("FORTUNE ERROR:", e)
        return jsonify({'error': 'Помилка сервера'}), 500
    
@app.route('/api/investigate', methods=['POST'])
def investigate():
    try:
        data = request.json
        family_id = data.get('family_id')
        module_id = data.get('module_id')

        if not family_id or not module_id:
            return jsonify({'error': 'Неповні дані (відсутній ID сім\'ї або модуля)'}), 400

        # Отримуємо дані модуля з каталогу
        if module_id not in CATALOG:
            return jsonify({'error': f'Модуль {module_id} не знайдено в каталозі'}), 404

        module_info = CATALOG[module_id].copy()
        module_info['id'] = module_id
        
        # Додаємо вартість, якщо її немає в каталозі (на основі ваших treeNodes в JS)
        # Це запобігає KeyError в database.py
        if 'cost' not in module_info:
            # Дефолтна вартість для модулів, які не прописані детально
            module_info['cost'] = {'coins': 100, 'iron': 100, 'fuel': 50}

        # Викликаємо існуючий метод БД
        success, message = db.buy_module_upgrade(family_id, module_info)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        print(f"CRITICAL SERVER ERROR: {e}")
        return jsonify({'error': 'Внутрішня помилка сервера'}), 500
    
import math # Переконайтеся, що на початку файлу є цей імпорт

@app.route('/api/raid/targets', methods=['GET'])
def get_raid_targets():
    family_id_raw = request.args.get('family_id')
    if not family_id_raw or family_id_raw == 'null': return jsonify({'error': 'Немає ID сім\'ї'})
    family_id = int(family_id_raw)
    
    try:
        # ПОВЕРНУТО ОТРИМАННЯ ПЛАНЕТИ ТА ПОТУЖНОСТІ
        res = db.get_family_resources(family_id)
        if not res: return jsonify({'error': 'Сім\'ю не знайдено'})
        my_planet = res[11]
        my_power = sum(db.get_ship_total_stats(family_id).values())

        with db.lock:
            with db.connection:
                db.cursor.execute("SELECT id, name, balance, under_attack_until FROM families WHERE current_planet = %s ORDER BY id", (my_planet,))
                rows = db.cursor.fetchall()
        
        targets = []
        for r in rows:
            if r[0] == family_id: continue
            t_id = r[0]
            
            is_attacked = r[3] > datetime.datetime.now() if r[3] else False
            end_ts = int(r[3].timestamp() * 1000) if r[3] else 0
            t_power = sum(db.get_ship_total_stats(t_id).values())
            
            # ПОВЕРНУТО ПРОРАХУНОК ШАНСУ
            if my_power == 0 and t_power == 0: win_chance = 50
            else:
                chance = (my_power / (my_power + t_power + 1)) * 100
                win_chance = min(95, max(5, int(chance)))
            
            seed_rng = random.Random(t_id)
            targets.append({
                'id': t_id, 
                'name': r[1], 
                'mine_level': db.get_family_mine_level(t_id, my_planet),
                'power': t_power,
                'win_chance': win_chance,
                'under_attack': is_attacked, 
                'attack_end_ms': end_ts,
                'raid_time': seed_rng.randint(5, 12), 
                'loot_coins': int(r[2] * 0.1),
                'x': seed_rng.randint(250, 1750), 
                'y': seed_rng.randint(250, 1750)
            })
            
        # ПОВЕРНУТО ПЛАНЕТУ ТА ПОТУЖНІСТЬ У JSON!
        return jsonify({
            'planet': my_planet,
            'my_power': my_power,
            'targets': targets, 
            'server_time': int(datetime.datetime.now().timestamp() * 1000)
        })
    except Exception as e: 
        print("RAID TARGETS ERROR:", e)
        return jsonify({'error': str(e)}), 500

import threading # Переконайтеся, що цей імпорт є зверху файлу

# === ФУНКЦІЯ ДЛЯ ФОНОВОГО ПРОРАХУНКУ БОЮ ===
# Вона спрацює автоматично, коли таймер польоту добіжить до кінця
def process_raid_battle(attacker_id, target_id, raid_time):
    try:
        my_stats = db.get_ship_total_stats(attacker_id)
        target_stats = db.get_ship_total_stats(target_id)
        my_power = sum(my_stats.values())
        target_power = sum(target_stats.values())
        
        with db.lock:
            with db.connection:
                db.cursor.execute("SELECT name FROM families WHERE id = %s", (attacker_id,))
                att_res = db.cursor.fetchone()
                attacker_name = att_res[0] if att_res else "Невідомі"
                
                db.cursor.execute("SELECT balance, name FROM families WHERE id = %s", (target_id,))
                t_data = db.cursor.fetchone()
                target_balance = t_data[0] if t_data else 0
                target_name = t_data[1] if t_data else "Невідомі"

        my_roll = my_power * random.uniform(0.8, 1.2)
        target_roll = target_power * random.uniform(0.8, 1.2)
        
        loot = 0
        if my_roll >= target_roll:
            loot = int(target_balance * random.uniform(0.1, 0.15))
            with db.lock:
                with db.connection:
                    db.cursor.execute("UPDATE families SET balance = balance - %s, shield_until = CURRENT_TIMESTAMP + INTERVAL '4 hours', under_attack_until = NULL WHERE id = %s", (loot, target_id))
                    db.cursor.execute("UPDATE families SET balance = balance + %s WHERE id = %s", (loot, attacker_id))
                    db.connection.commit()
            atk_msg = f"✅ <b>Рейд завершено!</b>\nМи розгромили <b>{target_name}</b> та викрали <b>{loot}</b> 🪙"
            def_msg = f"💔 <b>Нас пограбували!</b>\nСім'я <b>{attacker_name}</b> викрала <b>{loot}</b> 🪙. Увімкнено щит на 4г."
        else:
            with db.lock:
                with db.connection:
                    # ВИПРАВЛЕНО: додано кому (target_id,)
                    db.cursor.execute("UPDATE families SET under_attack_until = NULL WHERE id = %s", (target_id,))
                    db.connection.commit()
            atk_msg = f"💥 <b>Поразка в рейді!</b>\nЗахист <b>{target_name}</b> виявився сильнішим. Флот повернувся ні з чим."
            def_msg = f"🛡 <b>Напад відбито!</b>\nСім'я <b>{attacker_name}</b> намагалася нас атакувати, але наші системи захисту впорались!"

        # Розсилка фінальних звітів
        for fid, msg in [(attacker_id, atk_msg), (target_id, def_msg)]:
            with db.lock:
                with db.connection:
                    db.cursor.execute("SELECT user_id FROM users WHERE family_id = %s", (fid,))
                    users = [r[0] for r in db.cursor.fetchall()]
            for uid in users:
                try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": str(uid), "text": msg, "parse_mode": "HTML"})
                except: pass
    except Exception as e:
        print("BATTLE ERROR:", e)


# === API ЗАПУСКУ АТАКИ З САЙТУ ===
@app.route('/api/raid/attack', methods=['POST'])
def attack_target():
    data = request.json
    attacker_id, target_id, r_time = data['family_id'], data['target_id'], data['raid_time']
    try:
        with db.lock:
            with db.connection:
                # Перевірки перед атакою
                db.cursor.execute("SELECT last_raid_time FROM families WHERE id = %s", (attacker_id,))
                last_r = db.cursor.fetchone()
                if last_r and last_r[0] and last_r[0] > datetime.datetime.now():
                    return jsonify({'error': 'Ваш флот вже у польоті!'})

                db.cursor.execute("SELECT under_attack_until FROM families WHERE id = %s", (target_id,))
                t_attack = db.cursor.fetchone()
                if t_attack and t_attack[0] and t_attack[0] > datetime.datetime.now():
                    return jsonify({'error': 'Ця колонія вже під облогою!'})

                # Встановлюємо статус облоги та кулдаун
                end_attack = datetime.datetime.now() + datetime.timedelta(minutes=r_time)
                db.cursor.execute("UPDATE families SET under_attack_until = %s WHERE id = %s", (end_attack, target_id))
                db.cursor.execute("UPDATE families SET last_raid_time = %s WHERE id = %s", (datetime.datetime.now() + datetime.timedelta(minutes=r_time*2), attacker_id))
                db.connection.commit()
                
                # Отримуємо імена для гарних сповіщень
                db.cursor.execute("SELECT name FROM families WHERE id = %s", (attacker_id,))
                attacker_name = db.cursor.fetchone()[0]
                db.cursor.execute("SELECT name FROM families WHERE id = %s", (target_id,))
                target_name = db.cursor.fetchone()[0]

        # МИТТЄВІ СПОВІЩЕННЯ В TELEGRAM
        def notify(fid, text):
            with db.lock:
                with db.connection:
                    db.cursor.execute("SELECT user_id FROM users WHERE family_id = %s", (fid,))
                    uids = [r[0] for r in db.cursor.fetchall()]
            for uid in uids:
                try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": str(uid), "text": text, "parse_mode": "HTML"})
                except: pass

        notify(attacker_id, f"🚀 <b>Рейд почався!</b>\nНаш флот атакує <b>{target_name}</b>. Повернення через {r_time} хв.")
        notify(target_id, f"⚠️ <b>ТРИВОГА! НА НАС НАПАЛИ!</b>\nСім'я <b>{attacker_name}</b> почала штурм нашої колонії! Бій відбудеться через {r_time} хв.")

        # Запускаємо фоновий процес (переводимо хвилини в секунди * 60)
        threading.Timer(r_time * 60, process_raid_battle, args=(attacker_id, target_id, r_time)).start()
        return jsonify({'success': True, 'win': True})
    except Exception as e: 
        print("ATTACK ERROR:", e)
        return jsonify({'error': str(e)}), 500
    
# --- АПІ ДЛЯ СІМЕЙНОГО ЧАТУ ---

@app.route('/api/chat/init', methods=['GET'])
def chat_init():
    user_id_raw = request.args.get('user_id')
    if not user_id_raw: return jsonify({'error': 'No user_id'}), 400
    
    user_id = int(user_id_raw)
    family_id = db.get_user_family(user_id)
    
    if not family_id:
        return jsonify({'error': 'Ви не перебуваєте в сім\'ї!'}), 403
        
    db.ping_user_activity(user_id)
    family_data = db.get_family(family_id)
    
    if not family_data:
        return jsonify({'error': 'Сім\'ю не знайдено'}), 404
        
    return jsonify({
        'family_id': family_id, 
        'family_name': family_data[1] 
    })

@app.route('/api/chat/sync', methods=['GET'])
def chat_sync():
    family_id = request.args.get('family_id')
    user_id = request.args.get('user_id')
    
    if user_id: db.ping_user_activity(int(user_id))
        
    messages = db.get_chat_messages(family_id)
    statuses = db.get_family_members_status(family_id)
    
    msg_data = [{
        'user_id': str(m[0]), 'username': m[1], 'text': m[2], 
        'time': m[3].strftime("%H:%M") if m[3] else ""
    } for m in messages]
    
    status_data = [{
        'user_id': str(s[0]), 'username': s[1], 'role': s[2], 'is_online': s[3]
    } for s in statuses]
    
    return jsonify({'messages': msg_data, 'members': status_data})

@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    data = request.json
    family_id = data.get('family_id')
    user_id = data.get('user_id')
    username = data.get('username')
    text = data.get('text')
    
    if not text.strip(): return jsonify({'error': 'Empty message'}), 400
    
    # 1. Зберігаємо повідомлення в базу та оновлюємо активність відправника
    db.ping_user_activity(int(user_id))
    db.add_chat_message(family_id, user_id, username, text)
    
    # 2. Отримуємо статуси всіх учасників (хто онлайн, а хто ні)
    statuses = db.get_family_members_status(family_id)
            
    # 3. Розсилаємо сповіщення ТІЛЬКИ ОФЛАЙН гравцям
    for s in statuses:
        mem_id = str(s[0])
        is_online = s[3] # Це значення True, якщо гравець був активний останні 2 хвилини
        
        # Відправляємо сповіщення всім, ОКРІМ самого відправника І ТІЛЬКИ ЯКЩО ВОНИ ОФЛАЙН
        if mem_id != str(user_id) and not is_online:
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                msg_text = f"💬 <b>Нове повідомлення в чаті сім'ї!</b>\nВід: <b>{username}</b>\n\n<i>«{text}»</i>"
                
                # Формуємо безпечне посилання для кнопки
                base_url = request.host_url.replace("http://", "https://")
                chat_url = f"{base_url}chat.html?user_id={mem_id}&family_id={family_id}"
                
                keyboard = {
                    "inline_keyboard": [[{"text": "📱 Відкрити Чат", "web_app": {"url": chat_url}}]]
                }
                
                requests.post(url, json={
                    "chat_id": mem_id, 
                    "text": msg_text, 
                    "parse_mode": "HTML", 
                    "reply_markup": keyboard
                })
            except Exception as e:
                print(f"Chat Notification Error: {e}")

    return jsonify({'success': True})
def run_flask():
    # Port 5000 стандартний, Render сам його прокине
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)