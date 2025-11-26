import pytest

from rename_files.rename_files import get_store_code, search_code
from tests.test_league_sert.test_data_preparaton.constants import TEST_WORD_FILES


@pytest.mark.parametrize('test_file, expected_store_code',
                         [
                             (TEST_WORD_FILES[0], '40515'),
                             (TEST_WORD_FILES[1], '50686'),
                             (TEST_WORD_FILES[2], '77189'),
                         ])
def test_get_store_code(test_file, expected_store_code):
    """ Тестирование получение кода магазина из файла с протоколом."""
    result_code = get_store_code(test_file)
    assert result_code == expected_store_code


@pytest.mark.parametrize('cell_text, expected_result',
                         [
                             ('АО «ДИКСИ ЮГ», ИНН: 5036045205', None),
                             ('МО, г. Подольск, ул. Юбилейная, д. 32 А', None),
                             ('МО, р.п. Калининец, в/ч 23626', None),
                             ('МО, р.п. Калининец, в/ч 23626 (№ 50662)', '50662'),
                             ('(№ 50662) МО, р.п. Калининец, в/ч 23626', '50662'),
                             ('МО, р.п. Калининец, в/ч 23626 № 50662', '50662'),
                             ('г. Калуга, ул. Ленина, д.58 (№40515)', '40515'),
                             ('№40515, г. Калуга, ул. Ленина, д.58 АО «ДИКСИ ЮГ», ИНН: 5036045205',
                              '40515'),
                             ('г. Калуга, ул. Ленина, д.58 (40515) АО «ДИКСИ ЮГ», ИНН: 5036045205'
                              'г. Калуга, ул. Ленина, д.58', '40515'),
                             ('40515, г. Калуга, ул. Ленина, д.58 АО «ДИКСИ ЮГ», ИНН: 5036045205'
                              'г. Калуга, ул. Ленина, д.58', '40515'),
                         ])
def test_search_code(cell_text, expected_result):
    """ Тестирование нахождения кода магазина при парсинге файла."""
    result = search_code(cell_text)
    assert result == expected_result

