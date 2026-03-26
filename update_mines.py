import psycopg2
from database import DATABASE_URL

def update_mines():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    c = conn.cursor()
    
    try:
        print("Додаємо нові колонки для шахт...")
        c.execute("ALTER TABLE families ADD COLUMN mine_lvl_earth INTEGER DEFAULT 1;")
        c.execute("ALTER TABLE families ADD COLUMN mine_lvl_moon INTEGER DEFAULT 0;")
        c.execute("ALTER TABLE families ADD COLUMN mine_lvl_mars INTEGER DEFAULT 0;")
        c.execute("ALTER TABLE families ADD COLUMN mine_lvl_jupiter INTEGER DEFAULT 0;")
        
        c.execute("ALTER TABLE families ADD COLUMN last_coll_earth TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        c.execute("ALTER TABLE families ADD COLUMN last_coll_moon TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        c.execute("ALTER TABLE families ADD COLUMN last_coll_mars TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        c.execute("ALTER TABLE families ADD COLUMN last_coll_jupiter TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        print("✅ Базу успішно оновлено!")
    except Exception as e:
        print(f"⚠️ Помилка (можливо колонки вже існують): {e}")
        
if __name__ == "__main__":
    update_mines()