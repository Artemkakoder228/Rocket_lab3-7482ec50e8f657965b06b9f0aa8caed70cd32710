import sqlite3

def init_resources_db():
    # Підключаємося до файлу resourses.db
    conn = sqlite3.connect('resourses.db')
    c = conn.cursor()
    
    # Створюємо таблицю storage для зберігання ресурсів та статусу бонуса
    c.execute("""
        CREATE TABLE IF NOT EXISTS storage (
            family_id INTEGER PRIMARY KEY,
            res_iron INTEGER DEFAULT 0,
            res_fuel INTEGER DEFAULT 0,
            res_regolith INTEGER DEFAULT 0,
            res_he3 INTEGER DEFAULT 0,
            res_silicon INTEGER DEFAULT 0,
            res_oxide INTEGER DEFAULT 0,
            res_hydrogen INTEGER DEFAULT 0,
            res_helium INTEGER DEFAULT 0,
            bonus_received BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("✅ База resourses.db успішно створена.")

if __name__ == "__main__":
    init_resources_db()