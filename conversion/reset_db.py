from storage.db import DB_PATH, init_db
import os

def reset_db():
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print(f"🗑 База удалена: {DB_PATH}")
    else:
        print("⚪ Базы не было — удалять нечего")

    init_db()
    print("✅ Создана новая пустая база данных")

if __name__ == "__main__":
    reset_db()
