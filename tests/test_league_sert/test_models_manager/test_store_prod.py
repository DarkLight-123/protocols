""" Тестирование создание объекта класса StoreProd"""
import datetime

import pytest

from league_sert.models.models import StoreProd
from league_sert.models.models_creator import create_store_prod


@pytest.fixture(scope='module')
def test_data():
    """ Вернуть тестовые данные. """
    return {'name_indic': 'Внешний вид тары после гермостатирования. Микроскопия консервированного продукта',
            'Шифр пробы': '4225-1', 'Группа продукции': 'Продукция производителя',
            'Наименование продукции': 'Консервы. Оливки фаршированные лимоном', 'НД на продукцию': '-',
            'Дата производства продукции': '27.07.2023 г. Годен до 27.07.2026 г.',
            'Производитель (фирма, предприятие, организация)': 'La Roda de Andalucia',
            'Условия доставки': 'Автотранспорт', 'Температура при доставке проб': '+15°C',
            'Нарушения при доставке проб': 'Упаковка не нарушена', 'Вид упаковки': 'Производственная упаковка',
            'Масса пробы': '300 г',
            'Цель исследования': 'Производственный контроль. На соответствие требованиям ТР ТС 021/2011 «О безопасности пищевой продукции», утв. Решением КТС от 9 декабря 2011 года№ 880',
            'Сведения о СИ': 'Генератор концентрации биодоз Delta Dilutor Standard, (39629-08), 10002510S/448; анализатор жидкости "Эксперт-001" № 7106; pH-метр и иономер -150МИ №8297',
            'Дата проведения исследований': '02.05.2024 г.- 13.05.2024 г.', 'result': 'не изменен<10',
            'norm': 'отсутствие дефектов не более 10 клеток м.о. в полезрения', 'norm_doc': 'ГОСТ 26669-85',
            'conformity_main': True}


def test_create_manuf_prod(test_data):
    """ Протестировать создание модели основных данных. """
    object_of_model = create_store_prod(**test_data)
    assert isinstance(object_of_model, StoreProd)
    assert object_of_model.sample_code == test_data['Шифр пробы']
    assert object_of_model.prod_name == test_data['Наименование продукции']
    assert object_of_model.prod_date == datetime.date(2023, 7, 27)
    assert object_of_model.manuf == test_data['Производитель (фирма, предприятие, организация)']
    assert object_of_model.name_indic == test_data['name_indic']
    assert object_of_model.conformity_main == test_data['conformity_main']
    assert object_of_model.conformity_deviation == True
