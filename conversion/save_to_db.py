import json
from pathlib import Path
import sqlite3
from storage.db import DB_PATH, init_db


def save_parsed_result(json_path: Path):
    """Сохраняет разобранный протокол и его показатели в SQLite"""

    if not json_path.exists():
        raise FileNotFoundError(f"❗ JSON не найден: {json_path}")

    # ✅ читаем JSON
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # ✅ инициализация БД (создание таблиц при первом запуске)
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    header = data.get("header", {})

    # ✅ вставляем протокол
    cur.execute("""
        INSERT INTO protocols (
            file_name,
            sample_place,
            sampling_datetime,
            documents,
            product_group,
            product_name,
            manufacture_date,
            test_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        json_path.stem,                          # file_name
        header.get("sample_place"),
        header.get("sampling_datetime"),
        header.get("documents"),
        header.get("product_group"),
        header.get("product_name"),
        header.get("manufacture_date"),
        header.get("test_date"),
    ))

    protocol_id = cur.lastrowid

    # ✅ вставляем показатели
    indicators = data.get("indicators", [])

    for item in indicators:
        cur.execute("""
            INSERT INTO indicators (
                protocol_id,
                name,
                norm,
                result,
                unit,
                page
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            protocol_id,
            item.get("name", ""),
            item.get("norm", ""),
            item.get("result", ""),
            item.get("unit", ""),
            item.get("page", None)
        ))

    conn.commit()
    conn.close()

    print(f"✅ сохранено в БД: protocol_id={protocol_id}")


if __name__ == "__main__":
    save_parsed_result(Path("parsed/parsed_result.json"))
