"""
Модуль для преобразования переданного значения в вид,
подходящий для последующего сравнения результатов исследований и норм.

Классы:
    - ValueProcessor:
        Класс обработки значений, принимает при инициализации значение и тип значения.
        Новое значение, подготовленное для сравнения, присваивает атрибуту self.new_value.

Функции:
    - define_value_type:
        Принимает значение и класс enum, перебирает паттерны из класса enum,
        находит тип, подходящий под значение, и возвращает его имя.

    - to_calculate_the_value:
        Обработать значение и вернуть его в преобразованном виде.
        Функция-обёртка для использования класса ValueProcessor.

enum-классы:
    - ConvertValueTypes:
        Тип преобразования значения.

Пример использования:
    processed_value = to_calculate_the_value(value)
"""

import re
from typing import Any

from league_sert.constants import DIGITS_IN_DEGREE, ConvertValueTypes, ComparTypes
from league_sert.data_preparation.exceptions import DetermineValueTypeError


class ValueProcessor:
    """
    Класс-обработчик значений.
    Задача — обработать строковое значение и преобразовать его
    в вид, удобный для численного сравнения.
    """

    def __init__(self, value: str, type_of_processing: str):
        """
        :param value: исходное строковое значение (как пришло из OCR / Word).
        :param type_of_processing: имя типа (строка), одно из ConvertValueTypes.*.name
        """
        self.value: str = (value or "").strip()
        self.type_of_processing: str = type_of_processing
        self.types = ConvertValueTypes  # Набор типов для выбора подходящего.
        self.new_value: Any = 0

        self.process_the_value()

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ РАЗНЫХ ТИПОВ ЗНАЧЕНИЙ ===

    def _extract_numbers(self, pattern: str = r'(\d+[,\.]?\s?\d*)') -> list[float]:
        """
        Общий помощник: вытянуть все числа по паттерну и вернуть список float.
        Приводит строку вида '2,3' или '2 , 3' к float.
        """
        matches = re.findall(pattern, self.value)
        numbers: list[float] = []
        for m in matches:
            if isinstance(m, tuple):
                m = m[0]
            normalized = str(m).replace(' ', '').replace(',', '.')
            try:
                numbers.append(float(normalized))
            except ValueError:
                continue
        return numbers

    def process_for_plus(self) -> None:
        """
        Обработка значений вида '3,2±0,4'.
        Результат — два числа: [основное, основное + отклонение].
        """
        nums = self._extract_numbers()
        if len(nums) >= 2:
            main_digit, deviation = nums[0], nums[1]
            self.new_value = [main_digit, main_digit + deviation]
        elif len(nums) == 1:
            # На всякий случай — хоть одно число
            self.new_value = [nums[0], nums[0]]
        else:
            self.new_value = 0

    def process_multiplication(self) -> None:
        """
        Обработка значений вида '5,5х10²', '1 • 10²', '5,5x102' и т.п.
        Учитываем OCR-косяки: x/х/X, 'О' вместо '0' и прочее.
        Вычисляет значение с учетом степени.
        """
        # Разрешаем: 1.2 x 10² / 1.2x10² / 1.2*10² / и т.п.
        pattern = (
            r'(\d+[,\.]?\d*)'          # первая часть (1.2)
            r'\s*[•■*xхХX]\s*'         # знак умножения
            r'([\dOО]+)'               # "10", "1О", "1O" и т.п.
            r'([⁰¹²³⁴⁵⁶⁷⁸⁹]?)'         # возможная степень
        )
        match = re.search(pattern, self.value)
        if not match:
            # fallback — просто пытаемся вытащить число
            self.process_other()
            return

        first_digit_raw = match.group(1)
        second_digit_raw = match.group(2)
        degree_char = match.group(3)

        # Нормализуем первую часть
        first_digit = float(first_digit_raw.replace(',', '.'))

        # Нормализуем основание степени: заменяем 'O', 'О' на '0'
        second_digit_str = (
            second_digit_raw
            .replace('O', '0')
            .replace('О', '0')
        )
        try:
            second_digit = float(second_digit_str)
        except ValueError:
            # Если совсем мусор — просто берём 10
            second_digit = 10.0

        if degree_char:
            # Преобразуем надстрочную цифру в целое
            power = DIGITS_IN_DEGREE.get(degree_char, 1)
            self.new_value = first_digit * (second_digit ** power)
        else:
            self.new_value = first_digit * second_digit

    def process_within(self) -> None:
        """
        Обработка значений вида '2,0 - 4,2'.
        Результат — список из двух границ [min, max].
        """
        nums = self._extract_numbers()
        if len(nums) >= 2:
            self.new_value = [nums[0], nums[1]]
        elif len(nums) == 1:
            self.new_value = [nums[0], nums[0]]
        else:
            self.new_value = [0.0, 0.0]

    def process_other(self) -> None:
        """
        Обработка "простых" значений — одиночное число, 'не более 10', 'менее 1,0x10⁴' и т.п.
        Здесь у нас уже есть тип по ConvertValueTypes, поэтому для NOT_FOUND/NONE сюда обычно не попадаем.
        """
        nums = self._extract_numbers()
        if nums:
            self.new_value = nums[0]
        else:
            # Если цифр нет — трактуем как "0" (результат отсутствует/не определён).
            self.new_value = 0

    def process_not_found(self) -> None:
        """
        Обработка значений вида 'не обнаружено', '-', 'не допускаются' и т.п.
        Для сравнения это трактуется как 0.
        """
        self.new_value = 0

    def process_the_value(self) -> None:
        """
        Преобразовать строку в значение для выполнения сравнения.
        Выбор логики преобразования в зависимости от типа значения.
        Результат сохраняется в self.new_value.
        """
        processing_methods = {
            self.types.PLUS.name: self.process_for_plus,
            self.types.MULTIPLICATION.name: self.process_multiplication,
            self.types.NOT_FOUND.name: self.process_not_found,
            self.types.NONE.name: self.process_not_found,
            self.types.WITHIN.name: self.process_within,
            # Для значений, которые по сути означают запрет/отсутствие —
            # тоже обрабатываем как "0" (см. логику сравнения).
            getattr(self.types, "NOT_ALLOWED", None) and self.types.NOT_ALLOWED.name: self.process_not_found,
        }

        processing_method = processing_methods.get(self.type_of_processing, self.process_other)
        # Если ключ NOT_ALLOWED отсутствует в enum, в dict может оказаться None: уберём это.
        if processing_method is None:
            processing_method = self.process_other

        processing_method()


def to_calculate_the_value(value: str):
    """
    Обработать значение и вернуть его в преобразованном виде.
    Функция для использования класса ValueProcessor.

    :param value: исходное строковое значение
    :return: число / список чисел в зависимости от типа
    """
    # Определить тип необходимых преобразований значения.
    value_type = define_value_type(value, ConvertValueTypes)
    # Преобразовать значение и вернуть.
    new_value = ValueProcessor(value, value_type).new_value
    return new_value


def define_value_type(value: str, types_of_value: type[ComparTypes] | type[ConvertValueTypes]) -> str:
    """
    Определить либо тип преобразования значения, либо тип сравнения.
    Принимает значение и enum-класс с типами (ComparTypes или ConvertValueTypes),
    перебирает паттерны из enum и возвращает имя подходящего типа.

    :param value: строковое значение
    :param types_of_value: enum-класс (ComparTypes или ConvertValueTypes)
    :return: имя подходящего enum-элемента (str)
    :raises DetermineValueTypeError: если не удалось подобрать ни один тип
    """
    val = (value or "").strip().lower()

    for type_value in types_of_value:
        pattern = type_value.value
        if re.search(pattern, val):
            return type_value.name

    # Если ничего не подошло — поднимаем подробную ошибку,
    # чтобы было понятно, какое именно значение не распознано.
    raise DetermineValueTypeError(value, types_of_value)
