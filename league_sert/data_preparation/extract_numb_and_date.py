"""
Получение основных номера и даты протокола из файла word.
"""
import re

import docx
from docx2txt import docx2txt

from conversion.exceptions import NumbDateNotFoundError
from league_sert.constants import PattNumbAndDateByParts, PattNumbDate, MONTHS


def form_date(result: dict) -> str:
    """ Сформировать определенного вида строку с датой. """
    match_year = re.findall(r'\d', result['year'])
    year = "".join(match_year)
    day = result['day'].replace('«', '').replace('»', '').replace(' ', '')
    month = result['month'].replace(' ', '')
    date = day + ' ' + month + ' ' + year
    return date


def get_numb_date_from_frames(file_path: str):
    """ Получить номер и дату протокола из word файла из рамок.
     Текст из документа выбирается двумя способами, чтобы
     была больше вероятность получения нужного результата.
     Затем ищем номер и дату при помощи регулярок."""

    text = []  # Для текста из параграфов.
    result = {}  # Такие части как день, месяц, год.
    doc = docx.Document(file_path)

    # Перебираем параграфы и берем содержимое каждого из них.
    for paragraph in doc.paragraphs:
        text.append(paragraph.text.strip())

    # Соединяем в одну строку.
    from_paragraphs = '\n'.join(text)
    # Берем весь текст вторым способом.
    other_text = docx2txt.process(file_path)
    # Объединяем оба текста.
    union_text = from_paragraphs + other_text

    # Ищем в объединенном текст номер и дату протокола.
    # Сохраняем найденные элементы в словарь.

    number = re.search(PattNumbAndDateByParts.number.value, union_text)
    if not number:
        return None

    result['number'] = number.group()
    numb_slice = number.start() + 150

    for patt in [
        PattNumbAndDateByParts.month,
        PattNumbAndDateByParts.day,
        PattNumbAndDateByParts.year
    ]:

        match_ = re.search(patt.value, union_text[:numb_slice])
        if match_:
            result[patt.name] = match_.group()
        else:
            return None

    number = result['number'].replace(' ', '')
    date = form_date(result)

    return number, date


class NumbDateGetter:
    """ Класс для изъятия основных номера и даты протокола.  """
    def __init__(self, text: str, file: str):
        self.text = text
        self.file = file
        self.match_numb = None
        self.main_numb = None
        self.main_date = None

    def get_from_solid_text(self):
        """ Найти номер и дату протокола из сплошного текста."""

        # Взять первые 3000 символов документа, убрать все пробельные символы.
        substring_with_number = re.sub(r'[\t\n\s]*', '', self.text[:3000])

        # Найти номер протокола в сплошном тексте.
        self.match_numb = re.search(PattNumbDate.NUMBER.value, substring_with_number)
        if self.match_numb:
            self.main_numb = self.match_numb.group(1)

        # Найти дату в сплошном тексте.
        match_date = re.search(PattNumbDate.DATE.value, substring_with_number)
        if match_date:
            self.main_date = (match_date.group(1) +
                              ' ' + match_date.group(2) +
                              ' ' + match_date.group(3))

        # Попытка вернуть номер и дату протокола.
        if self.main_numb and self.main_date:
            return True

    def get_from_frames(self):
        """ Найти номер и дату из текста в рамках. """
        try:
            numb_from_frames, date_from_frames = get_numb_date_from_frames(self.file)
        except Exception as e:
            print(e)
            return False

        if numb_from_frames and date_from_frames:
            self.main_numb = numb_from_frames
            self.main_date = date_from_frames
            return True

    def get_date(self):
        """ Поиск даты в сплошном тексте,
        когда уже есть номер протокола. """

        if self.main_numb and not self.main_date:
            # Берем промежуток в 150 символов от номера протокола в разные стороны.
            substring = self.text[self.match_numb.start() - 150:self.match_numb.start() + 500]
            # Ищем день.
            day = re.search(r'«_*(\d{2})_*»', substring).group(1)
            # Ищем месяц.
            month = None
            for m in MONTHS.keys():
                match = re.search(m, substring)
                if match:
                    month = match.group()
                    break

            # Ищем год.
            year = re.search(r'(\d{2}\s?\d{2})\s?г.', substring).group(1)
            # Собираем дату.
            self.main_date = day + ' ' + month + ' ' + year
            if self.main_date:
                return True


def get_main_numb_and_date(text: str, file: str) -> tuple:
    """ Найти номер и дату протокола,
    реализует работу класса NumbDateGetter. """

    text = re.sub(r'«[\s_]*И[\s_]*»', "«11»", text)
    text = re.sub(r'«[\s_]*II[\s_]*»', "«11»", text)
    text = re.sub(r'«[\s_]*!![\s_]*»', "«11»", text)
    getter = NumbDateGetter(text, file)

    # Пытаемся найти номер и дату протокола одним из трех методов.
    if getter.get_from_solid_text():
        return getter.main_numb, getter.main_date
    if getter.get_from_frames():
        return getter.main_numb, getter.main_date
    if getter.get_date():
        return getter.main_numb, getter.main_date

    raise NumbDateNotFoundError(file)
