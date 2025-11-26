"""
Пример сжатия файла с использованием библиотеки aspose.
Сжимает, сохраняет качество, оставляет водный знак, красная строка на странице,
нужна лицензия
"""
import os
from pathlib import Path

import aspose.pdf as ap

from conversion.files_and_proc_utils import return_or_create_dir
from league_sert.db_operations.file_utils import read_viewed_from_file


COMPRESSED_FILES = r'.\compress_pdfs\compressed_files.txt'


def compress_file_with_aspose(input_pdf: str | Path,
                              output_pdf: str | Path,
                              image_quality: int = 50,
                              dpi: int = 120):
    """
    Сжать pdf файл.

    :param input_pdf:
    :param output_pdf:
    :param image_quality: Качество изображения от 0 до 100.
    :param dpi:
    :return: None
    """

    # Проверка переданных аргументов.
    if not os.path.isfile(input_pdf):
        raise FileNotFoundError(f"Файл '{input_pdf}' не найден.")
    if not (0 < image_quality <= 100) or not isinstance(image_quality, int):
        raise ValueError("image_quality должно быть целое число в диапазоне от 0 до 100.")
    if not (72 <= dpi <= 600) or not isinstance(dpi, int):
        raise ValueError("dpi должно быть целое число в диапазоне от 72 до 600.")

    try:
        # Загрузить PDF-файл.
        input_pdf = ap.Document(input_pdf)

        # Создать объект класса OptimizationOptions.
        pdf_optimize_options = ap.optimization.OptimizationOptions()

        # Включить сжатие изображений.
        pdf_optimize_options.image_compression_options.compress_images = True

        # Установить качество изображения.
        pdf_optimize_options.image_compression_options.image_quality = image_quality

        # Установить максимальное разрешение изображений.
        pdf_optimize_options.image_compression_options.max_resolution = dpi

        # Включить изменение размера изображений
        pdf_optimize_options.image_compression_options.resize_images = True

        # Сжать PDF
        input_pdf.optimize_resources(pdf_optimize_options)

        # Сохранить сжатый PDF
        input_pdf.save(output_pdf)

        return input_pdf, None

    except Exception as e:
        print(e)
        return None, input_pdf


def compress_files_in_dir(dir_with_pdf_files: str):
    """ Сжать файлы формата ПДФ в директории, синхронно, """

    # Директория для сжатых файлов.
    dir_compressed = return_or_create_dir(dir_with_pdf_files + '\\compressed_files\\')

    # Перечень сжатых файлов из документа.
    compressed: set = read_viewed_from_file(COMPRESSED_FILES)

    # Получить перечень уже сжатых файлов из директории.
    compressed_files = set(
        [file for file in os.listdir(dir_compressed)
         if file.endswith('.pdf')
         and '$' not in file])

    compressed.update(compressed_files)

    # Получить список файлов в директории
    files_to_convert = [file for file in os.listdir(dir_with_pdf_files)
                        if file.endswith('.pdf') and file not in compressed
                        and '$' not in file]

    # Несжатые файлы.
    uncompressed = set()

    # Цикл по файлам, нуждающимся в конвертации.
    for file in files_to_convert:

        try:
            input_file = str(Path(dir_with_pdf_files) / file)
            output_file = str(Path(dir_compressed) / file)
            compressed_file, uncompressed_file = compress_file_with_aspose(
                input_file, output_file)

            if compressed_file:
                compressed.add(file)

            if uncompressed_file:
                uncompressed.add(file)

        except Exception as e:

            print(f"Ошибка при сжатии файла: {file} -> {e}")
            uncompressed.add(file)

    # Обновить файл с записанными файлами.
    with open(COMPRESSED_FILES, 'w', encoding='utf-8') as file:
        file.write(",".join(compressed))

    print(f'Сжато {len(compressed)} файлов.')
    print(f'Не сжаты файлы. {uncompressed}')
