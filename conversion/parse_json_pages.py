import json
from pathlib import Path

INPUT_DIR = Path("../word_files")

def parse_first_page(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n=== Анализируем: {json_path.name} ===")

    # просто выводим первые 30 строк для анализа
    for line in data[:30]:
        print(line["text"])


def run():
    pages = sorted(INPUT_DIR.glob("*_page_1.json"))

    if not pages:
        print("❗ Не найдено JSON страниц")
        return

    print(f"✅ Найдено файлов первой страницы: {len(pages)}")

    parse_first_page(pages[0])


if __name__ == "__main__":
    run()
