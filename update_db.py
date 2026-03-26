from database import Database
db = Database('space.db')
try:
    with db.connection:
        db.cursor.execute("ALTER TABLE families ADD COLUMN unlocked_planets TEXT DEFAULT 'Earth';")
    print("✅ Базу оновлено успішно!")
except Exception as e:
    print(f"База вже оновлена або помилка: {e}")