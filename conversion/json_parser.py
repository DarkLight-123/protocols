import json
from pathlib import Path

JSON_FOLDER = Path("word_files")

def extract_indicators_from_page(page_data):
    indicators = {}

    for block in page_data:
        text = block.get("text", "").strip()

        # Пропускаем пустые строки и длинные описания
        if not text or len(text) > 120:
            continue

        # Находим строки, где есть два элемента (норма + результат)
        unit = block.get("unit")
        result = block.get("result")
        norm = block.get("norm")

        # Если есть хотя бы результат или норма — это показатель
        if result or norm:
            indicators[text] = {}
            if result:
                indicators[text]["result"] = result
            if norm:
                indicators[text]["norm"] = norm

    return indicators


def parse_all_json():
    json_files = sorted(JSON_FOLDER.glob("*_page_*.json"))

    if not json_files:
        print("❗ Не найдено JSON страниц")
        return

    print(f"✅ Найдено JSON-страниц: {len(json_files)}")

    total = {}

    for jf in json_files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            indicators = extract_indicators_from_page(data)

            count = len(indicators)
            total.update(indicators)

            if count:
                print(f"✅ {jf.name}: {count} показателей")
            else:
                print(f"⚪ {jf.name}: нет данных")

        except Exception as e:
            print(f"❌ Ошибка в {jf.name}: {e}")

    print("\n=== ИТОГО ===")
    print(f"Всего показателей: {len(total)}\n")

    for k, v in list(total.items())[:30]:
        print(f"- {k}: {v}")


if __name__ == "__main__":
    parse_all_json()
