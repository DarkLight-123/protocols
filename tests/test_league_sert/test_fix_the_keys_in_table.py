import pytest

from league_sert.constants import FIX_KEYS_SAMPLE
from league_sert.data_preparation.launch_data_preparation import _fix_the_keys_in_table

sample_object_dict = {'Объект исследования': 0}
prod_group = {'Группа продукции': 0}
prod_date = {'Дата производства продукции': 0}
sample_code = {'Шифр пробы': 0}


@pytest.mark.parametrize('input_dict, expected_dict',
                         [
                             ({'()бт>ект исследования': 0}, sample_object_dict),
                             ({'Обвеют исследования': 0}, sample_object_dict),
                             ({'О&ьскт исследований': 0}, sample_object_dict),
                             ({'Обз,ект исследования': 0}, sample_object_dict),
                             ({'()бъскт 1 тсследован ия': 0}, sample_object_dict),
                             ({'Обз.ект исследований': 0}, sample_object_dict),
                             ({'Обект исследований': 0}, sample_object_dict),
                             ({'Обз.ект исследования': 0}, sample_object_dict),
                             ({'Обект исследования': 0}, sample_object_dict),
                             ({'Объект исследовании': 0}, sample_object_dict),
                             ({'объект исследований': 0}, sample_object_dict),
                             ({'Объек г исследования': 0}, sample_object_dict),
                             ({'()бъект исследования': 0}, sample_object_dict),
                             ({'()бьскт исследования': 0}, sample_object_dict),
                             ({'Обьек-i  исследования': 0}, sample_object_dict),
                             ({'Обьск-i  исследования': 0}, sample_object_dict),
                             ({'Обьест  исследования': 0}, sample_object_dict),

                             ({'[ рунпа продукции': 0}, prod_group),
                             ({'1 руппа продукции': 0}, prod_group),
                             ({'группа продукции': 0}, prod_group),
                             ({'Группа продукции': 0}, prod_group),
                             ({'Г руина продукции': 0}, prod_group),
                             ({"1 'руппа продукции": 0}, prod_group),
                             ({"'1 ’руппа продукции'": 0}, prod_group),
                             ({"1 руина пролу кции": 0}, prod_group),
                             ({'Г pvnna продукции': 0}, prod_group),

                             ({'Дата производства ироду кции': 0}, prod_date),
                             ({'Дата производства продукции': 0}, prod_date),
                             ({'Да>а производства продукции': 0}, prod_date),
                             ({'Лага производства продукции': 0}, prod_date),

                             ({'1Нифр пробы': 0}, sample_code),
                         ]
                         )
def test_fix_the_keys_in_tables(input_dict, expected_dict):
    result = _fix_the_keys_in_table(input_dict, FIX_KEYS_SAMPLE)
    assert result == expected_dict
