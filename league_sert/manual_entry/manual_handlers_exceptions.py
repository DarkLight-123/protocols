"""
Обработчики ошибок при записи данных из файлов формата .docx вручную через корректировки файлов.
"""
import re

from league_sert.constants import MONTHS


def get_address_and_code_handler():
    code_from_user = None
    address_from_user = None

    while not code_from_user:
        code_from_user = input('Введите код магазина - 5 цифр, затем нажмите <Enter>\n>>>')
        code = re.search(r'\d{5}', code_from_user)
        if not code or code.group().isalpha():
            print('Неверный ввод, введите 5 цифр без пробелов и других знаков, букв,'
                  'затем нажмите <Enter>.\n>>>')
            continue
        else:
            code_from_user = code.group()

    while not address_from_user:
        address_from_user = input('Введите адрес магазина, затем нажмите <Enter>\n>>>')
        if not address_from_user:
            print('Адрес не введен, введите адрес, затем нажмите <Enter>.\n>>>')
            continue
        break
        #     raise ValueError('Адрес не введен, введите адрес, затем нажмите <Enter>.\n>>>')

    return address_from_user, code_from_user


def get_sampling_date_handler():
    date_from_user = None
    while not date_from_user:
        date_from_user = input('Введите дату отбора проб из основной таблицы в формате <16.12.2024>\n>>>')
        check_date = re.search(r'\d{2}\.\d{2}d.\d{4}', date_from_user)

        if not check_date:
            print('Введите дату отбора проб из основной таблицы в формате <31.12.2024>\n>>>')
            continue
        date_from_user = check_date.group()

    day_month_year = re.search(r'(\d{2})[-\\\.\s](\d{2})[-\\\.\s](\d{4})', date_from_user)

    MONTHS_REV = {v: k for k, v in MONTHS.items()}
    date_from_user = day_month_year.group(1) + ' ' + MONTHS_REV[day_month_year.group(2)] + ' ' + day_month_year.group(3)

    return date_from_user


def get_main_number_and_date_handler():
    number_from_user = None
    date_from_user = None

    while not number_from_user:
        number = input('Введите основной номер протокола испытаний, например "1111/24",'
                                 'затем нажмите <Enter>.\n>>>')
        number_from_user = re.search(r'\d{1,5}[\\/]\d{2}', number)

        if not number_from_user:
            print('Неверный ввод.')
            continue
        else:
            number_from_user = number_from_user.group().replace('\\', '/') + '-Д'

    while not date_from_user:
        date_from_user = input('Введите основную дату протокола испытаний, например "13.09.2024",'
                               'затем нажмите <Enter>.\n>>>')
        if not date_from_user:
            print('Неверный ввод.')
            continue
        break
        #     raise ValueError('Адрес не введен, введите адрес, затем нажмите <Enter>.\n>>>')

    return number_from_user, date_from_user


def passed_main_prot_table(file):
    print(f'В открытом через word файле {file}. Не обнаружена таблица '
          f'с основными данными по протоколу исследования.\nПерепроверьте '
          f'таблицу, в том числе проверьте Правильно ли написано слово "Заявитель."\n'
          f'Внесите изменения в файл, сохраните, затем нажмите <Enter>.\t>>>')
    input()


def handle_missed_table(error, file):
    print(error.msg)
    print(f'В открытом через word файле {file}. Внесите изменения в файл, '
          f'сохраните, затем нажмите <Enter>.\t>>>')
    user_input = input()


def handle_missed_key_create_inst_error(error, file):
    print(error.msg)
    print(f'В открытом через word файле {file}. Внесите изменения в файл, '
          f'сохраните, затем нажмите <Enter>.\t>>>')
    input()


def handle_date_missed_error(error, file):
    print(error)
    print(f'В файле {file} возможно не удалось распознать дату и номер протокола.\n'
          f' В открытом через word файле {file} проверьте основные дату и номер протокола, если '
          f'дата или номер протокола не пропечатаны, а сохранены в качестве рисунка, допечатайте их '
          f'в word файл с точным соблюдением стиля, в месте, где они должны находиться. '
          f'сохраните, затем нажмите <Enter>.\t>>>')
    input()
