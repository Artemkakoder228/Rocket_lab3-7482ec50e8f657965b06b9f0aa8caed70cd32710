from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_kb_no_family():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Створити сім'ю"), KeyboardButton(text="🔗 Приєднатися до сім'ї")]
        ], 
        resize_keyboard=True
    )

def get_main_kb_with_family():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌌 Кабінет сім'ї"), KeyboardButton(text="🛸 Ангар (Веб)")],
            [KeyboardButton(text="📡 Місії"), KeyboardButton(text="🏭 Інфраструктура")],
            [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="🎁 Вітальний бонус")],
            [KeyboardButton(text="🎲 Розваги"), KeyboardButton(text="⚔️ Рейд")],
            [KeyboardButton(text="👾 Космічний бій"), KeyboardButton(text="🚀 Навігація")],
            [KeyboardButton(text="❌ Покинути сім'ю")]
        ], 
        resize_keyboard=True
    )

def main_keyboard():
    """Заглушка для сумісності з іншими модулями"""
    return get_main_kb_with_family()

def get_missions_kb(planet):
    from database import Database
    db = Database('space.db')
    missions = db.get_missions_by_planet(planet)
    
    builder = ReplyKeyboardBuilder()
    # Іконки для характеристик
    icons = {"speed": "🚀", "armor": "🛡️", "aerodynamics": "🌬️", "handling": "🕹️", "damage": "⚔️"}

    for m in missions:
        # m[12] - тип стата, m[13] - значення
        req_type = m[12] if len(m) > 12 else "speed"
        req_val = m[13] if len(m) > 13 else 0
        icon = icons.get(req_type, "📊")
        
        btn_text = f"{m[1]} [{icon} {req_val}]"
        builder.button(text=btn_text)
    
    builder.adjust(1)
    builder.row(KeyboardButton(text="⬅️ Назад"))
    return builder.as_markup(resize_keyboard=True)

def get_navigation_kb():
    """Клавіатура вибору планет"""
    builder = ReplyKeyboardBuilder()
    planets = ["Earth", "Moon", "Mars", "Jupiter"]
    for planet in planets:
        builder.button(text=planet)
    builder.adjust(2)
    builder.row(KeyboardButton(text="⬅️ Назад"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_kb():
    """Клавіатура для адмін-панелі"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📢 Розсилка")],
            [KeyboardButton(text="💰 Видати монети"), KeyboardButton(text="⚙️ Налаштування")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )