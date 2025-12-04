from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "protocols.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS protocols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            sample_place TEXT,
            sampling_datetime TEXT,
            documents TEXT,
            product_group TEXT,
            product_name TEXT,
            manufacture_date TEXT,
            test_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocol_id INTEGER,
            name TEXT,
            norm TEXT,
            result TEXT,
            unit TEXT,
            page INTEGER,
            FOREIGN KEY(protocol_id) REFERENCES protocols(id)
        )
    """)

    conn.commit()
    conn.close()
