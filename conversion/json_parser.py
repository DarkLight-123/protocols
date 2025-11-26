import json
from pathlib import Path
from collections import defaultdict

WORD_FILES_DIR = Path("word_files")

# минимальный порог: строки ниже будут игнорироваться (убираем шапки, подписи)
MIN_TEXT_LENGTH = 3


def load_page(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def group_lines_into_rows(lines, y_threshold=8):
    """
    Объединяет строки в одну "строку таблицы" по координате Y.
    """
    rows = []
    for line in lines:
        y = line["bbox"][1]
        text = line["text"].strip()

        if not text or len(text) < MIN_TEXT_LENGTH:
            continue

        if not rows:
            rows.append({"y": y, "cells": [text], "bboxes": [line["bbox"]]})
            continue

        if abs(y - rows[-1]["y"]) <= y_threshold:
            rows[-1]["cells"].append(text)
            rows[-1]["bboxes"].append(line["bbox"])
        else:
            rows.append({"y": y, "cells": [text], "bboxes": [line["bbox"]]})

    return rows


def extract_table_from_page(json_path: Path):
    data = load_page(json_path)
    rows = group_lines_into_rows(data)

    indicators = {}

    for row in rows:
        cells = row["cells"]

        # пропускаем строки из шапки
        if len(cells) < 3:
            continue

        name = cells[0]
        norm = cells[-2]
        result = cells[-1]

        # простая фильтрация норм и результатов
        if (
            any(x in norm for x in ["-", "≤", "≥"])
            or norm.replace(",", "").replace(".", "").isdigit()
        ) and ("±" in result or any(c.isdigit() for c in result)):
            indicators[name] = {
                "norm": norm,
                "result": result
            }

    return indicators


def parse_all_pages():
    json_files = sorted(WORD_FILES_DIR.glob("*_page_*.json"))

    all_data = defaultdict(dict)

    for json_file in json_files:
        page_data = extract_table_from_page(json_file)
        if page_data:
            print(f"✅ {json_file.name}: {len(page_data)} показателей")
            all_data.update(page_data)
        else:
            print(f"⚪ {json_file.name}: нет данных")

    print("\n=== ИТОГО ===")
    print(f"Всего показателей: {len(all_data)}\n")

    for k, v in all_data.items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    parse_all_pages()
