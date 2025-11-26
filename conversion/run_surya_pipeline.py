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


if __name__ == "__main__":
    run_ocr_for_all_pdfs()
