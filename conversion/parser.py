import re
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


# ================================
# 1) Вспомогательные структуры
# ================================

@dataclass
class OCRItem:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class Row:
    y: float
    items: List[OCRItem]


# ================================
# 2) Утилиты
# ================================

def normalize(text: str) -> str:
    """Чистим текст OCR."""
    if not text:
        return ""
    text = text.replace("•", "x").replace("■", "x").replace("х", "x").replace("Х", "x")
    return text.strip()


def merge_rows(ocr_items: List[Dict[str, Any]], y_threshold: float = 10.0) -> List[Row]:
    rows: List[Row] = []

    items = [
        OCRItem(
            text=normalize(obj["text"]),
            x0=obj["x0"], y0=obj["y0"],
            x1=obj["x1"], y1=obj["y1"]
        )
        for obj in ocr_items
        if normalize(obj.get("text", "")) not in ["", None]
    ]

    items.sort(key=lambda i: i.y0)

    for item in items:
        if not rows:
            rows.append(Row(y=item.y0, items=[item]))
            continue

        last = rows[-1]
        if abs(item.y0 - last.y) <= y_threshold:
            last.items.append(item)
        else:
            rows.append(Row(y=item.y0, items=[item]))

    for r in rows:
        r.items.sort(key=lambda i: i.x0)

    return rows


def row_to_text(row: Row) -> str:
    return " ".join(i.text for i in row.items).strip()


def split_into_columns(row: Row) -> List[str]:
    positions = [i.x0 for i in row.items]
    if not positions:
        return [row_to_text(row)]

    cols = []
    current = [row.items[0].text]

    for prev, nxt in zip(row.items, row.items[1:]):
        if nxt.x0 - prev.x1 > 120:
            cols.append(" ".join(current))
            current = [nxt.text]
        else:
            current.append(nxt.text)

    cols.append(" ".join(current))
    return cols


# ================================
# 3) Поиск правильного results.json
# ================================

def find_surya_json(output_dir: Path) -> Path:
    """
    Surya создаёт вложенную папку → мы ищем results.json рекурсивно.
    Возвращаем НЕ пустой файл.
    """
    candidates = list(output_dir.rglob("results.json"))
    if not candidates:
        raise RuntimeError("❌ Surya не создала results.json вообще")

    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data:  # непустой JSON
                return path
        except Exception:
            continue

    return candidates[0]


# ================================
# 4) Извлечение строк из JSON Surya
# ================================

def extract_lines_from_surya(surya_json: dict) -> list[dict]:
    """
    Surya даёт структуру вида:

    {
        "<обрезанное_имя_pdf>": [
            { "text_lines": [...] },
            ...
        ]
    }

    Нужно:
      ✔ взять первый ключ
      ✔ пройтись по каждой странице
      ✔ вытянуть item["text"]
    """

    if not isinstance(surya_json, dict):
        raise ValueError("❌ Неверный формат Surya JSON — ожидается объект dict")

    keys = list(surya_json.keys())
    if not keys:
        return []

    first_key = keys[0]
    page_list = surya_json[first_key]  # это список страниц

    if not isinstance(page_list, list):
        raise ValueError("❌ Surya JSON: ожидается список страниц внутри ключа")

    pages_output = []

    for idx, page in enumerate(page_list, start=1):

        # Страница может быть строкой — это баг Surya → пропускаем
        if not isinstance(page, dict):
            continue

        lines = []
        for item in page.get("text_lines", []):
            if not isinstance(item, dict):
                continue
            text = item.get("text", "").strip()
            if text:
                lines.append(text)

        pages_output.append({
            "page": idx,
            "lines": lines
        })

    return pages_output


# ================================
# 5) Главная функция — PARSER API
# ================================

def parse_pdf_to_json(pdf_path: str) -> dict:
    """
    Полный цикл:
      1) Запуск Surya OCR
      2) Поиск нужного results.json
      3) Извлечение строк
      4) Возврат в нормальном формате
    """

    pdf_path = Path(pdf_path).resolve()
    out_dir = Path("results/surya") / pdf_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["surya_ocr", str(pdf_path), "--output_dir", str(out_dir)]
    print("🔥 Запускаю OCR Surya...")
    print(f"⚙️ Команда: {' '.join(cmd)}")

    subprocess.run(cmd, check=True)

    json_path = find_surya_json(out_dir)
    print(f"✅ Найден корректный OCR JSON: {json_path}")

    surya_json = json.loads(json_path.read_text(encoding="utf-8"))
    pages = extract_lines_from_surya(surya_json)

    return {
        "file": pdf_path.name,
        "pages": pages
    }
