"""
Обработка данных, полученных из таблиц word файла.

Набор действий по преобразованию данных из таблиц результатов исследований
в подходящий для дальнейшей работы вид. Объединить или разделить неправильно
обработанные таблицы. Соединить ошибочно разделенные строки.
Удалить пустую колонку слева.

"""
import re

from league_sert.constants import WordsPatterns, TEST_OBJECT
from league_sert.data_preparation.add_conclusions import find_out_results_table_type


NAME = WordsPatterns.NAME.value
RESULT = WordsPatterns.RESULT.value
REQUIREMENTS = WordsPatterns.REQUIREMENTS.value
INDICATORS = WordsPatterns.INDICATORS.value


def process_the_tables(tables: dict):
    """ Выполнить все действия по преобразованию таблиц в вид,
    подходящий для дальнейшего создания и сохранения моделей. """

    # Убрать из таблицы пустые колонки и ряды с одним значением.
    tables = rm_invalid_cols_and_rows_from_tabs(tables)
    # Разделить ошибочно соединенные таблицы.
    tables = divide_the_table(tables)

    tables = remove_one_raw_table(tables)
    # Объединить ошибочно разделенные таблицы.
    tables = merge_results_table(tables)
    return tables


def remove_one_raw_table(tables_: dict):
    """ Удалить таблицу из одной пустой строки. """
    new_tables = {}
    for tab_key, tab_val in tables_.items():

        if tab_key[1] == 'SAMPLE' and isinstance(tab_val, dict) and list(tab_val.keys()) == ['']:
            pass
        else:
            new_tables[tab_key] = tab_val

    return new_tables


def merge_results_table(tables: dict) -> dict:
    """ Соединение таблиц с результатами воедино в случае, если одна
    логически самостоятельная таблица была разделена на две и более. """

    keys_of_tabs = list(tables.keys())  # Список всех ключей - названий таблиц.
    new_tables = {}  # Итоговые таблицы.

    # Цикл по всем ключам.
    i = 0
    while i < len(keys_of_tabs):

        current_key = keys_of_tabs[i]  # Ключ текущей таблицы.

        # Если таблица из числа MAIN, SAMPLE просто добавить в итоговые таблицы.
        if current_key[1] != 'RESULTS':
            new_tables[current_key] = tables[current_key]
            i += 1
            continue

        # Если таблица с результатами исследований, то определить тип таблицы с результатами.
        current_table_type = find_out_results_table_type(tables[current_key])

        # Если текущая таблица относится к производственному
        # контролю просто добавить в итоговые таблицы.
        if current_table_type == 'prod_control':
            new_tables[current_key] = tables[current_key]
            i += 1
            continue

        # Если таблица с результатами последняя, то просто добавить в итоговые таблицы..
        if i + 1 == len(keys_of_tabs):
            new_tables[current_key] = tables[current_key]
            i += 1
            continue

        next_table_key = keys_of_tabs[i + 1]  # Ключ следующей за проверяемой таблицы.

        # Если следующая таблица не с результатами, то добавить в итоговые таблицы.
        if next_table_key[1] != 'RESULTS':
            new_tables[current_key] = tables[current_key]
            i += 1
            continue

        # Если следующая таблица - самостоятельная таблица с показателями.
        # То добавить текущую в итоговый набор таблиц.
        patt = f'{NAME}|{RESULT}|{REQUIREMENTS}'
        first_row = " ".join(tables[next_table_key][0])
        if next_table_key[1] == 'RESULTS' and re.search(patt, first_row):
            new_tables[current_key] = tables[current_key]
            i += 1
            continue

        # Если таблица не производственного контроля и не последняя.
        # Сохраняем значения из текущей таблицы.
        result = tables[current_key]
        # Определяем тип следующей таблицы с результатами
        next_result_table_type = find_out_results_table_type(tables[keys_of_tabs[i + 1]])

        # Дальше в цикле идем по таблицам, пока они с результатами
        # и не относятся к производственному контролю добавляем их в
        # одну таблицу - текущую таблицу.
        while (i + 1 < len(keys_of_tabs) and
               keys_of_tabs[i + 1][1] == 'RESULTS' and
               next_result_table_type != 'prod_control'):

            result.extend(tables[keys_of_tabs[i + 1]])
            i += 1

        new_tables[current_key] = result
        i += 1

    return new_tables


def rm_first_col_if_blank(tab_rows: list[list]) -> list:
    """ Убрать пустую колонку слева.

    Получить таблицу в виде списка списков, где вложенные списки
    представляют собой строки таблицы. Перебрать через цикл и если
    каждый список-строка таблицы начинается с пустого значения, то убрать
    пустые значения."""
    if set(row[0] for row in tab_rows) == {''}:
        for row in tab_rows:
            if row[0] == '':
                del row[0]
    return tab_rows


def join_divided_sample_code(tab_rows: list[list]) -> list | tuple[dict, str]:
    """ В случае, если в таблице ячейки из первой колонки
     разделило на две колонки. Собрать в одну колонку и исправить
     ключи 'Шифр пробы' и 'Объект исследований' """

    # Проверка, что эта таблица с шифром пробы, поделенная на 2 ячейки.
    if (len(tab_rows[0]) == 3 and
            re.search(r'\bШ', tab_rows[0][0], re.IGNORECASE) and
            re.search(r'\bпроб', tab_rows[0][1], re.IGNORECASE)):

        new_rows = []
        # Перебираем строки и соединяем разделенные значения,
        # попутно, не допуская дублирования значений.
        for row in tab_rows:
            if row[0] != row[1]:
                new_rows.append([row[0] + row[1], row[2]])
            else:
                new_rows.append([row[0], row[2]])

        # Исправляем орфографические ошибки, допущенные в ключах.
        new_rows[0][0] = 'Шифр пробы'
        for ind, row in enumerate(new_rows):
            if re.search(TEST_OBJECT, row[0], re.IGNORECASE):
                new_rows[ind][0] = 'Объект исследований'
        new_rows = {row[0]: row[1] for row in new_rows}
        return new_rows, 'SAMPLE'
    return tab_rows


def join_from_2_cols_to_1(tab_rows):
    """ Если первая колонка таблицы ошибочно была поделена на два значения
     выполнить их объединение. """

    # Если в таблице всего одна или две колонки, то просто вернуть таблицу.
    if len(tab_rows) <= 2:
        return tab_rows

    new_rows = []
    for row in tab_rows:

        # Проверяем, чтобы первое и второе значение в ряде либо идентичное,
        # либо одно из них пустое.
        if row[0] == row[1] or (row[0] == '' or row[1] == ''):
            # Объединяем первое значение в ряде.
            joined_row = ["".join(set([row[0], row[1]]))]
            # Заполняем остальными значениями из ряда.
            joined_row.extend(row[2:])
            new_rows.append(joined_row)
        else:
            return tab_rows  # Возвращаем старые строки
    return new_rows  # Возвращаем новые строки


def rm_blank_rows_in_tab(tab_rows: list):
    """ Убрать строки с пустыми значениями или определенными словами.

    Получить таблицу в виде списка списков, где вложенные списки
    представляют собой строки таблицы. Перебрать через цикл строки
    и удалить то строки, которые состоят из одного повторяющегося значения."""
    new_tab = []

    for row in tab_rows:
        row_elems = set(row)  # Элементы строки
        # Если строка состоит из одного, повторяющегося значения, то не добавлять в новую таблицу.
        if ((len(row_elems) <= 2 and '' in row_elems) or
                (len(row_elems) == 1) or
                (row_elems == {'', 'НД', 'испытаний', 'показателя'})):
            continue
        new_tab.append(row)
    return new_tab


def join_split_rows(tab_rows: list) -> list:
    """ Если строка с заголовками таблицы показателей
    была разделена на две строки, то соединить их. """

    row_ind = 0
    new_tab = []

    # Цикл по строкам таблицы.
    while row_ind < len(tab_rows) - 1:

        # Проверка, что текущая строка относится к заголовкам таблицы.
        match_cur_row = re.search(
            f'{NAME}|{RESULT}|{REQUIREMENTS}',
            str(tab_rows[row_ind]),
            re.IGNORECASE)

        # Если текущая строка заголовки, то проверяем,
        # что следующая также относится к заголовкам таблицы.
        if match_cur_row:
            match_next_row = re.search(
                f'{NAME}|{RESULT}|{REQUIREMENTS}|{INDICATORS}',
                str(tab_rows[row_ind + 1]),
                re.IGNORECASE)

        # Если строка была разделена на две, то соединить в одну и добавить в результат.
        if match_cur_row and match_next_row:
            merged_row = [j + ' ' + k for j, k in zip(tab_rows[row_ind], tab_rows[row_ind + 1])]
            new_tab.append(merged_row)
            row_ind += 2

        # Если обычная строка, то просто добавить в результат.
        else:
            new_tab.append(tab_rows[row_ind])
            row_ind += 1

    # Добавить последнюю строку.
    new_tab.append(tab_rows[-1])
    return new_tab


def fix_centimeter_cell(tab_rows: list) -> list:
    """ Исправить ситуацию, когда в результате конвертации word
    файла произошло разделение ячейки на две, и 'см' и его
    производные перешли в отдельную ячейку. Если такой случай обнаружен,
    то берем значение из того же столбца, но строкой выше и добавляем
    оттуда значение."""

    row_ind = 0
    while row_ind < len(tab_rows) - 1:
        for cell_ind, cell in enumerate(tab_rows[row_ind]):
            patt = r'^(?<!\d)\(?см\d*\)?'
            if re.search(patt, cell):
                tab_rows[row_ind][cell_ind] = (
                        tab_rows[row_ind - 1][cell_ind] + ' ' + cell)
        row_ind += 1

    return tab_rows


def rm_invalid_cols_and_rows_from_tabs(tables: dict) -> dict:
    """ Удалить из таблиц пустые колонки, строки с одним значением,
    соединить разделенные строки. Получить все таблицы в виде словаря
    и перебрать их для каждой таблицы выполнить перечисленный набор действий."""

    new_tables = {}
    for key, tab_data in tables.items():

        # Если не таблица с результатами или пустая, то пропустить.
        if key[1] != 'RESULTS':
            new_tables[key] = tab_data
            continue
        if key[1] == 'RESULTS' and tab_data == []:
            continue

        # Набор действий с каждой таблицей.

        # Удалить строки с 1 значением.
        tab_data = rm_blank_rows_in_tab(tab_data)

        # Соединить разделенные на 2 строки в 1.
        tab_data = join_split_rows(tab_data)

        # Проверить на выделенную в отдельную ячейку 'см'
        tab_data = fix_centimeter_cell(tab_data)

        # Удалить пустую колонку слева.
        tab_data = rm_first_col_if_blank(tab_data)

        # Исправит разделение колонки на две с шифрами проб.
        united = join_divided_sample_code(tab_data)
        united = join_from_2_cols_to_1(united)

        if isinstance(united, tuple):
            new_tables[(key[0], united[1])] = united[0]
        else:
            new_tables[key] = united

    return new_tables


def divide_the_table(tables: dict) -> dict:
    """ В случае если две и более таблицы с показателями были
    соединены в одну, разделить их.

    Получить все таблицы в виде словаря, перебираем их с помощью цикла for.
    Для каждой таблицы запускаем внутренний цикл по строкам внутри таблицы.
    Если просматриваемая строка содержит указание на начало новой таблицы, то
    строки до текущей строки, записываем в качестве самостоятельной
    таблицы, изменяя ключ, добавляя в него, в номер таблицы значение ind(каждые 0,1).
    И продолжить просматривать строки далее.
    """
    new_tables = {}  # Результат работы функции
    patt_new_table = f'{NAME}|{RESULT}|{REQUIREMENTS}'  # Для поиска новой таблицы.

    # Перебираем все таблицы, выбранные из файла.
    for key, tab_data in tables.items():

        # Если не таблица с результатами, то просто добавить в результат.
        if key[1] != 'RESULTS':
            new_tables[key] = tab_data
            continue

        ind = 0.1  # Постоянное значение для добавления в названия таблиц.
        start_cur_tab = 0  # Индекс строки текущей таблицы.

        # Перебираем циклом строки в таблице.
        for numb, row in enumerate(tab_data[1:]):

            #  Собираем значения из списка в одну строку.
            row_str = "".join(row)

            # Если строка содержит слова идентификаторы начала новой таблицы.
            if re.search(patt_new_table, row_str):
                # Ключ для записи данных из таблицы со строками до обнаруженных идентификаторов.
                key_for_new_tab = (key[0] + ind, key[1])
                ind += 0.1
                # Запись выделенной таблицы до обнаруженных идентификаторов.
                new_tables[key_for_new_tab] = tab_data[start_cur_tab:numb + 1]
                start_cur_tab = numb + 1

        key_for_new_tab = (key[0] + ind, key[1])
        new_tables[key_for_new_tab] = tab_data[start_cur_tab:]

    return new_tables
