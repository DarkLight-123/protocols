"""
Модуль screen_work.py

Этот модуль содержит общие функции для работы со скриншотами,
позволяя автоматизировать процессы взаимодействия с графическим интерфейсом пользователя (GUI).
Функции модуля позволяют выполнять действия, связанные с ожиданием появления элементов,
кликами по изображениям и запуска приложений.

Функции модуля включают:

    - wait_scr: Ожидание появления скриншота на экране и клик по нему.
    - click_scr: Ожидание появления и клик по скриншоту с возвратом объекта изображения.
    - wait_scr_to_disappear: Ожидание исчезновения скриншота с экрана.
    - click_scr_in_scr: Клик по внутреннему скриншоту, найденному в другом скриншоте.
    - launch_desktop_app: Запуск приложения с проверкой его состояния.
    - wait_fr_app_loading: Ожидание полной загрузки приложения FineReader.
    - click_convert_main_menu: Клик по кнопке для открытия главного меню конвертации.
    - input_filename: Ввод названия файла в поле приложения.
    - is_in_convert_to_word_section: Проверка нахождения в разделе '
            Конвертировать в Microsoft Word'.
    - uncheck_save_image: Убрать галочку с сохранения изображения.
    - check_save_image: Установить галочку на сохранение изображения.
    - uncheck_open_doc: Убрать галочку с открытия документа после конвертации.
    - click_convert_blue_button: Нажать кнопку для конвертации в Word.
    - handle_fr_warning: Проверка наличия предупреждения после конвертации документа.

"""
import os
import time

import psutil
#import pyautogui
import pyperclip

from protocols.league_sert.constants import FRScreens
from protocols.conversion.exceptions import ScreenshotNotFoundError
from protocols.conversion.files_and_proc_utils import change_keyboard_layout_on_english, hide_the_windows


def get_absolute_scr_path(filename: str) -> str:
    """Возвращает абсолютный путь к изображению скриншота."""
    conver_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(conver_dir, 'screenshots', filename)


def wait_scr(screenshot_path: str,
             timeout: int | float = 3,
             confidence: float = 0.8) -> tuple[float] | None:
    """ Ожидать появление скриншота в течение заданного времени.
     При обнаружении кликнуть по нему один раз. """
    screenshot_path = get_absolute_scr_path(screenshot_path)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            time.sleep(0.03)
            image = pyautogui.locateOnScreen(screenshot_path, confidence=confidence)
            if image:
                return image
        except pyautogui.ImageNotFoundException:
            pass
    # Поднять исключение, если скриншот не найден в течении заданного периода времени.
    raise ScreenshotNotFoundError(screenshot_path)


def click_scr(screenshot_path: str,
              timeout: int | float = 3,
              confidence: float = 0.8) -> None:
    """Ожидать появление и кликнуть по скриншоту, возвращая объект изображения."""
    screenshot_path = get_absolute_scr_path(screenshot_path)
    img = wait_scr(screenshot_path, timeout, confidence)
    pyautogui.click(img)


def wait_scr_to_disappear(screenshot_path: str,
                          timeout: int = 40,
                          time_sleep: int | float = 0.5) -> None:
    """ Ждем пока определенный скриншот не исчезнет с экрана.
    В течении заданного периода времени ищем скриншот на экране. Если находим,
    то продолжаем искать, если не находим, то выходим из функции и возвращаем None.
    Если в течении заданного времени скриншот с экрана не ушел, то возвращаем False.
    """
    screenshot_path = get_absolute_scr_path(screenshot_path)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            time.sleep(time_sleep)
            wait_scr(screenshot_path, confidence=0.7)
            break
        except ScreenshotNotFoundError:
            return None


def click_scr_in_scr(inner_img: str,
                     external_img: tuple[float] | None,
                     confidence: float = 0.7):
    """ Найти скриншот в скриншоте и кликнуть по внутреннему скриншоту. """
    try:
        found_inner_img = pyautogui.locateOnScreen(
            inner_img, region=external_img, confidence=confidence)
        pyautogui.click(found_inner_img)

    except pyautogui.ImageNotFoundException:
        pass


def launch_desktop_app(process: str, icon_from_panel: str,
                       icon_from_desktop: str, confidence: float = 0.8) -> None:
    """ Проверяет запущен ли переданный процесс в ОС. Если процесс(окно) запущено, то
    раскрываем кликом по иконке на панели. Если нет, то кликаем по иконке на рабочем столе. """

    change_keyboard_layout_on_english()
    hide_the_windows()

    # Перебираем текущие процессы и ищем нужный нам процесс.
    for proc in psutil.process_iter():
        name = proc.name()
        # Если нужный процесс запущен.
        if name == process:
            # Кликнуть по иконке на нижней панели, чтобы развернуть окно.
            click_scr(icon_from_panel, confidence=confidence)
            return None
    # Если нужный процесс не запущен, то запускаем по иконке с рабочего стола.
    click_scr(icon_from_desktop, confidence=confidence)
    pyautogui.hotkey('enter')
    return None


def wait_fr_app_loading() -> None:
    """ Дождаться полной загрузки FineReader. """
    # time.sleep(5)
    wait_scr_to_disappear(FRScreens.DESKTOP_APP_LOADING.value)


def click_convert_main_menu() -> None:
    """ Главное меню, кликнуть по кнопке конвертировать """
    click_scr(FRScreens.CONVERT_TO_WORD_MAIN_MENU.value)


def press_enter():
    pyautogui.press('enter')


def pick_all_files(screen=FRScreens.INPUT_FIELD_FILE_NAME.value):
    """ Ввести название файла в поле приложения. """
    scr = wait_scr(screen)
    time.sleep(0.5)

    new_x = scr[0] + 90
    new_y = scr[1] - 140

    time.sleep(0.5)
    pyautogui.click(new_x, new_y)

    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    press_enter()


def input_filename(file_path, screen=FRScreens.INPUT_FIELD_FILE_NAME.value):
    """ Ввести название файла в поле приложения. """
    wait_scr(screen)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyperclip.copy(file_path)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    press_enter()


def is_in_convert_to_word_section():
    """Проверяем находимся ли в подразделе 'Конвертировать в Microsoft Word'."""
    try:
        click_scr(FRScreens.BUTTON_CANCEL.value, timeout=5)
    except ScreenshotNotFoundError:
        pass


def uncheck_save_image() -> None:
    """ Убрать галочку с сохранения рисунка. """
    timeout: int | float = 1
    confidence: float = 0.8
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            time.sleep(0.03)
            # Найти скрин с чекбоксом сохранения рисунков.
            image = wait_scr(FRScreens.CHECKBOX_SAVE_PICS_WITH_MARK.value, confidence=confidence)
            # Если найден убрать галочку.
            if image:
                click_scr_in_scr(FRScreens.CHECKMARK.value, image)
        except ScreenshotNotFoundError:
            break


def check_save_image() -> None:
    """ Убрать галочку с сохранения рисунка. """
    timeout: int | float = 1
    confidence: float = 0.8
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            time.sleep(0.03)

            # Найти скрин с чекбоксом сохранения рисунков.
            image = wait_scr(FRScreens.CHECKBOX_SAVE_PICS_WITH_MARK.value, confidence=confidence)
            if image:
                try:
                    click_scr_in_scr(FRScreens.CHECKMARK.value, image)
                    pyautogui.click(image)
                except:
                    pyautogui.click(image)

        except ScreenshotNotFoundError:

            break


def uncheck_open_doc() -> None:
    """ Убрать галочку с сохранения рисунка. """
    timeout: int | float = 1
    confidence: float = 0.8
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            time.sleep(0.03)
            # Найти скрин с чекбоксом сохранения рисунков.
            image = wait_scr(FRScreens.OPEN_DOC.value, confidence=confidence)
            # Если найден убрать галочку.
            if image:
                click_scr_in_scr(FRScreens.OPEN_DOC_CHECKMARK.value, image)
        except ScreenshotNotFoundError:
            break


def click_convert_blue_button() -> None:
    """ Нажать синюю кнопку конвертировать в Word. """
    try:
        click_scr(FRScreens.CONVERT_TO_WORD_INNER_BUTTON.value)
    except Exception as e:
        pyautogui.press('enter')


def handle_fr_warning():
    """ Проверить наличия предупреждения после конвертации документа. """
    # Проверить нахождение во внутреннем меню конвертации.
    wait_scr(FRScreens.IN_CONVERSION_MENU.value)

    try:
        wait_scr(FRScreens.WARNING_AFTER_CONVERT.value, timeout=0.5)
        time.sleep(0.5)
        click_scr(FRScreens.SHUT_WARNING_BLUE_FRAME.value)
    except ScreenshotNotFoundError:
        return None
