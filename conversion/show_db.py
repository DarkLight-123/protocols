import argparse
import sqlite3
from storage.db import DB_PATH


def show_all_protocols():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT id, file_name, product_name, manufacture_date, test_date
        FROM protocols
        ORDER BY id
    """).fetchall()

    print("\n=== ВСЕ ПРОТОКОЛЫ ===")
    if not rows:
        print("❗ В базе пока нет протоколов")
    else:
        for r in rows:
            print(f"ID={r[0]} | {r[1]} | {r[2]} | {r[3]} → {r[4]}")

    conn.close()


def show_protocol_details(protocol_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    protocol = cur.execute("""
        SELECT file_name, product_name, manufacture_date, test_date
        FROM protocols
        WHERE id = ?
    """, (protocol_id,)).fetchone()

    if not protocol:
        print(f"❗ Протокол с id={protocol_id} не найден")
        conn.close()
        return

    print(f"\n=== ПРОТОКОЛ {protocol_id} ===")
    print(f"Файл: {protocol[0]}")
    print(f"Продукция: {protocol[1]}")
    print(f"Дата производства: {protocol[2]}")
    print(f"Дата испытаний: {protocol[3]}")

    indicators = cur.execute("""
        SELECT name, norm, result, page
        FROM indicators
        WHERE protocol_id = ?
        ORDER BY page
    """, (protocol_id,)).fetchall()

    print(f"\n--- ПОКАЗАТЕЛИ ({len(indicators)}) ---")
    if not indicators:
        print("Нет показателей")
    else:
        for name, norm, result, page in indicators:
            print(f"[стр. {page}] {name} | norm='{norm}' | result='{result}'")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Просмотр данных из БД")
    parser.add_argument("id", nargs="?", type=int, help="ID протокола")

    args = parser.parse_args()

    if args.id:
        show_protocol_details(args.id)
    else:
        show_all_protocols()
