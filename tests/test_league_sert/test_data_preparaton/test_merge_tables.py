""" Тестирование модуля merge_tables. """
import pytest

from league_sert.data_preparation.merge_tables import (
    join_sample_and_results, remove_results_table, refine_and_merge_tables)

from tests.test_league_sert.test_data_preparaton.data_for_test.test_data_for_merge import (
    data_input_for_merge_1, DATA_FOR_MERGE)


def test_join_sample_and_results():
    """ Тестируется правильное объединение таблиц с образцами
     и результатами исследований, результатом должен быть перенос таблицы
     с результатами в поле indicators таблицы образца."""

    result_tables = join_sample_and_results(data_input_for_merge_1)
    assert result_tables[(1, 'SAMPLE')]['indicators'] == [(data_input_for_merge_1[(2, 'RESULTS')])]
    assert result_tables[(3, 'SAMPLE')]['indicators'] == [(data_input_for_merge_1[(4, 'RESULTS')])]
    assert result_tables[(5, 'SAMPLE')]['indicators'] == [(data_input_for_merge_1[(6, 'RESULTS')]),
                                                          (data_input_for_merge_1[(7, 'RESULTS')])]


@pytest.mark.parametrize("input_data", [
    (DATA_FOR_MERGE[0]),
    (DATA_FOR_MERGE[1]),
    (DATA_FOR_MERGE[2])
])
def test_remove_results_table(input_data):
    """ Тестируется удаление таблиц с результатами
    исследований после их добавления в поле indicators."""
    tables = join_sample_and_results(input_data)
    result_tables = remove_results_table(tables)
    print(result_tables)
    result_keys = {i[1] for i in result_tables.keys()}
    assert 'RESULTS' not in result_keys


@pytest.mark.parametrize("input_data, expected_tables", [
    (DATA_FOR_MERGE[0], [(0, 'MAIN'), (1, 'manuf_prod'), (3, 'manuf_prod'),
                         (5, 'manuf_prod'), (8, 'manuf_prod'),
                         (10, 'air'), (13, 'PROD_CONTROL')]),
    (DATA_FOR_MERGE[1], [(0, 'MAIN'), (1, 'manuf_prod'), (4, 'manuf_prod'),
                         (6, 'manuf_prod'), (10, 'manuf_prod'), (12, 'air'),
                         (15, 'PROD_CONTROL')]),
    (DATA_FOR_MERGE[2], [(0, 'MAIN'), (1, 'store_prod'),
                         (5, 'air'), (7, 'washings'),
                         (10, 'PROD_CONTROL')]
     )])
def test_refine_and_merge_tables(input_data, expected_tables):
    """ Протестировать работу функции по объединению
    и присвоению наименования вида таблицы. Входные данные - таблицы типа
    RESULTS и SAMPLE должны быть объединены и переименованы."""
    result_data = refine_and_merge_tables(input_data)
    assert list(result_data.keys()) == expected_tables
