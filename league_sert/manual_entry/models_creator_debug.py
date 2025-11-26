""" Модуль с кодом для создания объектов моделей при записи в БД через корректировки
файлов формата .docx
"""
import re
import sys
from pathlib import Path

from league_sert.data_preparation.file_parser import MainCollector
from league_sert.manual_entry.manual_handlers_exceptions import (
    get_address_and_code_handler, get_sampling_date_handler)
from league_sert.models.models_creator import (
    create_date, split_code_and_address, validate_attribute, create_instance, \
    ObjectsForDB, create_objects_same_cls)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if BASE_DIR not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from league_sert.models.models import MainProtocol


@create_instance
def create_main_protocol_debug(main_number, main_date, table_data: dict):
    """ Создать объект модели MainProtocol.  """

    for key in table_data.keys():
        match_ = re.search(r'З\s*а\s*я\s*в\s*и\s*т\s*е\s*л\s*ь', key, re.IGNORECASE)
        if match_:
            try:
                address, code = split_code_and_address(table_data['Место отбора проб'],
                                                       table_data[key])
                if address and code:
                    break
            except KeyError:
                address, code = get_address_and_code_handler()
                break

    main_date = create_date(main_date)
    try:
        sampling_date = create_date(table_data['Дата и время отбора проб'])
    except KeyError:

        sampling_date = get_sampling_date_handler()
        sampling_date = create_date(sampling_date)

    validate_attribute(MainProtocol, main_number, 'main_number')
    validate_attribute(MainProtocol, main_date, 'main_date')
    validate_attribute(MainProtocol, code, 'code')

    return MainProtocol(
        number=main_number,
        date=main_date,
        store_code=code,
        sampling_date=sampling_date,
        store_address=address)


def create_all_objects_debug(main_collector: MainCollector) -> ObjectsForDB:
    """ Создание из объекта класса MainCollector, содержащего все данные из
     файла, набора объектов всех моделей. """

    objects_of_models = {}

    for key, value in main_collector.data_from_tables.items():
        if key[1] == 'MAIN':
            objects_of_models[key] = create_main_protocol_debug(main_collector.main_number,
                                                          main_collector.main_date,
                                                          value)
        else:
            objects_of_models[key] = create_objects_same_cls(value, key[1])

    # Результатом будет словарь, в котором ключом будет tuple, где 1 значение порядковый номер,
    # 2 значение это тип объектов - класс, значением в словаре будет список объектов
    # определенной модели.
    return objects_of_models
