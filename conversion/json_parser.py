import json
from pathlib import Path
import re

WORD_FILES_DIR = Path("word_files")
OUTPUT_DIR = Path("parsed")
OUTPUT_DIR.mkdir(exist_ok=True)


# ----------------------------------------
# 🧹 Helpers
# ----------------------------------------

def normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"<.*?>", "", text)  # remove HTML/math tags
    return text


def is_potential_indicator(text: str) -> bool:
    """
    Determine if a line is likely a real indicator.
    We check for digits + threshold words.
    """
    t = text.lower()

    has_number = bool(re.search(r"\d", t))
    has_keywords = any(k in t for k in [
        "не допуска", "не обнаруж", "менее", "более", "до", "±", "-"
    ])

    return has_number and has_keywords


def is_header_key(text: str) -> bool:
    """
    Identify header fields based on stable key fragments.
    """
    HEADER_KEYS = [
        "место отбора",
        "дата и время отбора",
        "сопроводительные документы",
        "группа продукции",
        "наименование продукции",
        "дата производства",
        "изготовитель",
        "дата проведения исследований",
    ]
    t = text.lower()
    return any(k in t for k in HEADER_KEYS)


# ----------------------------------------
# 🔥 Extract from JSON page
# ----------------------------------------

def process_page(items):
    raw_lines = []
    header = {}
    indicators = {}

    buffer = []

    # collect cleaned text lines
    for obj in items:
        t = normalize(obj.get("text", ""))
        if not t:
            continue
        raw_lines.append(t)
        buffer.append(t)

    # try to extract header
    for line in buffer:
        if is_header_key(line):
            header[line] = ""  # value extraction can be improved later

    # extract indicators intelligently
    i = 0
    while i < len(buffer):
        name = buffer[i]

        norm = result = ""

        if i + 1 < len(buffer):
            nxt = buffer[i + 1]

            if is_potential_indicator(nxt):
                # classify numeric line as norm or result heuristically
                if any(w in nxt.lower() for w in ["не допуска", "не обнаруж", "до", "не более", "менее"]):
                    norm = nxt
                else:
                    result = nxt
                i += 2
            else:
                i += 1
        else:
            i += 1

        # only store valid indicators
        if norm or result:
            indicators[name] = {"norm": norm, "result": result}

    return raw_lines, header, indicators


# ----------------------------------------
# 🚀 Main runner
# ----------------------------------------

def run():
    json_files = sorted(WORD_FILES_DIR.glob("*_page_*.json"))
    if not json_files:
        print("❗ Не найдено JSON страниц")
        return

    print(f"✅ Найдено JSON-страниц: {len(json_files)}")

    full_raw = []
    full_header = {}
    full_indicators = {}

    for jf in json_files:
        data = json.loads(jf.read_text(encoding="utf-8"))
        raw, header, indicators = process_page(data)

        # accumulate results
        full_raw.extend(raw)
        full_header.update(header)
        full_indicators.update(indicators)

        print(f"✅ {jf.name}: {len(indicators)} показателей")

    # summary
    print("\n=== ИТОГО ===")
    print(f"Всего показателей: {len(full_indicators)}\n")

    for k, v in list(full_indicators.items())[:40]:
        print(f"- {k}: {v}")

    # save result JSON
    out_path = OUTPUT_DIR / "parsed_result.json"
    result = {
        "raw": full_raw,
        "header": full_header,
        "indicators": full_indicators,
    }
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n💾 Сохранено в: {out_path.resolve()}")
    print("✅ Готово!")


if __name__ == "__main__":
    run()
