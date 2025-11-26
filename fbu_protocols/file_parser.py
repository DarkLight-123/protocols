"""
Изъятие данных из word файла с ФБУ протоколом.
"""
import os
import re
from enum import Enum

from docx import Document, table
import docx2txt

from comparator.comparator import create_conformity_conclusion
from league_sert.data_preparation.file_parser import get_text_with_superscripts

# Множество для хранения заголовков таблицы, для пропуска при высчитывании соответствия нормам.
KEYS_IN_INDICATORS_FOR_PASS = {'Гигиенические требования безопасности',
                               'Жирно-кислотный состав',
                               'Микробиологические нормативы безопасности (патогенные)',
                               'Микробиологические нормативы безопасности',
                               'Органолептические показатели',
                               'Физико-химические показатели',
                               }


# Ключи для поиска на первой странице протокола.
REQUIRED_KEYS_FOR_PARSING_FIRST_PAGE = (
    'Место отбора проб',
    'Дата и время отбора проб',
    'Сопроводительные документы',
    'Группа продукции',
    'Наименование продукции',
    'Дата производства продукции',
    'Производитель (фирма, предприятие, организация)',
    'Дата проведения исследований'
)


class FbuPatternsForKeys(Enum):
    """ Паттерны для изъятия данных с протоколов ФБУ."""
    number_date: str = r'(протокол испытаний\s+№)([\s\d-]*от\s\d{2}.\d{2}.\d{4})'
    accompl_doc: str = r'(\bсопроводительный\b[\w\s]+:\s*)([\w\.\s№-]+.\d{4})'
    prod_name: str = r'(Наименование образца испытаний\*\:\s*)([\s\S]*?)\s*Изготовитель'
    manufacturer: str = r'(Изготовитель[\*\:]*)([\w%\s"\.]+)(Место)'
    manuf_date: str = r'(Дата (изготовления|производства)[\*\:\s]*)(\d{2}\.\d{2}\.(\d{4}|\d{2}))'
    test_date: str = r'(Дата проведения испытаний[:\s]*)(с \d{2}.\d{2}.\d{4} по \d{2}.\d{2}.\d{4})'


def process_one_indic(cells: tuple[table._Cell]) -> dict:
    """ Обработать один индикатор, сделать вывод
    о соответствии и сохранить его в словарь."""

    sub_indicators = {}
    indicator_name = get_text_with_superscripts(cells[0]).strip()
    result = get_text_with_superscripts(cells[3]).strip()
    norm = get_text_with_superscripts(cells[2]).strip()

    pattern = r'(\d+[,\.]?\d*)\s?([•■*xх]+\s?)(\d+)([⁰¹²³⁴⁵⁶⁷⁸⁹]?)'

    match_result = re.search(pattern, result)
    match_norm = re.search(pattern, norm)
    if match_result:
        result = re.sub(r'[■*]', '•', match_result.group())
    if match_norm:
        norm = re.sub(r'[■*]', '•', match_norm.group())

    result = re.sub(r'[■*]', '•', result)
    norm = re.sub(r'[■*]', '•', norm)

    # Проверка, что значение и нормы неидентичные.
    if not result == norm:
        sub_indicators[indicator_name] = {'result': result, 'norm': norm}
        # Проверка на результат и значения, которые нельзя сравнить между собой.
        if indicator_name in {'Консистенция и внешний вид',
                              'Цвет',
                              'Вкус и запах',
                              'Внешний вид',
                              'Консистенция',
                              'Цвет',
                              'Вкус',
                              'Запах',
                              'Структура',
                              'Поверхность',
                              'Внешний вид и консистенция',
                              'Упитанность',
                              'Состояние кожи',

                              }:
            if result.replace(' ', '') == norm.replace(' ', ''):
                sub_indicators[indicator_name]['conformity_main'] = True
                sub_indicators[indicator_name]['conformity_deviation'] = True
            else:
                sub_indicators[indicator_name]['conformity_main'] = False
                sub_indicators[indicator_name]['conformity_deviation'] = True

        # Для обычных показателей.
        else:
            conformity = create_conformity_conclusion(result, norm)
            if isinstance(conformity, tuple):
                sub_indicators[indicator_name]['conformity_main'] = conformity[0]
                sub_indicators[indicator_name]['conformity_deviation'] = conformity[1]
            else:
                sub_indicators[indicator_name]['conformity_main'] = conformity
                sub_indicators[indicator_name]['conformity_deviation'] = True
    return sub_indicators


class WordFileParser:
    """ Класс для изъятия данных из Word файла. """
    def __init__(self, input_word_file: str):
        self.word_file = input_word_file
        self.all_text_from_file = self.get_one_string()
        self.document_with_tables = self.convert_file_to_document()
        self.data = {}
        self.indicators = {}

    def get_one_string(self) -> str:
        """Прочитать word файл, вернуть одну большую строку постранично."""
        document = Document(self.word_file)
        pages = []
        for para in document.paragraphs:
            text = para.text.strip()
            if text:
                pages.append(text)
        return "\n".join(pages)

    def convert_file_to_document(self) -> Document:
        """ Прочитать word файл, преобразовать для работы с таблицами в
        объект класса Document. """
        document = Document(self.word_file)
        return document

    def get_data_by_keys(self) -> None:
        """ Собрать данные из word файла и сохранить ко ключам в self.data. """
        for key in FbuPatternsForKeys:
            match = re.search(key.value, self.all_text_from_file, flags=re.IGNORECASE)
            if key == FbuPatternsForKeys.manuf_date:
                self.data[key.name] = match.group(3).strip() if match else ''
            else:
                self.data[key.name] = match.group(2).strip() if match else ''

    def get_indicators(self) -> None:
      """ Пройтись по таблицам с результатами исследований и собрать
      # данные по ним и сохранить в поле 'indicators'.
      # Результат будет сохранен в виде словаря, где ключ - наименование
      # показателя, значение - tuple из нормы и результата исследования. """
      # # Цикл по таблицам документа.
      # for table_ in self.document_with_tables.tables:
      #     # Проверка на наличие в таблице более двух строк и колонок.
      #     if len(table_.rows) > 1 and len(table_.columns) > 2:
      #         # Цикл по строкам в таблице, начиная со второй.
      #         for _, row in enumerate(table_.rows[1:], start=1):
      #             # Поучаем и распаковываем словарь из одного показателя.
      #             sub_indicators = process_one_indic(row.cells)
      #             self.indicators = {**self.indicators, **sub_indicators}
      return

    def get_all_required_data_from_word_file(self):
        """ Основной метод - направленный на изъятие данных из Word файла."""
        self.get_data_by_keys()  # Получить основные данные по протоколу
        self.get_indicators()  # Добавить в словарь показатели.




if __name__ == '__main__':

    wp=WordFileParser(r'C:\Users\RIMinullin\PycharmProjects\protocols\fbu_protocols\выходной_файл.docx')
    wp.get_data_by_keys()
    wp.get_indicators()
    # print(wp.data)
    wp.get_all_required_data_from_word_file()
    print(wp.data.keys())
    print(wp.indicators)
