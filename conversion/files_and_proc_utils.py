"""
Модуль 'files_and_proc_works'

Этот модуль содержит функции, которые предназначены для работы с процессами,
файлами и папками, а также для управления окнами и взаимодействия с пользователем.


Функции:

    - `change_keyboard_layout_on_english()`:
    Переключает раскладку клавиатуры на английскую, что может быть полезно при вводе
    данных или работе с программным обеспечением, требующим англоязычной раскладки.

    - `hide_the_windows()`:
    Сворачивает (минимизирует) все открытые окна на рабочем столе.
      Используется для очистки экрана или для сосредоточения внимания
      на конкретной задаче.

    - `return_or_create_dir(path_to_dir: str)`:
    Проверяет наличие директории по указанному пути.
      Если директория не существует, она будет создана. Возвращает путь к
      проверенной или созданной директории.

    - `check_proc(process: str) -> None`:
    Проверяет наличие и закрывает указанный процесс на компьютере.
      Может использоваться для предотвращения конфликта программ
      или освобождения системных ресурсов.

    - `terminate_the_proc(process: str) -> None`:
    Завершает указанный процесс. Это действие более агрессивное,
      чем просто закрытие, и может быть использовано в случае, когда
      процесс не поддаётся стандартному завершению.

    - `get_path_from_user(message_for_user: str) -> str`:
    Получает путь от пользователя через ввод,
      проверяя, что указанный путь существует и указывает на директорию.
      Возвращает проверенный путь.

    - `fetch_files_for_conversion(path_to_dir_pdf: str, path_to_dir_word: str) -> set`:
    Возвращает множество
      файлов, которые необходимо конвертировать, из указанной
      директории PDF в целевую директорию Word.
      Это важно для автоматизации процесса конвертации файлов.

    - `is_specific_word_window_open(target_title: str)`:
    Проверяет, открыт ли документ Word с указанным заголовком.
      Полезно для скриптов, которым нужно знать, открыт ли конкретный документ.

    - `is_file_in_dir(dir_, file)`:
    Проверяет, находится ли файл в указанной директории. Возвращает логическое значение,
      указывающее на наличие файла. Это удобно для подтверждения
      успешного перемещения или поиска файла.

Использование модулей и функций из этого набора может существенно упростить автоматизацию различных
задач, связанных с управлением файловой системой и взаимодействием с пользователем.
"""
import os
import time

import py_win_keyboard_layout
#import pyautogui
import psutil
import pygetwindow as gw

from protocols.conversion.exceptions import PathNotInputError, InvalidPathError, PageNeedToRMError
from protocols.league_sert.constants import FRScreens


def change_keyboard_layout_on_english():
    """ Переключить раскладку клавиатуры на английскую. """
    py_win_keyboard_layout.change_foreground_window_keyboard_layout(0x04090409)


def hide_the_windows():
    """ Свернуть все окна"""
    pyautogui.hotkey('Win', 'd')


def return_or_create_dir(path_to_dir: str):
    """ Вернуть или создать директорию. """
    if not os.path.isdir(path_to_dir):
        os.mkdir(path_to_dir)
        print("Создана директория <%s>." % path_to_dir)
    else:
        print("Проверено наличие директории <%s>. Директория существует. " % path_to_dir)
    return path_to_dir


def check_proc(process: str) -> None:
    """ Закрыть переданный процесс. """
    # Перебираем текущие процессы и ищем нужный нам процесс.
    flag = True
    while flag:
        processes = {proc.name() for proc in psutil.process_iter()}
        # Если нужный процесс запущен.
        if process in processes:
            continue
        break


def terminate_the_proc(process: str) -> None:
    """ Закрыть переданный процесс. """
    # Перебираем текущие процессы и ищем нужный нам процесс.
    for proc in psutil.process_iter():
        name = proc.name()
        # Если нужный процесс запущен.
        if name == process:
            proc.terminate()
            break
    check_proc(process)


def get_path_from_user(message_for_user: str) -> str:
    """Получить путь от пользователя к существующей директории."""
    path_from_user = input(message_for_user)
    if not path_from_user:
        raise PathNotInputError()
    if not os.path.isdir(path_from_user):
        raise InvalidPathError()
    return path_from_user


def fetch_files_for_conversion(path_to_dir_pdf: str, path_to_dir_word: str) -> set:
    """Вернуть множеством файлы, которые нужно конвертировать."""
    pdf_files = {i for i in os.listdir(path_to_dir_pdf) if i[-4:] == '.pdf' and
                 i[-9:-4] != 'stamp' and i[-8:-4] != 'temp'}
    pdf_files = {i[:-4] for i in pdf_files}
    word_files = {i for i in os.listdir(path_to_dir_word) if i[-5:] == '.docx'}
    word_files = {i[:-5] for i in word_files}
    set_files_required_to_convert = pdf_files.difference(word_files)
    return set_files_required_to_convert


def is_specific_word_window_open(target_title: str):
    """ Проверить открыт ли определенный документ word. """

    # Получаем все окна с заголовком, содержащим "Word"
    word_windows = gw.getWindowsWithTitle('Word')

    # Проверяем, есть ли окно с заголовком target_title.
    for window in word_windows:
        if window.title == target_title:
            return True
    return False


def close_specific_word_windows(target_title: str):
    # Получаем все окна с заголовком, содержащим "Word"
    target_title = target_title[:target_title.rfind('.')] + ' - Word'
    word_windows = gw.getWindowsWithTitle('Word')

    # Проверяем, есть ли окно с заголовком target_title.
    for window in word_windows:
        print(window.title)
        print(target_title)
        if window.title == target_title:
            window.close()


def close_specific_pdf_windows(target_title: str):
    target_title = target_title.replace('.docx', '.pdf') + ' - Adobe Acrobat Reader (64-bit)'
    # Получаем все окна с заголовком, содержащим "Word"
    pdf_windows = gw.getWindowsWithTitle('pdf')

    # Проверяем, есть ли окно с заголовком target_title.
    for window in pdf_windows:
        print(window.title)
        print(target_title)
        if window.title == target_title:
            window.close()


def is_file_in_dir(dir_, file):
    """ Проверка, что файл находится в директории. """

    from conversion.screen_work import wait_scr

    start = time.time()
    in_dir = False
    while time.time() - start < 120 and not in_dir:
        files = set(os.listdir(dir_))
        in_dir = file in files
        if in_dir:
            return True
    if wait_scr(FRScreens.ERROR_PAGE_NEED_TO_RM.value):
        raise PageNeedToRMError(file)
