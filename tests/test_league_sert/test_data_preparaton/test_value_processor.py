""" Тестирование модуля value_processor."""
import pytest

from league_sert.constants import ComparTypes, ConvertValueTypes
from league_sert.data_preparation.exceptions import DetermineValueTypeError
from league_sert.data_preparation.value_processor import (define_value_type,
                                                          to_calculate_the_value)

PLUS: str = r'\d\s?[+±]\s?\d'  # 16,34±0,15;  +
MULTIPLICATION: str = r'\d\s?[•■]\s?\d'  # 1 ■ 101², 1 • 10²
NO_MORE: str = r'до \d+,?\d*'  # до 1,5
WITHIN: str = r'\d+\,?\d*\s?-\s?\d+\,?\d*\b'  # 2,0 - 4,2
LESS: str = r'менее \d+,?\d*'  # менее 0,10
NOT_FOUND: str = r'не обнаружено|не обнаружены'  # не обнаружено в 25,0 г
DIGIT: str = r'\d+,?\d*'  # 9,0
NONE: str = r'^\-$|^$'  # '-'
NO_CHANGE: str = r'отсутствие изменений|отсутствие'
NOT_ALLOWED: str = r'не допускаются'


@pytest.mark.parametrize(
    'value, types_of_value, expecting_type', [
        ('не допускаются', ComparTypes, ComparTypes.NOT_ALLOWED),
        ('Отсутствие', ComparTypes, ComparTypes.NOT_ALLOWED),
        ('-', ComparTypes, ComparTypes.NOT_ALLOWED),
        ('-', ConvertValueTypes, ConvertValueTypes.NONE),
        ('-', ComparTypes, ComparTypes.NOT_ALLOWED),
        ('0', ComparTypes, ComparTypes.DIGIT),
        ('0,4, не более', ComparTypes, ComparTypes.NO_MORE),
        ('18-27', ComparTypes, ComparTypes.WITHIN),
        ('0,4, не более', ComparTypes, ComparTypes.NO_MORE),
        ('до 1,5', ComparTypes, ComparTypes.UP_TO),
        ('не менее 1,5', ComparTypes, ComparTypes.AT_LEAST),
        ('20,3±0,6', ConvertValueTypes, ConvertValueTypes.PLUS),
        ('0,4, не более', ConvertValueTypes, ConvertValueTypes.DIGIT),
        ('0', ConvertValueTypes, ConvertValueTypes.DIGIT),
        ('Отсутствие', ConvertValueTypes, ConvertValueTypes.NO_CHANGE),
        ('1 • 10²', ConvertValueTypes, ConvertValueTypes.MULTIPLICATION),
        ('5,5*102', ConvertValueTypes, ConvertValueTypes.MULTIPLICATION),
        ('5,5x102', ConvertValueTypes, ConvertValueTypes.MULTIPLICATION),
        ('не обнаружено в 25,0 г', ConvertValueTypes, ConvertValueTypes.NOT_FOUND),
        ('9,0', ConvertValueTypes, ConvertValueTypes.DIGIT),
        ('5,5х10²', ConvertValueTypes, ConvertValueTypes.MULTIPLICATION)])
def test_define_value_type(value, types_of_value, expecting_type):
    """ Проверка определения типа сравнения и типа значения для преобразования. """
    result_type = define_value_type(value, types_of_value)
    assert result_type == expecting_type.name


def test_define_value_type_raises_error_compar_types():
    """ Проверка возникновения исключения при типе значения,
    не подпадающего под паттерны сравнения - ComparTypes."""
    invalid_value = "some_invalid_value"
    types_of_value = ComparTypes  # Передавайте в список подходящие enum классы
    with pytest.raises(DetermineValueTypeError) as excinfo:
        define_value_type(invalid_value, types_of_value)
    assert invalid_value in str(excinfo.value)
    assert str(types_of_value) in str(excinfo.value)


def test_define_value_type_raises_error_convert_value_types():
    """ Проверка возникновения исключения при типе значения,
    не подпадающего под паттерны сравнения - ConvertValueTypes."""
    invalid_value = "some_invalid_value"
    types_of_value = ConvertValueTypes
    with pytest.raises(DetermineValueTypeError) as excinfo:
        define_value_type(invalid_value, types_of_value)
    assert invalid_value in str(excinfo.value)
    assert str(types_of_value) in str(excinfo.value)


@pytest.mark.parametrize(
    'value, expected_value', [
        ('не изменен<10', 10.0),
        ('не обнаружено в 1 г (см³)', 0),
        ('не более 11 клеток в 1 г (см³)', 11.0),
        ('не более 3,0x10⁴', 30000.0),
        ('не обнаружено в 25 г', 0),
        ('менее 1,0x10¹', 10.0),
        ('не более 10', 10.0),
        ('менее 1,0x10*', 10.0),
        ('3,2±0,4', [3.2, 3.6]),
        ('2,0-4,2', [2.0, 4.2]),
        ('2,3±0,4', [2.3, 2.6999999999999997]),
        ('-', 0),
        ('не более 5,0х10⁶', 5000000.0),
        ('3,5х10²', 350.0),
        ('не менее 1.0x10⁷', 10000000.0)
    ])
def test_to_calculate_the_value(value, expected_value):
    """ Проверка преобразования значения. """
    result_value = to_calculate_the_value(value)
    assert result_value == expected_value
