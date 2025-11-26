""" Исключения для моделей и процесса их создания."""
from league_sert.exceptions import MyException


class AttrNotFoundError(MyException):
    """ Исключение, возникает, когда отсутствует один из
    ключевых атрибутов объекта класса. """
    def __init__(self, class_type, attr_):
        self.message = (f'При создании объекта класса - {class_type.__name__}, '
                        f'отсутствуют данные для атрибута - {attr_}.')
        super().__init__(self.message)
