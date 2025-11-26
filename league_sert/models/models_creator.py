""" Модуль с кодом для создания объектов моделей.

Функции:
    - Создание объектов, соответствующей модели:
    - create_main_protocol
    - create_manuf_prod
    - create_store_prod
    - create_air
    - create_water
    - create_washings
    - create_prod_control

    - split_code_and_address:
        Разбить место отбора проб на адрес и код магазина
    - create_date:
        Строку с датой преобразовать в объект datetime.

    - create_common_violations: сделать и вернуть вывод
    о наличии нарушений нормам для всей таблицы.

    - create_objects: получает на вход объект класса MainCollector,
    содержащий все данные, собранные с файла формата .docx.
    Обрабатывает их и возвращает структуру данных:
    Dict[Tuple[int, str], Union[MainProtocol, ManufProd, ProdControl,
                                Air, Water, Washings, StoreProd]]

Пример использования:
    - objects_for_db = create_objects(main_collector)

"""
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, Union, List
from datetime import datetime, date

from league_sert.constants import MONTHS, TABLE_TYPES_IN_RUS
from league_sert.data_preparation.exceptions import AddressNotFoundError
from league_sert.data_preparation.file_parser import MainCollector
from league_sert.exceptions import TypeIndicatorsError
from league_sert.manual_entry.exceptions import MissedKeyCreateInstError
from league_sert.models.exceptions import AttrNotFoundError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if BASE_DIR not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from league_sert.models.models import (MainProtocol, ManufProd, Air, Water,
                                       ProdControl, Washings, StoreProd)


def create_common_violations(table_data: dict) -> List[bool]:
    """Вернуть вывод о наличии нарушений результатов
    нормам для всей таблицы целиком.
    :param table_data: Словарь с данными по одной таблиц показателей.
    :return: Список булевых значений, где каждое значение указывает
    на наличие или отсутствие нарушений для показателей всей таблицы. """

    if isinstance(table_data['indicators'], list):
        main_viol = False
        deviation_viol = False
        for sub_table in table_data['indicators']:
            if sub_table['violations_of_norms'][0]:
                main_viol = True
            if sub_table['violations_of_norms'][1]:
                deviation_viol = True
        return [main_viol, deviation_viol]
    raise TypeIndicatorsError()


def split_code_and_address(sampling_place: str, apllicant_info: str) -> tuple[str, int]:
    """ Разбить место отбора проб на адрес и код магазина. """
    pattern = r'(.+)\(№?\s*>?(\d+)|(\d{5})(.*)'
    match = re.search(pattern, sampling_place)

    if match:
        if match.group(1):
            address = match.group(1).strip(', ()')
            code = int(match.group(2))
        else:
            address = match.group(4).strip(', ()')
            code = int(match.group(3))

    else:
        address = sampling_place
        code = re.search(r'\d{5}', apllicant_info).group()

    if address and code:
        return address, code
    raise AddressNotFoundError(sampling_place + ' ' + apllicant_info)


def remove_spaces_between_numbers(s):
    """ Убрать пробелы в годе, 20 23 """
    return re.sub(r'(\d)\s+(\d)', r'\1\2', s)


def create_date(date_: str) -> date:
    """ Строку с датой преобразовать в объект datetime. """

    date_ = re.sub(r'\s{2,}', ' ', date_)
    date_ = re.sub(r'(\d{2})[-.](\d{2})[-.](\d{4})', r'\1.\2.\3', date_)
    date_ = remove_spaces_between_numbers(date_)
    date_ = date_.replace(',', '.')
    match = re.search(r'\d{2}.\d{2}.\d{2,4}', date_)
    if not match:
        date_ = date_.split(' ')
        if len(date_) < 3:
            raise ValueError('Некорректный формат даты.')
        date_[1] = MONTHS[date_[1]]
        date_ = '.'.join(date_[:3])
    else:
        date_ = match.group()

    date_ = datetime.strptime(date_, '%d.%m.%Y')
    return date_.date()


def remove_digits_from_name(text: str):
    """ Убрать _ и числа из названий показателей."""
    pattern = r'_\d+$'
    return re.sub(pattern, '', text)


def validate_attribute(class_name, value, attr_name):
    """ Проверить, что атрибут не None и не пустая строка. """
    if value is None or value == '':
        raise AttrNotFoundError(class_name, attr_name)


def fix_keys(data: dict, keys: dict) -> dict:
    """
    Исправить орфографические ошибки в ключах
    данных, подготовленных для создания моделей.

    :param data: данные, собранные из word файла и подготовленные для создания моделей
    :param keys: словарь, где ключи - правильное написание ключей, а значения паттерны
                для нахождения неправильного написания в ключах.
    :return: словарь с исправленными ключами.
    """

    new_data = {**data}
    for data_key in data.keys():
        for right_key, patt_wrong_key in keys.items():
            match_ = re.search(patt_wrong_key, data_key, re.IGNORECASE)
            if match_:
                new_data[right_key] = data[data_key]

    return new_data


def create_instance(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except KeyError as err:
            cls_inst = str(func.__name__).strip('create_')
            in_rus = TABLE_TYPES_IN_RUS[cls_inst]
            key_ = str(err)
            raise MissedKeyCreateInstError(in_rus, key_)

    return wrapper


@create_instance
def create_main_protocol(main_number, main_date, table_data: dict):
    """ Создать объект модели MainProtocol.  """

    for key in table_data.keys():
        match_ = re.search(r'З\s*а\s*я\s*в\s*и\s*т\s*е\s*л\s*ь', key)
        if match_:
            address, code = split_code_and_address(table_data['Место отбора проб'],
                                                   table_data[key])
            if address and code:
                break

    main_date = create_date(main_date)
    sampling_date = create_date(table_data['Дата и время отбора проб'])

    validate_attribute(MainProtocol, main_number, 'main_number')
    validate_attribute(MainProtocol, main_date, 'main_date')
    validate_attribute(MainProtocol, code, 'code')

    return MainProtocol(
        number=main_number,
        date=main_date,
        store_code=code,
        sampling_date=sampling_date,
        store_address=address)


@create_instance
def create_prod_control(**kwargs):
    """ Создать объект модели ProdControl.  """
    return ProdControl(
        number=kwargs['number_of_protocol'],
        date=create_date(kwargs['date_of_protocol']),
        act=kwargs['act'],
        address=kwargs['place_of_measurement'],
        conclusion=kwargs['inner_conclusion'],
        conclusion_compl=True if kwargs['inner_conclusion'] else False,
        name_indic=kwargs['name'],
        result=kwargs['result'],
        norm=kwargs['norm'],
        conformity_main=kwargs['conformity_main'],
        conformity_deviation=kwargs.get('conformity_deviation', True),
        sampling_site=remove_digits_from_name(kwargs['sampling_site']),
        unit=kwargs['unit'])


@create_instance
def create_manuf_prod(**kwargs):
    """ Создать объект модели ManufProd.  """

    return ManufProd(
        sample_code=kwargs['Шифр пробы'],
        prod_name=kwargs['Наименование продукции'],
        prod_date=kwargs['Дата производства продукции'],
        manuf=kwargs['Производитель (фирма, предприятие, организация)'],

        name_indic=kwargs['name_indic'],
        result=kwargs['result'],
        norm=kwargs['norm'],
        conformity_main=kwargs['conformity_main'],
        conformity_deviation=kwargs.get('conformity_deviation', True),
        norm_doc=kwargs['norm_doc'])


@create_instance
def create_store_prod(**kwargs):
    """ Создать объект модели ManufProd.  """
    return StoreProd(
        sample_code=kwargs['Шифр пробы'],
        prod_name=kwargs['Наименование продукции'],
        prod_date=create_date(kwargs['Дата производства продукции']),
        manuf=kwargs['Производитель (фирма, предприятие, организация)'],
        name_indic=kwargs['name_indic'],
        result=kwargs['result'],
        norm=kwargs['norm'],
        conformity_main=kwargs['conformity_main'],
        conformity_deviation=kwargs.get('conformity_deviation', True),
        norm_doc=kwargs['norm_doc'])


@create_instance
def create_air(**kwargs):
    """ Создать объект модели Air. """
    validate_attribute(Air, kwargs['name_indic'], 'name_indic')
    return Air(
        sample_code=kwargs['Шифр пробы'],
        name_indic=kwargs['Объект исследования'],
        result=kwargs['result'],
        norm=kwargs['norm'],
        conformity_main=kwargs['conformity_main'],
        conformity_deviation=kwargs.get('conformity_deviation', True),
        sampling_site=kwargs['name_indic'],
        norm_doc=kwargs['norm'])


@create_instance
def create_water(**kwargs):
    """ Создать объект модели Water.  """
    return Water(
        test_object=kwargs['Объект исследования'],
        sample_code=kwargs['Шифр пробы'],
        name_indic=kwargs['name_indic'],
        result=kwargs['result'],
        norm=kwargs['norm'],
        conformity_main=kwargs['conformity_main'],
        conformity_deviation=kwargs.get('conformity_deviation', True),
        norm_doc=kwargs['norm_doc'])


@create_instance
def create_washings(**kwargs):
    """ Создать объект модели washings.  """
    return Washings(
        sampling_site=remove_digits_from_name(kwargs['sampling_site']),
        name_indic=kwargs['name_indic'],
        result=kwargs['result'],
        norm=kwargs['norm'],
        conformity_main=kwargs['conformity_main'],
        conformity_deviation=kwargs.get('conformity_deviation', True),
        norm_doc=kwargs['norm_doc_of_method'])


ObjectsForDB = Dict[Tuple[int, str], Union[
    MainProtocol, ManufProd, ProdControl, Air, Water, Washings, StoreProd]]


def create_objects_same_cls(table_data: dict, type_table):
    """ Создание объектов одного и того же класса, в результате будет создан
    объект класса на каждый показатель. """

    methods = {
        'manuf_prod': create_manuf_prod,
        'store_prod': create_store_prod,
        'air': create_air,
        'water': create_water,
        'washings': create_washings,
        'PROD_CONTROL': create_prod_control}

    result = []
    method = methods.get(type_table, None)
    indicators = table_data['indicators']
    del table_data['indicators']
    for row in indicators:
        for name_indic, value in row.items():
            result.append(method(name_indic=name_indic, **table_data, **value))
    return result


def create_all_objects(main_collector: MainCollector) -> ObjectsForDB:
    """ Создание из объекта класса MainCollector, содержащего все данные из
     файла, набора объектов всех моделей. """

    objects_of_models = {}

    for key, value in main_collector.data_from_tables.items():
        if key[1] == 'MAIN':
            objects_of_models[key] = create_main_protocol(main_collector.main_number,
                                                          main_collector.main_date,
                                                          value)
        else:
            objects_of_models[key] = create_objects_same_cls(value, key[1])

    # Результатом будет словарь, в котором ключом будет tuple, где 1 значение порядковый номер,
    # 2 значение это тип объектов - класс, значением в словаре будет список объектов
    # определенной модели.
    return objects_of_models
