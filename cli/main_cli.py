"""
Общий CLI для взаимодействия со всем приложением.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from compress_pdfs.compress_file_aspose_pdf import compress_files_in_dir
from cli_db_manager import cli_db_manager
from utils import divider, get_dir_from_user
from conversion.convert_files_all import convert_all_pdf_in_dir_to_docx
from conversion.remove_pages_in_pdf import remove_pdf_pages
from league_sert.db_operations.db_writer import write_files_to_db_from_dir
from league_sert.manual_entry.db_writer_debug import write_files_to_db_from_dir_debug
from rename_files.rename_files import rename_the_files_in_dir


def main_cli():
    """ Основной CLI. """
    choice_of_user = True
    divider()
    print('Общее меню.\nВыберите нужное действие, введите число, нажмите <Enter>')

    actions = {
        1: "Выполнить весь процесс",
        2: "Конвертировать PDF в DOCX",
        3: "Записать файлы в БД",
        4: "Записать файлы через корректировки",
        5: "Переименовать файлы",
        6: "Сжать файлы",
        7: "Удалить страницы из PDF",
        8: "Работа с таблицами в БД",
        0: "Выход"
    }

    while True and choice_of_user != 0:
        divider()
        print("\nМеню:")
        for key, value in actions.items():
            print(f"{key}. {value}")

        try:
            choice_of_user = int(input("\nВведите номер действия: "))
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите число.")
            continue

        if choice_of_user not in actions:
            print("Некорректный выбор. Пожалуйста, выберите действие из меню.")
            continue

        if choice_of_user == 0:
            break
        if choice_of_user != 8:
            path_from_user = get_dir_from_user()

        if choice_of_user == 1:
            convert_all_pdf_in_dir_to_docx(path_from_user)
            print('Файлы конвертированы.')
            rename_the_files_in_dir(path_from_user)
            print('Файлы переименованы.')
            compress_files_in_dir(path_from_user)
            print('Файлы сжаты.')
            write_files_to_db_from_dir(path_from_user)
            print('Файлы записаны в БД.')

        elif choice_of_user == 2:
            convert_all_pdf_in_dir_to_docx(path_from_user)
            print('Файлы в директории конвертированы.')

        elif choice_of_user == 3:
            write_files_to_db_from_dir(path_from_user)
            print('Данные из файлов записаны в Базу Данных.')

        elif choice_of_user == 4:
            write_files_to_db_from_dir_debug(path_from_user)
            print('Запись данных в Базу Данных через корректировки word файлов окончена.')

        elif choice_of_user == 5:
            rename_the_files_in_dir(path_from_user)
            print('Файлы в директории переименованы.')

        elif choice_of_user == 6:
            compress_files_in_dir(path_from_user)
            print('Файлы формата .pdf в директории сжаты.')

        elif choice_of_user == 7:
            pages = input('Введите номера страниц, которые нужно удалить из ПДФ файла, '
                          'подряд без пробелов и других знаков, затем нажмите <Enter>,\n'
                          'либо введите слово <отмена> и нажмите <Enter>, если хотите выйти\n'
                          '>>>')
            if pages.lower() == "отмена":
                continue
            pages = [int(i) for i in pages if i.isdigit()]
            remove_pdf_pages(path_from_user, pages)
            print('Страницы удалены из файла формата .pdf')

        elif choice_of_user == 8:
            print('Вы перешли в меню работы с таблицами в Базе Данных.')
            cli_db_manager()


if __name__ == '__main__':
    main_cli()
