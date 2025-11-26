""" Тестирование модуля models_creator.py

Тестируем создание набора объектов из данных, собранных из word файла
при помощи main_collector.
"""
import pytest

from league_sert.models.models import MainProtocol, ProdControl, ManufProd, Air, StoreProd, Washings
from league_sert.models.models_creator import create_common_violations, create_all_objects
from tests.test_league_sert.test_models_manager.test_data_main_collector import full_main_collector


data_proc_viol = {'indicators': [{'violations_of_norms': (True, True)},
                                 {'violations_of_norms': (False, True)},
                                 {'violations_of_norms': (False, False)}]}
data_proc_viol_not_list = {'indicators': [{'violations_of_norms': (False, False)}]}


@pytest.mark.parametrize('data, expected', [
    (data_proc_viol, [True, True]),
    (data_proc_viol_not_list, [False, False])])
def test_process_violations(data, expected):
    """ Проверить выдачу общего для всего образца вывода
    о нарушении результатов исследования нормам. """
    result = create_common_violations(data)
    assert result == expected


def test_create_all_objects(main_collector=full_main_collector()):
    """ Тестирование создание из данных, собранных MainCollector набора
    объектов моделей. """
    objects = create_all_objects(main_collector)

    assert len(objects) == 5
    assert isinstance(objects, dict)
    assert isinstance(objects[(1, 'MAIN')], MainProtocol)

    assert isinstance(objects[(2, 'store_prod')], list)
    assert isinstance(objects[(2, 'store_prod')][0], StoreProd)
    assert len(objects[(2, 'store_prod')]) == 17

    assert isinstance(objects[(7, 'air')], list)
    assert len(objects[(7, 'air')]) == 1
    assert isinstance(objects[(7, 'air')][0], Air)

    assert isinstance(objects[(9, 'washings')], list)
    assert isinstance(objects[(9, 'washings')][0], Washings)
    assert len(objects[(9, 'washings')]) == 9

    assert isinstance(objects[(12, 'PROD_CONTROL')], list)
    assert isinstance(objects[(12, 'PROD_CONTROL')][0], ProdControl)
    assert len(objects[(12, 'PROD_CONTROL')]) == 16
