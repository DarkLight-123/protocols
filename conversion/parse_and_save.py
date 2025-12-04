"""
Запуск полного цикла обработки:
1) OCR Surya → parsed_result.json
2) Адаптация под систему коллеги
3) Обогащение таблицы выводами
4) Запись в БД
"""

from pathlib import Path

from conversion.parser import parse_pdf_to_json   # наш новый парсер Surya
from league_sert.data_preparation.surya_adapter import load_surya_data
from league_sert.db_operations.db_writer import write_tables_to_db


def process_protocol(pdf_path: str | Path):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Файл не найден: {pdf_path}")

    # ---------------------------------------------
    # 1) OCR → parsed_result.json
    # ---------------------------------------------
    json_path = parse_pdf_to_json(pdf_path)

    # ---------------------------------------------
    # 2) Преобразуем в формат системы коллеги
    # ---------------------------------------------
    collector = load_surya_data(json_path)

    # collector.data_from_tables теперь полностью готова структура
    tables = collector.data_from_tables

    # ---------------------------------------------
    # 3) Сохраняем в базу через существующий pipeline коллеги
    # ---------------------------------------------
    write_tables_to_db(tables)

    print("✔ Готово: файл обработан и записан в БД!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python -m conversion.parse_and_save path/to/pdf")
        exit(1)

    process_protocol(sys.argv[1])
