from database import Database

print("🔄 Підключення до бази даних Neon...")
db = Database()

with db.connection:
    print("🗑 Видалення всіх існуючих таблиць...")
    # Використовуємо CASCADE, щоб видалити таблиці разом з усіма залежностями (зовнішніми ключами)
    db.cursor.execute("""
        DROP TABLE IF EXISTS shop_purchases CASCADE;
        DROP TABLE IF EXISTS family_upgrades CASCADE;
        DROP TABLE IF EXISTS launches CASCADE;
        DROP TABLE IF EXISTS missions CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS families CASCADE;
    """)
    print("✅ Усі таблиці успішно видалено.")

# Викликаємо метод для повторного створення чистих таблиць
db.create_tables()
print("✅ Нові таблиці створено. База даних чиста!")