""" Протестировать создание модели MainProtocol """
import pytest
import datetime

from league_sert.models.exceptions import AttrNotFoundError
from league_sert.models.models import MainProtocol
from league_sert.models.models_creator import create_main_protocol


@pytest.fixture(scope='module')
def test_data():
    """ Вернуть тестовые данные. """
    main_number = '4225/24-Д'
    main_date = '23 мая 2024'
    table_data = {'Заявитель. ИНН': 'АО «ДИКСИЮГ», ИНН 5036045205',
        'Ненужный параметр': 'ненужное значение',
        'Место отбора проб': 'г. Кострома, ул. Юрия Беленогова, д. 17 А (44433)',
        'Дата и время отбора проб': '03.05.2024 г., 13 ч. 30 мин.',
    }

    return {'main_number': main_number,
            'main_date': main_date,
            'table_data': table_data}


def test_create_main_protocol(test_data):
    """ Протестировать создание модели основных данных. """
    result_object = create_main_protocol(test_data['main_number'],
                                         test_data['main_date'],
                                         test_data['table_data']
                                         )
    assert isinstance(result_object, MainProtocol)
    assert result_object.number == test_data['main_number']
    assert result_object.date == datetime.date(2024, 5, 23)
    assert result_object.sampling_date == datetime.date(2024, 5, 3)
    assert result_object.store_code == 44433
    assert result_object.store_address == 'г. Кострома, ул. Юрия Беленогова, д. 17 А'


@pytest.fixture(scope='module')
def test_data_wrong():
    """ Вернуть тестовые данные. """
    main_number = ''
    main_date = '23 мая 2024'
    table_data = {
        'Ненужный параметр': 'ненужное значение',
        'Место отбора проб': 'г. Кострома, ул. Юрия Беленогова, д. 17 А (44433)',
        'Дата и время отбора проб': '03.05.2024 г., 13 ч. 30 мин.',
    }

    return {'main_number': main_number,
            'main_date': main_date,
            'table_data': table_data}


def test_create_air_error(test_data_wrong):
    """ Протестировать возникновение исключения при создании объекта класса Air. """
    with pytest.raises(AttrNotFoundError) as excinfo:
        create_main_protocol(**test_data_wrong)
    assert 'MainProtocol' in str(excinfo.value)
    assert 'main_number' in str(excinfo.value)
