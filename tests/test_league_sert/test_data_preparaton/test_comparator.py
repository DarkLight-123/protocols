""" Тестирование модуля comparator. """
import pytest
from comparator.comparator import Comparator


@pytest.mark.parametrize('result, norm, expecting_conclusion',
                         [
                             ('<0,01', 'не допускаются', True),
                             ('0', '', True),
                             ('0', '-', True),
                             ('20,3±0,6', '18-27', (True, True)),
                             ('0,10±0,06', '0,4, не более', (True, True)),
                             ('0,10±0,06', 'не более 0,4', (True, True)),

                             ('0,30±0,06', 'не более 0,2', (False, False)),

                             ('0,30±0,06', 'не более 0,35', (True, False)),
                             ('0,30±0,06', 'не более 0,3', (True, False)),
                             ('менее 70', '80', True),
                             ('не изменен', 'отсутствие дефектов не более 10 клеток м.о. '
                                            'в поле зрения', True),
                             ('не обнаружено в 1 г (см3)', 'не допускаются в 1 г (см3)', True),
                             ('не обнаружено в 1 г (см3)', 'не более 11 клеток в 1 г (см3)', True),
                             ('Не обнаружены', 'Отсутствие', True),
                             ('3,5х10²', 'не более 5,0х10⁶', True),
                             ('не обнаружено в 25 г', 'не допускаются в 25 г', True),
                             ('11,0±2,2', '9,0-13,0', (True, False)),
                             ('менее 70**', '80', True),
                             ('<0,01 ', 'не более 0,02', True),
                             ('<0,01 ', 'не допускаются', True),
                             ('<20', '-', False),
                             ('650,0±60,0', '300, не менее', (True, True)),
                             ('0,9±0,4', '1,0-2,0', (False, True)),
                             ('2,0±0,4', '2,0-3,5', (True, True)),
                             ('1,4±0,4', '-', (False, False)),
                             ('2.0±0.4', '1.5-3,0', (True, True)),
                             ('11,4±2,2', '8,0-13,0', (True, False)),
                             ('11,0±2.2', '9,0-13,0', (True, False)),


                         ])
def test_comparator(result, norm, expecting_conclusion):
    """ Тестирование работы функций и класса по сопоставлению результата исследований и норм. """
    comparator = Comparator(result, norm)
    comparator.compare()
    assert comparator.conclusion == expecting_conclusion
