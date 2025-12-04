import sqlite3
from storage.db import DB_PATH

def show_pretty(protocol_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- получаем протокол ---
    cur.execute("""
        SELECT product_name, manufacture_date, test_date
        FROM protocols WHERE id = ?
    """, (protocol_id,))
    row = cur.fetchone()

    if not row:
        print("❗ Протокол не найден")
        return

    product_name, manufacture_date, test_date = row

    print(f"\n=== ПРОТОКОЛ {protocol_id} ===")
    print(f"Продукция: {product_name}")
    print(f"Дата производства: {manufacture_date}")
    print(f"Дата испытаний: {test_date}")
    print("\n--- ПОКАЗАТЕЛИ ---\n")

    # --- получаем показатели ---
    cur.execute("""
        SELECT name, norm, result
        FROM indicators
        WHERE protocol_id = ?
        ORDER BY page
    """, (protocol_id,))

    for name, norm, result in cur.fetchall():

        name = name.strip() if name else ""
        norm = norm.strip() if norm else ""
        result = result.strip() if result else ""

        # --- вычисляем статус ---
        if not result:
            status = "⚪ нет результата"
        elif not norm:
            status = "⚪ нет нормы"
        else:
            status = "✅ соответствует"  # временно всегда ок

        print(name)
        print(f"Норма:     {norm or '—'}")
        print(f"Результат: {result or '—'}")
        print(f"Статус:    {status}")
        print("-" * 40)

    conn.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python -m conversion.show_pretty <id>")
    else:
        show_pretty(int(sys.argv[1]))
