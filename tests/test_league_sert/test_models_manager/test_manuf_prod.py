"""
Тестирование создание объектов модели ManufProd.
"""
import pytest

from league_sert.models.models import ManufProd
from league_sert.models.models_creator import create_manuf_prod


@pytest.fixture(scope='module')
def test_data():
    """ Вернуть тестовые данные. """
    return {'name_indic': 'Внешний вид тары после гермостатирования. Микроскопия консервированного продукта',
            'Шифр пробы': '4225-1', 'Группа продукции': 'Продукция производителя',
            'Наименование продукции': 'Консервы. Оливки фаршированные лимоном', 'НД на продукцию': '-',
            'Дата производства продукции': '27.07.2023 г. Годен до 27.07.2026 г.',
            'Производитель (фирма, предприятие, организация)': 'La Roda de Andalucia',
            'Условия доставки': 'Автотранспорт', 'Температура при доставке проб': '+15°C',
            'result': 'не изменен<10',
            'norm': 'отсутствие дефектов не более 10 клеток м.о. в полезрения',
            'norm_doc': 'ГОСТ 26669-85',
            'conformity_main': True}


def test_create_manuf_prod(test_data):
    """ Протестировать создание модели основных данных. """
    object_of_model = create_manuf_prod(**test_data)
    assert isinstance(object_of_model, ManufProd)
    assert object_of_model.sample_code == test_data['Шифр пробы']
    assert object_of_model.prod_name == test_data['Наименование продукции']
    assert object_of_model.prod_date == test_data['Дата производства продукции']
    assert object_of_model.manuf == test_data['Производитель (фирма, предприятие, организация)']
    assert object_of_model.name_indic == test_data['name_indic']
    assert object_of_model.conformity_main == test_data['conformity_main']
    assert object_of_model.conformity_deviation == True
