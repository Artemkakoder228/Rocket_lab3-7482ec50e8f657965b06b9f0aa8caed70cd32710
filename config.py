BOT_TOKEN = "8578542989:AAFsaR62n5S3Wkh9RW4Ljdh98HuNLQd96OQ"
WEB_APP_URL = "https://kevin-substructural-luz.ngrok-free.dev"
WEB_APP_URL1 = "https://kevin-substructural-luz.ngrok-free.dev/tree_Earth.html"
CATALOG = {
    # --- ЗЕМЛЯ (Earth) ---
    'gu1': {'name': 'Конус-верхівка', 'type': 'nose', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'aerodynamics': 10}},
    'gu2': {'name': 'Сенсорний шпиль', 'type': 'nose', 'tier': 'II', 'cost': {'iron': 400, 'fuel': 150, 'coins': 250}, 'stats': {'aerodynamics': 25}},
    
    'nc1': {'name': 'Корпус', 'type': 'body', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'armor': 50}},
    'h1': {'name': 'Сталевий Корпус', 'type': 'body', 'tier': 'II', 'cost': {'iron': 600, 'fuel': 200, 'coins': 400}, 'stats': {'armor': 120}},
    
    'e1': {'name': 'Турбіна', 'type': 'engine', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'speed': 30}},
    'e2': {'name': 'Турбо-нагнітач', 'type': 'engine', 'tier': 'II', 'cost': {'iron': 500, 'fuel': 300, 'coins': 500}, 'stats': {'speed': 75}},
    
    'a1': {'name': 'Надкрилки', 'type': 'fins', 'tier': 'I', 'cost': {'iron': 0, 'fuel': 0, 'coins': 0}, 'stats': {'handling': 15}},
    'a2': {'name': 'Активні закрилки', 'type': 'fins', 'tier': 'II', 'cost': {'iron': 300, 'fuel': 150, 'coins': 350}, 'stats': {'handling': 40}},

    # --- МІСЯЦЬ (Moon) ---
    'root1': {'name': 'Сталевий Корпус', 'type': 'body', 'tier': 'II', 'cost': {'regolith': 0, 'he3': 0, 'coins': 0}, 'stats': {'armor': 120}},
    'branch1_up1': {'name': 'Вантажний Відсік', 'type': 'body', 'tier': 'III', 'cost': {'regolith': 500, 'he3': 200, 'coins': 800}, 'stats': {'armor': 200}},
    'branch1_up2': {'name': 'Сонячні Панелі', 'type': 'body', 'tier': 'IV', 'cost': {'regolith': 700, 'he3': 400, 'coins': 1200}, 'stats': {'armor': 250}},
    'branch1_down1': {'name': 'Аеро-надкрилки', 'type': 'fins', 'tier': 'III', 'cost': {'regolith': 400, 'he3': 150, 'coins': 900}, 'stats': {'handling': 65}},

    'root2': {'name': 'Турбо-нагнітач', 'type': 'engine', 'tier': 'II', 'cost': {'regolith': 0, 'he3': 0, 'coins': 0}, 'stats': {'speed': 75}},
    'branch2_up': {'name': 'Турбо-Форсаж', 'type': 'engine', 'tier': 'III', 'cost': {'regolith': 800, 'he3': 600, 'coins': 1500}, 'stats': {'speed': 150}},
    'branch2_down': {'name': 'Бокові Рушії', 'type': 'engine', 'tier': 'II', 'cost': {'regolith': 600, 'he3': 400, 'coins': 1000}, 'stats': {'speed': 100}},

    'root3': {'name': 'Сенсорний шпиль', 'type': 'nose', 'tier': 'II', 'cost': {'regolith': 0, 'he3': 0, 'coins': 0}, 'stats': {'aerodynamics': 25}},
    'branch3': {'name': 'Керамічний Щит', 'type': 'nose', 'tier': 'III', 'cost': {'regolith': 500, 'he3': 300, 'coins': 1100}, 'stats': {'aerodynamics': 55}},

    # --- МАРС (Mars) ---
    'g1_1': {'name': 'Вантажний Відсік', 'type': 'body', 'tier': 'III', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'armor': 200}},
    'g1_2': {'name': 'Герметизація', 'type': 'body', 'tier': 'IV', 'cost': {'silicon': 900, 'oxide': 500, 'coins': 2500}, 'stats': {'armor': 450}},
    'g1_up': {'name': 'Панель Оновлення', 'type': 'body', 'tier': 'III', 'cost': {'silicon': 1200, 'oxide': 800, 'coins': 3500}, 'stats': {'armor': 350}},
    'g1_down': {'name': 'Сонячні Панелі', 'type': 'body', 'tier': 'V', 'cost': {'silicon': 1000, 'oxide': 600, 'coins': 3000}, 'stats': {'armor': 600}},
    'g1_end': {'name': 'Нові Панелі MK-II', 'type': 'body', 'tier': 'VI', 'cost': {'silicon': 1500, 'oxide': 1000, 'coins': 5000}, 'stats': {'armor': 900}},

    'g2_1': {'name': 'Турбо-Форсаж', 'type': 'engine', 'tier': 'III', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'speed': 150}},
    'g2_up': {'name': 'Покращений Форсаж', 'type': 'engine', 'tier': 'IV', 'cost': {'silicon': 1800, 'oxide': 1200, 'coins': 4500}, 'stats': {'speed': 320}},
    'g2_down': {'name': 'Бокові Турбіни', 'type': 'engine', 'tier': 'III', 'cost': {'silicon': 1200, 'oxide': 800, 'coins': 3200}, 'stats': {'speed': 210}},

    'g3_a1': {'name': 'Керамічний Щит', 'type': 'nose', 'tier': 'III', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'aerodynamics': 55}},
    'g3_a2': {'name': 'Нова Верхівка', 'type': 'nose', 'tier': 'IV', 'cost': {'silicon': 1100, 'oxide': 600, 'coins': 2800}, 'stats': {'aerodynamics': 90}},
    'g3_b1': {'name': 'Бластер', 'type': 'weapons', 'tier': 'I', 'cost': {'silicon': 0, 'oxide': 0, 'coins': 0}, 'stats': {'damage': 40}},
    'g3_b2': {'name': 'Покращений Бластер', 'type': 'weapons', 'tier': 'II', 'cost': {'silicon': 2000, 'oxide': 1500, 'coins': 5000}, 'stats': {'damage': 110}},

    # --- ЮПІТЕР (Jupiter) ---
    'hull_start': {'name': 'Герметизація', 'type': 'body', 'tier': 'IV', 'cost': {'hydrogen': 0, 'helium': 0, 'coins': 0}, 'stats': {'armor': 450}},
    'hull_mk2': {'name': 'Композитний Корпус', 'type': 'body', 'tier': 'V', 'cost': {'hydrogen': 3000, 'helium': 2000, 'coins': 8000}, 'stats': {'armor': 1200}},
    'solar_upg': {'name': 'Фотоелементи MK-2', 'type': 'body', 'tier': 'VII', 'cost': {'hydrogen': 4000, 'helium': 2500, 'coins': 10000}, 'stats': {'armor': 1800}},
    'solar_max': {'name': 'Квантові Панелі', 'type': 'body', 'tier': 'VIII', 'cost': {'hydrogen': 6000, 'helium': 4000, 'coins': 15000}, 'stats': {'armor': 3000}},
    'aux_bay': {'name': 'Допоміжні Відсіки', 'type': 'body', 'tier': 'V', 'cost': {'hydrogen': 3500, 'helium': 2500, 'coins': 7500}, 'stats': {'armor': 1000}},
    'combat_bay': {'name': 'Бойовий Модуль', 'type': 'body', 'tier': 'VI', 'cost': {'hydrogen': 5500, 'helium': 4500, 'coins': 12000}, 'stats': {'armor': 1500}},
    'cannons': {'name': 'Плазмові Гармати', 'type': 'weapons', 'tier': 'I', 'cost': {'hydrogen': 8000, 'helium': 6000, 'coins': 20000}, 'stats': {'damage': 350}},

    'eng_start': {'name': 'Форсаж', 'type': 'engine', 'tier': 'IV', 'cost': {'hydrogen': 0, 'helium': 0, 'coins': 0}, 'stats': {'speed': 320}},
    'eng_ultimate': {'name': 'Гіпер-Турбіна', 'type': 'engine', 'tier': 'V', 'cost': {'hydrogen': 9000, 'helium': 7000, 'coins': 18000}, 'stats': {'speed': 800}},
    'eng_side': {'name': 'Бокові Рушії', 'type': 'engine', 'tier': 'IV', 'cost': {'hydrogen': 2500, 'helium': 1500, 'coins': 7000}, 'stats': {'speed': 450}},

    'nose_start': {'name': 'Титановий Конус', 'type': 'nose', 'tier': 'IV', 'cost': {'hydrogen': 0, 'helium': 0, 'coins': 0}, 'stats': {'aerodynamics': 90}},
    'nose_adv': {'name': 'Аеро-Композит', 'type': 'nose', 'tier': 'V', 'cost': {'hydrogen': 4500, 'helium': 3000, 'coins': 9000}, 'stats': {'aerodynamics': 200}},
}