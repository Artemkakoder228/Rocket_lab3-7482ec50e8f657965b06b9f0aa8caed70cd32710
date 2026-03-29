from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import Database
import datetime
import random
import os
import requests
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

@app.route('/api/fortune/check', methods=['GET'])
def fortune_check():
    family_id = request.args.get('family_id')
    if not family_id: return jsonify({'error': 'Не вказано ID'}), 400
    
    can_spin, time_left = db.check_fortune(family_id)
    return jsonify({'can_spin': can_spin, 'time_left': time_left})

@app.route('/api/fortune/spin', methods=['POST'])
def fortune_spin():
    data = request.json
    family_id = data.get('family_id')
    user_id = data.get('user_id')
    reward_type = data.get('type')
    amount = data.get('amount')
    
    can_spin, time_left = db.check_fortune(family_id)
    if not can_spin:
        return jsonify({'success': False, 'error': f'Колесо перезаряджається. Залишилось: {time_left}'})
        
    db.claim_fortune(family_id, reward_type, amount)
    
    # Відправляємо повідомлення в Telegram
    type_names = {
        'coins': '🪙 Монет', 'iron': '🪨 Заліза', 'fuel': '⛽ Палива',
        'silicon': '💠 Кремнію', 'oxide': '🔴 Оксиду', 
        'regolith': '🌑 Реголіту', 'he3': '💨 Гелію-3'
    }
    
    name = type_names.get(reward_type, 'Ресурсів')
    msg = f"🎡 <b>КОЛЕСО ФОРТУНИ</b>\n━━━━━━━━━━━━━━━━━━━━━\nВи успішно крутнули колесо і виграли:\n🎁 <b>{amount} {name}</b>!"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": user_id, "text": msg, "parse_mode": "HTML"})
    
    return jsonify({'success': True})
    
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

def run_flask():
    # Port 5000 стандартний, Render сам його прокине
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)