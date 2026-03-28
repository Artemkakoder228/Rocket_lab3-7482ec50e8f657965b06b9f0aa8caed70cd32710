import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_1PhACa8zgNmd@ep-withered-fire-aiay68rh-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def update():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE families ADD COLUMN IF NOT EXISTS unlocked_planets TEXT DEFAULT 'Earth';")
        print("✅ Колонку unlocked_planets успішно додано!")
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update()