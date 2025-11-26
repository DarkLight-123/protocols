import pytest

from league_sert.models.models import Water
from league_sert.models.models_creator import create_water


@pytest.fixture(scope='function')
def test_data():
    """ Вернуть тестовые данные. """
    return {'name_indic': 'Общее микробное число, КОЕ/см³, (ОМЧ)', 'Шифр пробы': '2890-1',
            'Объект исследования': 'Вода питьевая. Комната принятия пищи',
            'Условия доставки': 'Автотранспорт, сумка-холодильник', 'Температура при доставке проб': '+4°С',
            'Нарушения при доставке проб': 'Упаковка не нарушена', 'Упаковка': 'Стерильные стеклянные бутыли',
            'Масса пробы': '0,5л*4',
            'Цель исследований': 'Производственный контроль. На соответствие СанПиН 1.2.3684-21; Сан-\nПиН 1.2.3685-21',
            'Сведения о СИ': 'Весы лабораторные JW-1, № 0509082; анализатор жидкости мод. Эксперт-001, №7106.',
            'Дата проведения исследований': '03.04.2024 г.-05.04.2024 г.', 'result': '0', 'norm': 'Не более 50',
            'norm_doc': 'МУК 4.2.3963-23/МУК 4.2.1018-01', 'conformity_main': True}


def test_create_main_protocol(test_data):
    """ Протестировать создание модели основных данных. """
    object_of_model = create_water(**test_data)
    assert isinstance(object_of_model, Water)
    assert object_of_model.test_object == test_data['Объект исследования']
    assert object_of_model.sample_code == test_data['Шифр пробы']
    assert object_of_model.name_indic == test_data['name_indic']
    assert object_of_model.result == test_data['result']
    assert object_of_model.norm == test_data['norm']
    assert object_of_model.conformity_main == test_data['conformity_main']
