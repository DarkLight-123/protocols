"""
Модуль для финальной обработки данных из таблиц.

Код добавляет таблицы показателей в соответствующую таблицу образцов,
удаляет лишние данные, определяет тип таблицы и прописывает его в ключе таблицы.

Функции:

    - join_sample_and_results:
        Объединить таблицы образцов(SAMPLE) с таблицами результатов(RESULTS).
        Следующие за таблицей образцов таблицы результатов добавить в поле
        indicators таблицы SAMPLE.

    - remove_results_table:
        Удалить таблицы с результатами исследований(RESULTS)

    - determine_names_of_tables:
        Определить тип таблицы исходя из ее содержимого.
        Под типом понимается к какой модели она относится.
        Тип таблицы - сохраняется в строке, под вторым индексом в ключе.

    - refine_and_merge_tables:
        Завершить обработку таблиц, объединяя, удаляя ненужные,
        и определяя тип таблиц.

"""
import re

from league_sert.constants import FIX_KEYS_OBJECT_MERGE, TABLE_TYPES_IN_RUS
from league_sert.manual_entry.exceptions import MissedTableError

Tables = dict[tuple[int, str]: dict[str]]


def join_sample_and_results(tables: Tables) -> Tables:
    """ Объединить таблицы образцов(SAMPLE) с таблицами результатов(RESULTS).
    Следующие за таблицей образцов таблицы результатов добавить в поле
    indicators таблицы SAMPLE. """

    names_of_tabs = list(tables.keys())
    cur_tab = 0

    while cur_tab < (len(names_of_tabs)):
        # Если ключ таблицы с "SAMPLE" - код шифра.
        if names_of_tabs[cur_tab][1] == 'SAMPLE':
            # Инициализируем поле 'indicators' для текущей 'SAMPLE' таблицы.
            tables[names_of_tabs[cur_tab]]['indicators'] = []
            # Проходим по всем последующим таблицам, пока они являются 'RESULTS'.
            next_table = cur_tab + 1
            while next_table < len(names_of_tabs) and names_of_tabs[next_table][1] == 'RESULTS':
                # Добавляем значения из текущей 'RESULTS' в 'SAMPLE'.
                tables[names_of_tabs[cur_tab]]['indicators'].append(
                    tables[names_of_tabs[next_table]])
                next_table += 1
            # Устанавливаем индекс текущей таблицы на первую не 'RESULTS' таблицу 'SAMPLE'.
            cur_tab = next_table
        else:
            cur_tab += 1
    return tables


def remove_results_table(tables: Tables) -> Tables:
    """ Удалить таблицы с результатами исследований. """
    tables = {name: value for name, value in tables.items() if name[1] != 'RESULTS'}
    return tables


def determine_names_of_tables(tables: Tables) -> Tables:
    """ Определить тип таблицы исходя из ее содержимого.
    Под типом понимается к какой модели она относится.
    Тип таблицы - сохраняется в строке, под вторым индексом в ключе. """

    # Переменная для итоговых данных по таблицам.
    result = {}

    # Перебираем таблицы. Ключи по типу (1, 'SAMPLE')
    for key, value in tables.items():

        # Если таблица с основными данными, просто сохраняем в результат.
        if key[1] == 'MAIN':
            result[key] = value
            continue

        # Если таблица с данными по производственному контролю.
        if key[1] == 'PROD_CONTROL':
            # Сохраняем в результат данные из таблицы.
            result[key] = value
            # Если ключ с производственным контролем последний, то прервать цикл.
            if key == list(tables.items())[-1]:
                break
            # Продолжить цикл, если таблица с производственным контролем не последняя в документе.
            continue

        # Для остальных таблиц, не относящихся к основным данным
        # и данным по производственному контролю.

        # Ищем в таблице ключ 'Группа продукции'. Такой ключ в таблицах
        # 'Производство магазина' и 'производство изготовителя'.
        production = value.get('Группа продукции', None)

        # Определяем это 'Производство магазина' или 'производство изготовителя'
        if production:
            manuf_pattern = r'п\s*р\s*о\s*и\s*з\s*в\s*о\s*д\s*и\s*[тг]\s*е\s*л\s*я'
            if re.search(manuf_pattern, production):
                result[(key[0], 'manuf_prod')] = value
                continue
            store_pattern = r'м\s*а\s*г\s*а\s*з\s*и\s*н\s*а'
            if re.search(store_pattern, production):
                result[(key[0], 'store_prod')] = value
                continue

        # Ищем в таблице ключ 'Объект исследования'. Такой ключ в таблицах
        # 'Смывы', 'Вода', 'Воздух'.

        object_of_test = value.get('Объект исследования', None)

        if object_of_test:
            object_of_test = object_of_test.replace(',', '', ).replace(' ', '')

            # Пытаемся понять - это таблица с водой, смывами, воздухом и т.д.
            for k, v in FIX_KEYS_OBJECT_MERGE.items():
                # Сохраняем в результат.
                if re.search(v, object_of_test, re.IGNORECASE):
                    result[(key[0], k)] = value
                    break
            continue

        raise MissedTableError(key[0], TABLE_TYPES_IN_RUS[list(result.keys())[-1][1]])

    if len(tables) != len(result):
        raise Exception('Упущена таблица в модуле merge_tables.')

    return result


def refine_and_merge_tables(tables: Tables) -> Tables:
    """ Завершить обработку таблиц, объединяя, удаляя ненужные,
    и определяя тип таблиц. """
    tables = join_sample_and_results(tables)
    tables = remove_results_table(tables)
    tables = determine_names_of_tables(tables)
    return tables
