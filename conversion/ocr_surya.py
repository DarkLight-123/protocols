import os
import time
import argparse
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
from docx import Document

# --- Surya ---
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

# Контроль потоков (ускоряет и не «забивает» ноут)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")


def render_page_to_pil(page, dpi=240) -> Image.Image:
    """Рендер страницы PDF в PIL.Image через PyMuPDF (быстро и без внешних тулов)."""
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.info["dpi"] = (dpi, dpi)
    return img


def downscale_if_needed(img: Image.Image, max_side: int = 1800) -> Image.Image:
    """Если изображение слишком большое — даунскейлим для ускорения инференса."""
    w, h = img.size
    m = max(w, h)
    if m <= max_side:
        return img
    scale = max_side / float(m)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS)


def ocr_page_surya(pil_img: Image.Image,
                   rec: RecognitionPredictor,
                   det: DetectionPredictor) -> str:
    """
    OCR одной страницы Surya.
    Возвращает склеенный построчно текст (сверху-вниз, слева-направо).
    """
    # В новых версиях: rec([...], det_predictor=det) -> List[OCRResult]
    results = rec([pil_img], det_predictor=det)
    ocr_res = results[0]  # OCRResult

    # У OCRResult есть .text_lines — список объектов TextLine (у каждого .text, .bbox)
    lines = getattr(ocr_res, "text_lines", []) or []

    # Отсортируем по bbox: сначала по y, затем по x
    def sort_key(line):
        # bbox = [x0, y0, x1, y1]
        b = getattr(line, "bbox", [0, 0, 0, 0])
        return (b[1], b[0])

    pieces = []
    for ln in sorted(lines, key=sort_key):
        t = (getattr(ln, "text", "") or "").strip()
        if t:
            pieces.append(t)

    return "\n".join(pieces)


def convert_pdf_to_docx_surya(pdf_path: Path, out_dir: Path, dpi: int = 240, max_side: int = 1800) -> Path:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    docx_path = out_dir / (pdf_path.stem + ".docx")

    # Инициализация моделей один раз на документ
    foundation = FoundationPredictor()                 # базовая фича-сеть
    rec = RecognitionPredictor(foundation)             # распознавание текста
    det = DetectionPredictor()                         # детекция текстовых блоков

    word_doc = Document()
    with fitz.open(pdf_path) as doc:
        total = len(doc)
        print(f"\n=== Обрабатываю: {pdf_path.name} ===")
        for i, page in enumerate(doc, 1):
            t_page = time.time()

            img = render_page_to_pil(page, dpi=dpi)
            img = downscale_if_needed(img, max_side=max_side)

            try:
                text = ocr_page_surya(img, rec, det)
                status = f"{'пусто' if not text.strip() else 'ok'}, символов: {len(text)}"
            except Exception as e:
                text = ""
                status = f"ошибка: {e}"

            word_doc.add_paragraph(f"[Страница {i}/{total}]")
            word_doc.add_paragraph(text if text.strip() else "(Пусто / не распознано)")
            if i < total:
                word_doc.add_page_break()

            print(f"  - Страница {i}/{total} ... {status}, {time.time() - t_page:.1f} c")

    word_doc.save(docx_path)
    print(f"[OK] {pdf_path.name} → {docx_path.name} за {time.time() - t0:.1f} c")
    return docx_path


def batch_convert(folder: Path, out_dir: Path, dpi: int = 240, max_side: int = 1800):
    """Пакетная обработка: модели инициализируем один раз и используем для всех PDF."""
    pdfs = sorted(p for p in folder.glob("*.pdf") if p.is_file())
    if not pdfs:
        print("❗ В папке нет PDF.")
        return

    # Модели один раз
    foundation = FoundationPredictor()
    rec = RecognitionPredictor(foundation)
    det = DetectionPredictor()

    out_dir.mkdir(parents=True, exist_ok=True)

    for pdf in pdfs:
        t0 = time.time()
        word_doc = Document()
        with fitz.open(pdf) as doc:
            total = len(doc)
            print(f"\n=== Обрабатываю: {pdf.name} ===")
            for i, page in enumerate(doc, 1):
                t_page = time.time()
                img = render_page_to_pil(page, dpi=dpi)
                img = downscale_if_needed(img, max_side=max_side)
                try:
                    results = rec([img], det_predictor=det)
                    ocr_res = results[0]
                    lines = getattr(ocr_res, "text_lines", []) or []
                    def sort_key(line):
                        b = getattr(line, "bbox", [0, 0, 0, 0])
                        return (b[1], b[0])
                    text = "\n".join(
                        (getattr(ln, "text", "") or "").strip()
                        for ln in sorted(lines, key=sort_key)
                        if (getattr(ln, "text", "") or "").strip()
                    )
                    status = f"{'пусто' if not text.strip() else 'ok'}, символов: {len(text)}"
                except Exception as e:
                    text = ""
                    status = f"ошибка: {e}"

                word_doc.add_paragraph(f"[Страница {i}/{total}]")
                word_doc.add_paragraph(text if text.strip() else "(Пусто / не распознано)")
                if i < total:
                    word_doc.add_page_break()

                print(f"  - Страница {i}/{total} ... {status}, {time.time() - t_page:.1f} c")

        docx_path = out_dir / (pdf.stem + ".docx")
        word_doc.save(docx_path)
        print(f"[OK] {pdf.name} → {docx_path.name} за {time.time() - t0:.1f} c")


def main():
    parser = argparse.ArgumentParser(description="OCR PDF → DOCX (Surya)")
    parser.add_argument("input", help="Путь к PDF файлу или папке с PDF")
    parser.add_argument("--out", default="word_files", help="Куда класть DOCX (по умолчанию: word_files)")
    parser.add_argument("--dpi", type=int, default=240, help="DPI рендера PDF (по умолчанию 240)")
    parser.add_argument("--max-side", type=int, default=1800, help="Ограничение по большей стороне (по умолчанию 1800)")
    args = parser.parse_args()

    inp = Path(args.input)
    out_dir = Path(args.out)

    if inp.is_file() and inp.suffix.lower() == ".pdf":
        convert_pdf_to_docx_surya(inp, out_dir, dpi=args.dpi, max_side=args["max_side"] if isinstance(args, dict) else args.max_side)
    elif inp.is_dir():
        batch_convert(inp, out_dir, dpi=args.dpi, max_side=args["max_side"] if isinstance(args, dict) else args.max_side)
    else:
        print("❌ Укажи путь к PDF файлу или папке с PDF.")


if __name__ == "__main__":
    main()
