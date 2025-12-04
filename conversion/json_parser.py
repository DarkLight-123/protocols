import json
from pathlib import Path
import re

WORD_FILES_DIR = Path("word_files")
OUTPUT_DIR = Path("parsed")
OUTPUT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# 🔥 МУСОРНЫЕ ШАБЛОНЫ
# -------------------------------------------------

SKIP_PATTERNS = [
    r"ооо", r"лига\-сер", r"лаборат", r"общество",
    r"тел", r"e[- ]?mail", r"лист", r"протокол",
    r"подпись", r"адрес", r"магазин",
    r"109383", r"москва", r"брянск",
    r"витрин", r"дба", r"м/сек",
]

SKIP_REGEX = re.compile("|".join(SKIP_PATTERNS), flags=re.IGNORECASE)

# -------------------------------------------------
# ✅ HEADER КЛЮЧИ
# -------------------------------------------------

HEADER_KEYS = {
    "место отбора проб": "sample_place",
    "дата и время отбора": "sampling_datetime",
    "сопроводительные документы": "documents",
    "группа продукции": "product_group",
    "наименование продукции": "product_name",
    "дата производства": "manufacture_date",
    "дата проведения исследований": "test_date",
}

HEADER_FRAGMENTS = tuple(HEADER_KEYS.keys())

# -------------------------------------------------
# ✨ HELPERS
# -------------------------------------------------

def normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"<.*?>", "", text)
    text = text.replace("\xa0", " ")
    return text


def looks_like_trash(text: str) -> bool:

    if any(key in text.lower() for key in HEADER_FRAGMENTS):
        return False

    if not text or len(text) < 3:
        return True

    if SKIP_REGEX.search(text):
        return True

    if text in {".", "-", "_", "—"}:
        return True

    return False


def is_numeric_value(text: str) -> bool:
    return bool(re.search(r"\d", text))


# -------------------------------------------------
# ✅ STATUS CHECKING
# -------------------------------------------------

def parse_number(val):
    val = val.replace(",", ".")
    m = re.search(r"(\d+(\.\d+)?)", val)
    return float(m.group(1)) if m else None

def check_status(norm, result):

    if not norm or not result:
        return "⚪ нельзя определить"

    norm_low = norm.lower()

    # RANGE  1.5–3.0
    if " - " in norm or "–" in norm or "-" in norm:
        nums = re.split(r"[–\-]", norm.replace(",", "."))
        if len(nums) >= 2:
            low = parse_number(nums[0])
            high = parse_number(nums[1])
            res = parse_number(result)
            if low and high and res:
                return "✅ соответствует" if low <= res <= high else "❌ вне нормы"

    # "до 0,3"
    if "до" in norm_low:
        limit = parse_number(norm)
        res = parse_number(result)
        if limit and res:
            return "✅ соответствует" if res <= limit else "❌ выше нормы"

    # "не более"
    if "не более" in norm_low:
        limit = parse_number(norm)
        res = parse_number(result)
        if limit and res:
            return "✅ соответствует" if res <= limit else "❌ выше нормы"

    # "менее"
    if "менее" in norm_low:
        limit = parse_number(norm)
        res = parse_number(result)
        if limit and res:
            return "✅ соответствует" if res < limit else "❌ выше нормы"

    return "⚪ нельзя определить"


# -------------------------------------------------
# 📄 PROCESS PAGE
# -------------------------------------------------

def process_page(items, page_num):
    lines = []
    indicators = []

    for obj in items:
        t = normalize(obj.get("text", ""))
        if not looks_like_trash(t):
            lines.append(t)

    i = 0
    while i < len(lines):
        name = lines[i]
        norm = result = ""

        # ищем максимум 3 строки вперед
        for j in range(1, 4):
            if i + j >= len(lines):
                break

            nxt = lines[i + j]

            # norm candidate
            if any(w in nxt.lower() for w in ["не допуска", "не обнаруж", "до", "не более", "менее"]) \
               or re.search(r"\d.*[-–].*\d", nxt):
                norm = nxt
                continue

            # result numeric
            if is_numeric_value(nxt) and not norm:
                result = nxt

        # сохраняем если есть хотя бы одно
        if norm or result:
            status = check_status(norm, result)
            indicators.append({
                "name": name,
                "norm": norm,
                "result": result,
                "status": status,
                "page": page_num
            })

        i += 1

    return lines, indicators


# -------------------------------------------------
# ✅ HEADER
# -------------------------------------------------

def find_header(lines):
    header = {}
    DATE_REGEX = re.compile(r"\d{2}\.\d{2}\.\d{4}")

    for i, line in enumerate(lines):
        low = line.lower()

        for key, field in HEADER_KEYS.items():
            if key in low:
                if ":" in line:
                    val = line.split(":", 1)[1].strip()
                    header[field] = val
                else:
                    if i + 1 < len(lines):
                        header[field] = lines[i + 1]
                break

    return header


# -------------------------------------------------
# 🚀 MAIN
# -------------------------------------------------

def run():
    json_files = sorted(WORD_FILES_DIR.glob("*_page_*.json"))

    if not json_files:
        print("❗ JSON страниц не найдено")
        return

    all_lines = []
    indicators = []

    for jf in json_files:
        data = json.loads(jf.read_text(encoding="utf-8"))
        page_num = int(jf.stem.split("_page_")[-1])

        lines, inds = process_page(data, page_num)

        all_lines.extend(lines)
        indicators.extend(inds)
        print(f"✅ {jf.name}: {len(inds)} показателей")

    header = find_header(all_lines)

    out_path = OUTPUT_DIR / "parsed_result.json"
    out_path.write_text(json.dumps({
        "header": header,
        "indicators": indicators
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== ИТОГО ПОКАЗАТЕЛЕЙ === {len(indicators)}")
    print(f"💾 Сохранено в: {out_path.resolve()}")
    print("✅ Готово!")


if __name__ == "__main__":
    run()
