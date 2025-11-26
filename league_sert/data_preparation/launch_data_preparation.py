"""
Модуль содержит функцию запуска всего кода пакета data_preparation

Пример использования:
    prepared_data_from_file = extract_and_prepare_data(path_to_word_file)

"""
import re
from typing import Dict

from league_sert.constants import FIX_KEYS_MAIN_PROT, FIX_KEYS_SAMPLE
from league_sert.data_preparation.process_tables import process_the_tables
from league_sert.data_preparation.add_conclusions import add_conclusions_for_all_tables
from league_sert.data_preparation.file_parser import MainCollector
from league_sert.data_preparation.merge_tables import refine_and_merge_tables


def extract_and_prepare_data(word_file):
    """Запуск кода модуля по изъятию и подготовке данных для записи в БД."""

    # Создаем объект собирателя данных из word файла.
    data_collector = MainCollector(word_file)

    # Собираем все данные из word документа, как отдельные поля, так и таблицы,
    # собираем в словари и списки
    data_collector.collect_all_data()

    # Обработка данных из таблиц word файла. Здесь исправляются ошибки,
    # связанные с неправильным разделением таблиц или добавлением лишних строк, колонок и т.д.
    data_collector.data_from_tables = process_the_tables(data_collector.data_from_tables)

    # Здесь пытаемся исправить все ключи с ошибками.
    data_collector.data_from_tables = (
        fix_the_keys_in_all_tables(data_collector.data_from_tables))

    # Добавляем выводы о соответствии результатов исследований нормам.
    data_collector.data_from_tables = add_conclusions_for_all_tables(
        data_collector.data_from_tables)

    # Объединяем таблицы описаний проб и таблицы результатов исследований.
    data_collector.data_from_tables = refine_and_merge_tables(
        data_collector.data_from_tables)

    # Объединяем данные по производственному контролю.
    data_collector.merge_prod_control()

    return data_collector


def _fix_the_keys_in_table(table_value: dict, valid_keys: Dict[str, re.Pattern]) -> dict:
    """ Исправить ключи в одной таблице. """

    fixed_table = {}  # Для исправленной таблицы.

    # Паттерн для очистки ключа от посторонних символов,
    # которые могли появиться в случае неверного распознавания текста.
    clean_pattern = re.compile(r'[<>\'\"\-\`\^]*')

    # Перебираем строки в таблице, ищем по паттерну значения для исправления.
    for key_row, value_row in table_value.items():
        clean_key = clean_pattern.sub('', key_row)  # Очищенный от посторонних символов ключ.
        pattern_found = False  # Найденное неверное написание ключа.

        # Перебираем ключи и значения из словаря, где ключ - правильное написание ключа в таблице,
        # а значения - это паттерн возможных ошибочных написаний ключа.
        for valid_key, pattern in valid_keys.items():
            if pattern.search(clean_key):
                fixed_table[valid_key] = value_row
                pattern_found = True
                break

        if not pattern_found:
            fixed_table[clean_key] = value_row

    return fixed_table


def fix_the_keys_in_all_tables(tables_: dict):
    """ Исправить ключи для всех таблиц, полученных из документа.
     Применить к каждой таблице _fix_the_keys_in_table. """

    new_tables = {}  # Для результата

    # Перебираем таблицы и исправляем ключи в зависимости от вида таблицы.
    for table_key, table_value in tables_.items():

        if table_key[1] in {'RESULTS', 'PROD_CONTROL'}:
            new_tables[table_key] = table_value
            continue

        if table_key[1] == 'MAIN':
            new_tables[table_key] = _fix_the_keys_in_table(table_value, FIX_KEYS_MAIN_PROT)

        if table_key[1] == 'SAMPLE':
            new_tables[table_key] = _fix_the_keys_in_table(table_value, FIX_KEYS_SAMPLE)

    return new_tables
