import pytest

from league_sert.models.exceptions import AttrNotFoundError
from league_sert.models.models import Air
from league_sert.models.models_creator import create_air


@pytest.fixture(scope='module')
def test_data():
    """ Вернуть тестовые данные. """
    return {'name': 'Плесени,КОЕ на чашке',
            'name_indic': 'Холодильная камера «Молочные продукты»',
            'Шифр пробы': '4639 - 1',
            'Объект исследования': 'Воздух (микробная обсемененность)',
            'Ненужный ключ': 'ненужное значение',
            'result': '0', 'norm': '-',
            'norm_doc': 'СП 4695-88',
            'sampling_site': 'Холодильная камера «Молочные продукты»',
            'conformity_main': True}


def test_create_air(test_data):
    """ Протестировать создание модели основных данных. """
    result_object = create_air(**test_data)
    assert isinstance(result_object, Air)
    assert result_object.sample_code == test_data['Шифр пробы']
    assert result_object.name_indic == test_data['Объект исследования']
    assert result_object.result == test_data['result']
    assert result_object.norm == test_data['norm']
    assert result_object.conformity_main == test_data['conformity_main']
    assert result_object.sampling_site == test_data['sampling_site']
    assert result_object.conformity_deviation is True
    assert isinstance(result_object.conformity_main, bool)


@pytest.fixture(scope='module')
def test_data_wrong():
    """ Вернуть тестовые данные. """
    return {'name_indic': '',
            'Шифр пробы': '4639 - 1',
            'Объект исследования': 'Воздух (микробная обсемененность)',
            'Ненужный ключ': 'ненужное значение',
            'result': '0', 'norm': '-',
            'norm_doc': 'СП 4695-88', 'conformity_main': True}


def test_create_air_error(test_data_wrong):
    """ Протестировать возникновение исключения при создании объекта класса Air. """
    with pytest.raises(AttrNotFoundError) as excinfo:
        create_air(**test_data_wrong)
    assert 'Air' in str(excinfo.value)
    assert 'name_indic' in str(excinfo.value)
