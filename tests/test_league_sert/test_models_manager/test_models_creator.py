""" Тестирование вспомогательных функций. """
import datetime

import pytest

from league_sert.models.models_creator import (
    split_code_and_address, create_date, create_manuf_prod, fix_keys)


@pytest.mark.parametrize('sampling_place, apllicant_info, expect_address, expect_code', [
    ('г. Калуга, ул. Ленина, д.58 (№40515)',
     'АО «ДИКСИ ЮГ», ИНН: 5036045205',
     'г. Калуга, ул. Ленина, д.58',
     40515),

    ('№40515, г. Калуга, ул. Ленина, д.58',
     'АО «ДИКСИ ЮГ», ИНН: 5036045205',
     'г. Калуга, ул. Ленина, д.58',
     40515),

    ('г. Калуга, ул. Ленина, д.58 (40515)',
     'АО «ДИКСИ ЮГ», ИНН: 5036045205',
     'г. Калуга, ул. Ленина, д.58',
     40515),

    ('40515, г. Калуга, ул. Ленина, д.58',
     'АО «ДИКСИ ЮГ», ИНН: 5036045205',
     'г. Калуга, ул. Ленина, д.58',
     40515),

    ('МО, р.п. Калининец, в/ч 23626 (№ 50662)',
     'АО «ДИКСИ ЮГ», ИНН: 5036045205',
     'МО, р.п. Калининец, в/ч 23626',
     50662),

])
def test_split_code_and_address(sampling_place, apllicant_info, expect_address, expect_code):
    """ Тестирование разделения адреса магазина и его кода. """
    address, code = split_code_and_address(sampling_place, apllicant_info)
    assert isinstance(address, str)
    assert isinstance(code, int)
    assert address == expect_address
    assert code == expect_code


@pytest.mark.parametrize('date_, expected_date',
                         [
                             ('11 мая 2024', datetime.date(2024, 5, 11)),
                             ('11 мая 2024 г.', datetime.date(2024, 5, 11)),
                             ('11 мая 2024 года', datetime.date(2024, 5, 11)),
                             ('11  мая   2024 г.', datetime.date(2024, 5, 11)),
                             ('23  сентября   20 24 г.', datetime.date(2024, 9, 23)),

                         ])
def test_create_date(date_, expected_date):
    """ Тестирование создания объекта даты. """
    received_date = create_date(date_)
    assert isinstance(received_date, datetime.date)
    assert received_date == expected_date


# @pytest.mark.parametrize('table_data, expected_key')
# def test_fix_keys(table_data, ):
#     result = fix_keys(table_data, keys)
#     assert
