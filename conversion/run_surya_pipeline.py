from pathlib import Path

from conversion.ocr_surya import convert_pdf_to_docx_surya


INPUT_PDFS_DIR = Path("input_pdfs")
OUTPUT_DOCX_DIR = Path("word_files")


def run_ocr_for_all_pdfs():
    """
    Находит все PDF в input_pdfs и конвертирует в DOCX через Surya.
    """
    pdf_files = sorted(INPUT_PDFS_DIR.glob("*.pdf"))

    if not pdf_files:
        print("❗ В папке input_pdfs нет PDF файлов.")
        return

    print(f"✅ Найдено PDF файлов: {len(pdf_files)}")

    for pdf in pdf_files:
        print(f"\n➡️ Обрабатываю: {pdf.name}")
        try:
            convert_pdf_to_docx_surya(pdf, OUTPUT_DOCX_DIR)
        except Exception as e:
            print(f"❌ Ошибка при обработке {pdf.name}: {e}")

    print("\n🎉 Готово! Все PDF преобразованы в DOCX.")
from fbu_protocols.file_parser import WordFileParser


def parse_all_docx():
    """
    Пройтись по всем DOCX в word_files и вывести разобранные данные.
    """
    docx_files = sorted(OUTPUT_DOCX_DIR.glob("*.docx"))

    if not docx_files:
        print("❗ В папке word_files нет DOCX файлов для парсинга.")
        return

    print(f"✅ Найдено DOCX файлов: {len(docx_files)}")

    for docx in docx_files:
        print(f"\n📄 Парсинг: {docx.name}")

        try:
            wp = WordFileParser(str(docx))
            wp.get_all_required_data_from_word_file()

            print("  ✅ Основные данные:")
            for k, v in wp.data.items():
                print(f"   • {k}: {v}")

            print("\n  ✅ Показатели:")
            print(f"   Всего: {len(wp.indicators)}")

        except Exception as e:
            print(f"❌ Ошибка при парсинге {docx.name}: {e}")

def run_full_pipeline():
    run_ocr_for_all_pdfs()
    parse_all_docx()


if __name__ == "__main__":
    run_full_pipeline()

