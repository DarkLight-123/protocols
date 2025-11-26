"""
Модуль для преобразования переданного значения в вид,
подходящий для последующего сравнения результатов исследований и норм.

Классы:
    - ValueProcessor:
        Класс обработки значений, принимает при инициализации значение и тип значения.
        Новое, значение, подготовленное для сравнения присваивает атрибуту - self.new_value.

Функции:
    - define_value_type:
        Принимает значение и класс enum, перебирает паттерны из класса enum,
        находит тип, подходящий под значение и возвращает его.

    - to_process_the_value:
        Обработать значение и вернуть в преобразованном виде.
        Функция для использования класса ValueProcessor


enum классы:
    - ConvertValueTypes:
        Тип преобразования значения.

Пример использования:
    processed_value = to_process_the_value(value)

"""
import re
from typing import Any

from league_sert.constants import ComparTypes, DIGITS_IN_DEGREE, ConvertValueTypes
from league_sert.data_preparation.exceptions import DetermineValueTypeError


class ValueProcessor:
    """ Класс обработчик значений.
    Задача обработать значение и преобразовать в подходящий для сравнения вид. """

    def __init__(self, value: str, type_of_processing: str):
        """ Конструктор - принимает само значение и тип значения. """
        self.value = value  # Само значение
        self.type_of_processing = type_of_processing  # Тип значения
        self.types = ConvertValueTypes  # Набор типов для выбора подходящего.
        self.new_value: Any  # Итоговое значение
        self.process_the_value()  # Значение в результате обработки

    def process_for_plus(self):
        """ Обработать значение для показателей плюс-минус.
        Результат - два числа: основное и с отклонением. """
        pattern = r'(\d+[,\.]?\s?\d*)'
        match = re.findall(pattern, self.value)
        main_digit = float(match[0].replace(',', '.').replace(' ', ''))
        deviation = float(match[1].replace(',', '.').replace(' ', ''))
        self.new_value: list = [main_digit, main_digit + deviation]

    def process_multiplication(self):
        """ Обработать значение для показателей с двумя перемножающимися числами,
        в том числе, со степенью. Вычисляет значение с учетом степени.  """
        pattern = r'(\d+[,\.]?\d*)\s?([•■*xхХX]+\s?)([\dOО]+)([⁰¹²³⁴⁵⁶⁷⁸⁹]?)'
        match_substr = re.search(pattern, self.value)
        first_digit = match_substr.group(1).replace(',', '.')
        second_digit = match_substr.group(3).replace(',', '.')
        degree = match_substr.group(4)
        if degree:
            degree = DIGITS_IN_DEGREE[degree]
            self.new_value = float(first_digit) * (float(second_digit) ** degree)
        else:
            self.new_value = float(first_digit) * (float(second_digit))

    def process_within(self):
        """ Обработать значение для показателей с пределами: "2,0 - 4,2".
        Заменить ',' на '.' """
        pattern = r'(\d+[,\.]?\d*)'
        match = re.findall(pattern, self.value)
        if match:
            self.new_value = [float(i.replace(',', '.')) for i in match]

    def process_other(self):
        """ Обработать не указанные ранее варианты,
        в основном для значений в виде числа.  """
        pattern = r'(\d+[,\.]?\d*)'
        match = re.search(pattern, self.value)
        if match:
            self.new_value = float(match.group(0).replace(',', '.'))
        else:
            self.new_value = 0

    def process_not_found(self):
        """ Обработать значение для не найдено и '-'. """
        self.new_value = 0

    def process_the_value(self):
        """ Преобразовать строку в значение для выполнения сравнения.
        Выбор логики преобразования в зависимости от типа значения.
        Результат преобразования будет сохранен в атрибут self.new_value"""
        processing_methods = {
            self.types.PLUS.name: self.process_for_plus,
            self.types.MULTIPLICATION.name: self.process_multiplication,
            self.types.NOT_FOUND.name: self.process_not_found,
            self.types.NONE.name: self.process_not_found,
            self.types.WITHIN.name: self.process_within,
            self.types.NOT_ALLOWED.name: self.process_not_found(),
        }
        processing_method = processing_methods.get(self.type_of_processing, self.process_other)
        if processing_method:
            processing_method()


def to_calculate_the_value(value: str):
    """ Обработать значение и вернуть в преобразованном виде.
    Функция для использования класса ValueProcessor"""
    # Определить тип необходимых преобразования значения.
    value_type = define_value_type(value, ConvertValueTypes)
    # Преобразовать значение и вернуть.
    new_value = ValueProcessor(value, value_type).new_value
    return new_value


def define_value_type(value: str, types_of_value: [ComparTypes | ConvertValueTypes]) -> str:
    """ Определить либо тип преобразования значения, либо тип сравнения.
    Принимает значение и класс enum с типами,
    перебирает паттерны из класса enum, находит тип,
    подходящий под значение и возвращает его. """
    for type_value in types_of_value:
        if re.search(type_value.value, value.lower()):
            return type_value.name
    raise DetermineValueTypeError(value, types_of_value)
