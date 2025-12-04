"""
Модуль для парсинга PDF-файла с помощью Surya и вывода
результата в удобном для дальнейшей обработки виде.

Сейчас модуль:
- принимает путь к PDF;
- прогоняет через OCR Surya;
- передаёт текст в наш парсер;
- печатает результат и (опционально) сохраняет в .json рядом с файлом.

Дальше на этот результат мы подвяжем запись в БД через db_writer.
"""

import argparse
import json
from pathlib import Path

from conversion.parser import parse_pdf_to_json  # наш новый парсер Surya


def parse_pdf(pdf_path: Path, save_json: bool = True) -> dict:
    """
    Распарсить PDF и вернуть структуру данных.

    :param pdf_path: путь до pdf-файла
    :param save_json: сохранять ли результат в .json рядом с файлом
    :return: словарь с извлечёнными данными
    """
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Файл не найден: {pdf_path}")

    # 1. Парсим PDF в нашу структуру (через OCR Surya + разбор текста)
    data = parse_pdf_to_json(str(pdf_path))

    # 2. По желанию — сохраняем рядом JSON
    if save_json:
        json_path = pdf_path.with_suffix(".json")
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Результат сохранён в: {json_path}")

    # 3. Печатаем в консоль для быстрой проверки
    print("✅ Извлечённые данные:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    return data


def main():
    parser = argparse.ArgumentParser(
        description="Парсинг PDF протоколов с помощью Surya (без записи в БД пока)."
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="Путь до PDF-файла протокола",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Не сохранять .json рядом с PDF, только вывод в консоль",
    )

    args = parser.parse_args()
    pdf_path = Path(args.pdf_path)

    parse_pdf(pdf_path, save_json=not args.no_json)


if __name__ == "__main__":
    main()
