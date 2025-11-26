""" Протестировать создание модели ProdControl """
import datetime

import pytest

from league_sert.models.models import ProdControl
from league_sert.models.models_creator import create_prod_control


@pytest.fixture(scope='module')
def test_data():
    """ Вернуть тестовые данные. """
    return {
        'number_of_protocol': '4644/24-Д',
        'date_of_protocol': '16 мая 2024',
        'act': '4644 от 13.05.2024',
        'place_of_measurement': 'г. Кострома, ул. Юрия Беленогова, д. 17А, магазин № 44433',
        'inner_conclusion': '- на момент проведения измерений параметры микроклимата, '
                            'уровни шума и общей вибрации соответствуют требованиям',
        'name_indic': 'Отдел«Овощи/фрукты», рабочее место работника торгового зала(Па)',
        'parameter': 'Относительная влажность воздухаОтносительная влажность воздуха',
        'name': 'Температура воздуха 0,1м',
        'sampling_site': 'Отдел«Овощи/фрукты», рабочее место работника торгового зала(Па)',
        'unit': '%',
        'result': '41,1±5,8',
        'norm': '15-75',
        'conformity_main': True,
        'conformity_deviation': True}


def test_create_prod_control(test_data):
    """ Протестировать создание модели ProdControl - контроля производства. """
    object_of_model = create_prod_control(**test_data)
    assert isinstance(object_of_model, ProdControl)
    assert object_of_model.number == test_data['number_of_protocol']
    assert object_of_model.date == datetime.date(2024, 5, 16)
    assert object_of_model.act == test_data['act']
    assert object_of_model.conclusion == test_data['inner_conclusion']
    assert object_of_model.conclusion_compl == True
    assert object_of_model.name_indic == test_data['name']
    assert object_of_model.sampling_site == test_data['name_indic']
    assert object_of_model.conformity_main == test_data['conformity_main']
    assert object_of_model.conformity_deviation == test_data['conformity_deviation']
