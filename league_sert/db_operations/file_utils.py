"""
Вспомогательные функции для работы с файлами и директориями.
"""
import os
import shutil
from pathlib import Path

from league_sert.constants import RECORDED_FILE


def read_viewed_from_file(file: str = RECORDED_FILE) -> set:
    """Прочитать номера просмотренных документов из файла."""
    if not os.path.isfile(file):
        with open(file, 'w', encoding='utf-8') as file:
            file.write('')
            return set()

    with open(file, 'r', encoding='utf-8') as file:
        viewed_files = set(file.read().split(','))
        return viewed_files


def move_unrecorded_files(word_file, dir_with_word_files):
    """ Переместить файл, который не удалось записать в DB
    в отельную директорию. """

    unrecorded_word_dir = Path(dir_with_word_files) / 'unrecorded'
    unrecorded_word_dir.mkdir(parents=True, exist_ok=True)

    # Перемещаем word файл.
    original_word_path = Path(dir_with_word_files) / word_file
    destination_word_path = Path(unrecorded_word_dir) / word_file
    shutil.move(original_word_path, destination_word_path)

    # Перемещаем pdf файл.
    pdf_file = word_file.replace('.docx', '.pdf')
    pdf_path = Path(dir_with_word_files).parent
    unrecorded_pdf_path = Path(pdf_path) / 'unrecorded'
    unrecorded_pdf_path.mkdir(parents=True, exist_ok=True)
    original_pdf_path = Path(pdf_path) / pdf_file
    destination_pdf_path = Path(unrecorded_pdf_path) / pdf_file
    shutil.move(original_pdf_path, destination_pdf_path)


def move_recorded_from_unrecorded(word_file, unrecorded_word_files):
    """ Переместить файл, который не удалось записать в DB
    в отельную директорию. """

    # Перемещаем word файл.
    original_word_path = Path(unrecorded_word_files) / word_file
    destination_word_path = Path(unrecorded_word_files).parent / word_file
    shutil.move(original_word_path, destination_word_path)

    # Перемещаем pdf файл.
    pdf_file = word_file.replace('.docx', '.pdf')
    pdf_path = Path(unrecorded_word_files).parent.parent
    unrecorded_pdf_path = Path(pdf_path) / 'unrecorded'

    original_pdf_path = Path(unrecorded_pdf_path) / pdf_file
    destination_pdf_path = Path(unrecorded_pdf_path).parent / pdf_file

    try:
        shutil.move(original_pdf_path, destination_pdf_path)
    except PermissionError:
        shutil.move(destination_word_path, original_word_path)
