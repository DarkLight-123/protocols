"""
Конвертировать все файлы ПДФ в .docx с помощью FineReader.
Работа с приложением осуществляется через кликер на pyautogui.
Выбирает все файлы за один раз и передает на конвертацию.

Пример использования:
    - convert_all_pdf_in_dir_to_docx(директория с ПДФ файлами)

"""
import os
import time

from league_sert.constants import FRScreens, FINE_READER_PROCESS

from conversion.files_and_proc_utils import (
    return_or_create_dir, fetch_files_for_conversion)

from conversion.screen_work import (
    click_scr,
    launch_desktop_app,
    wait_fr_app_loading,
    click_convert_main_menu,
    input_filename,
    is_in_convert_to_word_section,
    uncheck_open_doc,
    click_convert_blue_button,
    check_save_image)

from conversion.screen_work import pick_all_files


def fetch_all_files_to_convert(path_to_dir_pdf: str,
                               path_to_dir_word: str) -> str:
    """Вернуть множеством файлы, которые нужно конвертировать."""
    # Все ПДФ файлы в директории
    pdf_files = {
        i.replace('.pdf', '') for i in os.listdir(path_to_dir_pdf)
        if i.endswith('.pdf') and
           'stamp' not in i
           and 'temp' not in i
    }

    # Все .docx файлы в директории
    word_files = {
        i.replace('.docx', '') for i in os.listdir(path_to_dir_word)
        if '.docx' in i
    }

    # Выбираем не конвертированные файлы.
    set_files_required_to_convert = pdf_files.difference(word_files)
    # Формируем и возвращаем все файлы, нуждающиеся в конвертации единой строкой
    files_str = '"' + '" "'.join(set_files_required_to_convert) + '"'
    return files_str


def check_all_files_converted(dir_, expected_files) -> None:
    """ Проверить все ли файлы, конвертированы. """

    time.sleep(2)
    start = time.perf_counter()
    while True:
        files_in_dir = set([i.replace('.docx', '') for i in os.listdir(dir_)])
        if expected_files.issubset(files_in_dir):
            elapsed = '{:.3f}'.format((time.perf_counter() - start) / 60)
            print(f'Конвертация {len(expected_files)} закончилась.'
                  f'Время конвертации составило {elapsed}')
            return


def convert_all_pdf_in_dir_to_docx(dir_with_pdf_files: str) -> None:
    """ Получить от пользователя путь к директории с PDF файлами создать директорию,
    в которую будут сохранены файлы в формате word после конвертации. """

    # Директория для Word файлов.
    dir_for_word_files = return_or_create_dir(dir_with_pdf_files + '\\word_files\\')

    # Перечень файлов, которые еще не конвертированы.
    files_for_convert = fetch_files_for_conversion(dir_with_pdf_files, dir_for_word_files)

    if not files_for_convert:
        print("Отсутствуют файлы для конвертации.")
        return

    # Запустить FineReader.
    launch_desktop_app(FINE_READER_PROCESS, FRScreens.PANEL_ICON.value,
                       FRScreens.DESKTOP_ICON.value, 0.8)

    wait_fr_app_loading()  # Ждем загрузки приложения FineReader.
    is_in_convert_to_word_section()  # Проверяем, что находимся в нужном разделе приложения.
    click_convert_main_menu()
    input_filename(dir_with_pdf_files)  # Ввести директории с ПДФ файлами.
    pick_all_files()  # Выбрать все файлы для конвертации.

    check_save_image()  # Флажок сохранить картинки.
    click_convert_blue_button()  # Кликнуть кнопку <Конвертировать в Word>
    uncheck_open_doc()  # Снять галочку с открыть документ по окончании конвертации.

    # Ввести путь к директории с .docx файлами
    input_filename(dir_for_word_files, screen=FRScreens.FOR_WORD_DIR.value)
    click_scr(FRScreens.CHOICE_DIR.value)

    check_all_files_converted(dir_for_word_files, files_for_convert)
