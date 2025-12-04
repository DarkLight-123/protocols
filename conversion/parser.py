import re
from dataclasses import dataclass
from typing import List, Dict, Any
import subprocess

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
    """Слегка чистим текст OCR."""
    if not text:
        return ""
    text = text.replace("•", "x").replace("■", "x").replace("х", "x").replace("Х", "x")
    text = text.replace("±", "±")
    return text.strip()


def merge_rows(ocr_items: List[Dict[str, Any]], y_threshold: float = 10.0) -> List[Row]:
    """
    Группируем объекты OCR от Surya по строкам на основе Y координат.
    """
    rows: List[Row] = []

    # Сортируем по вертикали (сверху вниз)
    items = [
        OCRItem(
            text=normalize(obj["text"]),
            x0=obj["x0"],
            y0=obj["y0"],
            x1=obj["x1"],
            y1=obj["y1"]
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

    # внутри строки — сортируем элементы слева направо
    for r in rows:
        r.items.sort(key=lambda i: i.x0)

    return rows


def row_to_text(row: Row) -> str:
    """Объединяем элементы строки в один текст (слева направо)."""
    return " ".join(i.text for i in row.items).strip()


def split_into_columns(row: Row) -> List[str]:
    """
    Пробуем определить логические колонки в таблице.
    Это критический момент — он делает модели устойчивыми.
    """
    positions = [i.x0 for i in row.items]
    if not positions:
        return [row_to_text(row)]

    # Heuristic:
    # если расстояние между словами > 120 px — считаем новой колонкой
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
# 3) Основной парсер страницы
# ================================

def parse_page(ocr_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Главный метод:
    - группируем строки
    - восстанавливаем "таблицу"
    - определяем хедер
    - определяем показатели (name, norm, result)
    """
    rows = merge_rows(ocr_items)

    table = [split_into_columns(r) for r in rows]

    header = {}
    indicators = []

    # Определим, где заканчивается header
    header_limit = 0
    for r in table:
        text = " ".join(r).lower()
        if any(k in text for k in ["массовая доля", "кислоты", "%", "доля", "норма"]):
            break
        header_limit += 1

    # HEADER
    header_rows = table[:header_limit]
    for r in header_rows:
        line = " ".join(r)
        if ":" in line:
            k, v = line.split(":", 1)
            header[k.strip()] = v.strip()
        else:
            # заголовки без ключей тоже сохраним
            header.setdefault("raw", []).append(line)

    # INDICATORS
    indicator_rows = table[header_limit:]

    for r in indicator_rows:
        if len(r) == 1:
            name = r[0]
            indicators.append({"name": name, "norm": None, "result": None})
        elif len(r) == 2:
            name, value = r
            # пытаемся угадать (норма или результат)
            if re.search(r"\d", value):
                indicators.append({"name": name, "norm": None, "result": value})
            else:
                indicators.append({"name": name, "norm": value, "result": None})
        elif len(r) >= 3:
            name = r[0]
            norm = r[1]
            res = r[2]
            indicators.append({"name": name, "norm": norm, "result": res})

    return {
        "header": header,
        "indicators": indicators
    }
from pathlib import Path
import json
import subprocess
import tempfile


def parse_pdf_to_json(pdf_path: str | Path) -> Path:
    """
    Выполнить OCR Surya и получить parsed_result.json.
    Возвращает путь к json-файлу.
    """

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")

    # Временная директория для OCR результата
    out_dir = Path(tempfile.mkdtemp(prefix="surya_out_"))

    json_path = out_dir / "parsed_result.json"

    # Вызов Surya OCR через subprocess
    cmd = [
        "surya-ocr",
        "layout",
        str(pdf_path),
        "--out", str(json_path)
    ]

    print("🔥 Запускаю OCR Surya...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Ошибка OCR Surya:")
        print(result.stderr)
        raise RuntimeError("Surya OCR failed")

    if not json_path.exists():
        raise RuntimeError("OCR завершён, но parsed_result.json не найден")

    print(f"✔ OCR завершён. JSON сохранён: {json_path}")
    return json_path

