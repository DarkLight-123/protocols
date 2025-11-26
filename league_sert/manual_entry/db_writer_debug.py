"""
Запись в БД через корректировку файлов формата .docx.

Берется перечень файлов, находящихся в директории для незаписанных в БД, ввиду
ошибок в файле .docx. Далее, каждый файл открывается как в формате .docx,
так и в формате .pdf. В консоли выводится подсказка, какая ошибка присутствует.
Пользователь исправляет ошибку, сохраняет файл .docx, в консоли нажимает <Enter>.
Файл повторно читается и осуществляется попытка записи в БД. Если запись осуществлена,
то файл перемещается к остальным файлам.

"""
import os
import subprocess
from pathlib import Path

from conversion.files_and_proc_utils import (close_specific_word_windows,
                                                       close_specific_pdf_windows)
from database.db_config_postgres import prot_session_maker
from league_sert.data_preparation.launch_data_preparation import (
    extract_and_prepare_data)
from league_sert.db_operations.db_writer import _write_objects_from_file_to_db
from league_sert.constants import RECORDED_FILE
from league_sert.db_operations.file_utils import (read_viewed_from_file,
                                                            move_recorded_from_unrecorded)
from league_sert.manual_entry.exceptions import (MissedTableError,
                                                           MissedKeyCreateInstError)
from league_sert.manual_entry.manual_handlers_exceptions import (
    passed_main_prot_table, handle_missed_table, \
    handle_missed_key_create_inst_error, handle_date_missed_error)
from league_sert.manual_entry.models_creator_debug import (
    create_all_objects_debug)


acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"


def write_files_to_db_from_dir_debug(dir_path):
    """ Обработать и записать в БД все файлы,
    находящиеся в передаваемой директории """

    # Записанные в БД файлы.
    recorded = read_viewed_from_file(RECORDED_FILE)  # Файлы, уже записанные в БД.

    # Директория с файлами не записанными в БД.
    unrecorded_word_dir = Path(dir_path, 'word_files', 'unrecorded')
    unrecorded_pdf_dir = Path(dir_path, 'unrecorded')

    # Перебираем файлы.
    for file in os.listdir(unrecorded_word_dir):

        word_path = Path(unrecorded_word_dir, file)

        # Пропускаем временные и директории
        if '$' in file or os.path.isdir(Path(unrecorded_word_dir, file)):
            continue
        print(file)

        for _ in range(3):

            # Путь к ПДФ файлу.
            pdf_file = Path(unrecorded_pdf_dir, file.replace('.docx', '.pdf'))
            # Путь к word файлу.

            try:
                # Получить и подготовить данные из word файла
                data_from_file = extract_and_prepare_data(Path(unrecorded_word_dir, file))
                # Создать объекты для записи в БД.
                objects_for_db = create_all_objects_debug(data_from_file)

            except MissedTableError as e:

                # Открываем pdf файл через акробат.
                process_pdf = subprocess.Popen([acrobat_path, '/N', str(pdf_file)], shell=True)
                # Открываем .docx файл через акробат.
                process_word = subprocess.Popen([str(word_path)], shell=True)
                handle_missed_table(e, file)
                if process_word:
                    close_specific_word_windows(file)
                if process_pdf:  # Check if process was successfully started
                    close_specific_pdf_windows(file)
                continue

            except MissedKeyCreateInstError as err:
                process_pdf = subprocess.Popen([acrobat_path, '/N', str(pdf_file)], shell=True)
                # Открываем ПДФ файл через акробат.
                process_word = subprocess.Popen([str(word_path)], shell=True)
                handle_missed_key_create_inst_error(err, file)
                if process_word:
                    close_specific_word_windows(file)
                if process_pdf:  # Check if process was successfully started
                    close_specific_pdf_windows(file)

                continue

            # except Exception as e:
            #     print(e)

            except (AttributeError, TypeError) as err:
                process_pdf = subprocess.Popen([acrobat_path, '/N', str(pdf_file)], shell=True)
                # Открываем ПДФ файл через акробат.
                process_word = subprocess.Popen([str(word_path)], shell=True)
                handle_date_missed_error(err, file)
                if process_word:
                    close_specific_word_windows(file)
                if process_pdf:  # Check if process was successfully started
                    close_specific_pdf_windows(file)

            try:

                # Записать объекты в БД.
                _write_objects_from_file_to_db(objects_for_db, prot_session_maker)

            except UnboundLocalError:

                # Открываем ПДФ файл через акробат.
                process_pdf = subprocess.Popen([acrobat_path, '/N', str(pdf_file)], shell=True)
                # Открываем ПДФ файл через акробат.
                process_word = subprocess.Popen([str(word_path)], shell=True)

                passed_main_prot_table(file)
                if process_word:
                    close_specific_word_windows(file)

                if process_pdf:  # Check if process was successfully started
                    close_specific_pdf_windows(file)
                continue

            # Добавить в записанный
            recorded.add(file)

            break

        move_recorded_from_unrecorded(file, unrecorded_word_dir)

    with open(RECORDED_FILE, 'w', encoding='utf-8') as file:
        file.write(",".join(recorded))
