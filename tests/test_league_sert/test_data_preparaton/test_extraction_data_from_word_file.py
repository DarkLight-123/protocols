"""Тестирование парсинга текста из word файлов. """

import pytest
from league_sert.data_preparation.file_parser import MainCollector
from league_sert.data_preparation.launch_data_preparation import extract_and_prepare_data
from tests.test_league_sert.test_data_preparaton.constants import TEST_WORD_FILES, COLLECTORS


@pytest.mark.parametrize('file, expected_collector',
                         [
                             (TEST_WORD_FILES[0], COLLECTORS[0]),
                             (TEST_WORD_FILES[1], COLLECTORS[1]),
                             (TEST_WORD_FILES[2], COLLECTORS[2]),
                         ])
def test_collect_data(file, expected_collector):
    """Тестирование данных на стадии собирания данных, то есть метода
    MainCollector.collect_all_data(). Таблиц до объединения и определения
    типа таблицы. """

    data_collector = MainCollector(file)
    data_collector.collect_all_data()
    expected_collector = expected_collector()
    print(data_collector.main_date)
    print(expected_collector)
    assert data_collector.main_number == expected_collector.main_number
    assert data_collector.main_date == expected_collector.main_date
    assert data_collector.prod_control_data == expected_collector.prod_control_data
    assert list(data_collector.data_from_tables.keys()) == expected_collector.keys_after_collect


@pytest.mark.parametrize('file, expected_collector',
                         [
                             (TEST_WORD_FILES[0], COLLECTORS[0]),
                             (TEST_WORD_FILES[1], COLLECTORS[1]),
                             (TEST_WORD_FILES[2], COLLECTORS[2]),

                         ])
def test_extract_and_prepare_data(file, expected_collector):
    """Тестирование данных на стадии собирания данных, преобразования их,
    и подготовки к записи в БД, то есть выполнения функции extract_and_prepare_data(file),
    которая возвращает таблицы в уже объединенном и подготовленном виде. """

    data_collector = extract_and_prepare_data(file)
    expected_collector = expected_collector()
    assert data_collector.main_number == expected_collector.main_number
    assert data_collector.main_date == expected_collector.main_date
    assert data_collector.prod_control_data == expected_collector.prod_control_data
    assert data_collector.data_from_tables.keys() == expected_collector.data_from_tables.keys()
