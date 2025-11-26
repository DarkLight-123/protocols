""" Исключения для пакета data_preparation. """
from league_sert.exceptions import MyException


class TypeOfIndicatorTableError(MyException):
    """ Исключение, возникающее, когда не определен тип таблицы с показателями. """
    def __init__(self, message='Не определен тип таблицы показателей, '
                               'невозможно в дальнейшем сравнить и сохранить результаты.'):
        self.message = message
        super().__init__(self.message)


class NoneConformityError(MyException):
    """ Исключение, возникающее, когда в результате сравнения вывод None"""
    def __init__(self, result, norm):
        self.message = (f'В результате вычисления соответствия результата нормам произошла ошибка. '
                        f'result - {result}, norm - {norm}')
        super().__init__(self.message)


class MethodOfComparisonError(MyException):
    """Исключение, возникающее, когда не найден подходящий под тип сравнения метод сравнения. """
    def __init__(self, comparison_type):
        self.message = f'Не найден подходящий метод сравнения типа сравнения - {comparison_type}'
        super().__init__(self.message)


class DetermineValueTypeError(MyException):
    """ Исключение, возникающее, когда текст значения или сравнения не подходит под паттерны"""
    def __init__(self, value, types_of_value):
        self.message = (f'Не определен подходящий тип для значения или сравнения'
                        f'value - {value}, класс сравнения - {types_of_value}')
        super().__init__(self.message)


class TypeOfTableError(MyException):
    """Исключение, возникающее, когда по содержимому первых двух ячеек
    не представляется возможным определить тип таблицы: RESULT, MAIN, SAMPLE."""

    def __init__(self, cells):
        self.message = (f'Для таблицы, начинающейся с {cells[0].text, cells[1].text} '
                        f'не найдено подходящего типа таблицы. ')
        super().__init__(self.message)


class AddressNotFoundError(MyException):
    """Исключение, возникающее, когда не получилось
    вычленить и сформировать адрес магазина."""
    def __init__(self, text):
        self.message = f'Не найден адрес {text}'
        super().__init__(self.message)
