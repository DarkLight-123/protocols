"""
Модуль содержит SQL запрос и функцию, которая записывает данные,
полученные по запросу в XLSX файл.
"""
from sqlalchemy import text
import pandas as pd

from database.db_config_postgres import protocols_engine


QUERY_ALL = """
-- Продукция изготовителя
SELECT 
    mt.id AS id_в_бд, 
    mt.number AS номер_основного_протокола, 
    mt.date AS дата_основного_протокола, 
    mt.store_address AS Адрес_магазина, 
    mt.store_code AS Код_магазина, 
    mt.sampling_date AS дата_отбора_проб,
    'Продукция_производителя' AS Тип_исследования,
    mp.name_indic AS Наименование_показателя,
    mp.result AS Результат,
    mp.norm AS Норма,
    
    CASE 
        WHEN mp.conformity_main = TRUE THEN 'соответствует' 
        WHEN mp.conformity_main = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_основной_показатель,

    CASE 
        WHEN mp.conformity_deviation = TRUE THEN 'соответствует' 
        WHEN mp.conformity_deviation = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_показатель_с_отклонением,
    mp.norm_doc AS Нормативные_документы,
    
    NULL AS Место_отбора_пробы,    
    NULL AS Единица_измерения,    
    NULL AS номер_протокола_производственного_контроля,    
    CAST(NULL AS date) AS Дата_протокола_производственного_контроля,    
    NULL AS Акт_производственного_контроля,    
    NULL AS Адрес_отбора_проб_производственного_контроля,    
    NULL AS Текст_заключения,    
    NULL AS Наличие_нарушений_в_заключении,
    
    mp.sample_code AS Шифр_проб,
    mp.prod_name AS Наименование_товара,
    mp.prod_date AS Дата_производства,
    mp.manuf AS Изготовитель
        
FROM main_prot mt
JOIN manuf_prod mp ON mt.id = mp.main_prot_id



UNION ALL
-- Производство магазина
SELECT
    mt.id AS id_в_бд, 
    mt.number AS номер_основного_протокола, 
    mt.date AS дата_основного_протокола, 
    mt.store_address AS Адрес_магазина, 
    mt.store_code AS Код_магазина, 
    mt.sampling_date AS дата_отбора_проб,
    
    'Производство_магазина' AS Тип_исследования,
    
    sp.name_indic AS Наименование_показателя,
    sp.result AS Результат,
    sp.norm AS Норма,
    CASE 
        WHEN sp.conformity_main = TRUE THEN 'соответствует' 
        WHEN sp.conformity_main = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_основной_показатель,

    CASE 
        WHEN sp.conformity_deviation = TRUE THEN 'соответствует' 
        WHEN sp.conformity_deviation = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_показатель_с_отклонением,
    sp.norm_doc AS Нормативные_документы,
    
    NULL AS Место_отбора_пробы,    
    NULL AS Единица_измерения,    
    NULL AS номер_протокола_производственного_контроля,    
    CAST(NULL AS date) AS Дата_протокола_производственного_контроля,    
    NULL AS Акт_производственного_контроля,    
    NULL AS Адрес_отбора_проб_производственного_контроля,    
    NULL AS Текст_заключения,    
    NULL AS Наличие_нарушений_в_заключении,
    
    sp.sample_code AS Шифр_проб,
    sp.prod_name AS Наименование_товара,
    sp.prod_date AS Дата_производства,
    sp.manuf AS Изготовитель
      
FROM main_prot mt
JOIN store_prod sp ON mt.id = sp.main_prot_id

UNION ALL
-- Воздух
SELECT
    mt.id AS id_в_бд, 
    mt.number AS номер_основного_протокола, 
    mt.date AS дата_основного_протокола, 
    mt.store_address AS Адрес_магазина, 
    mt.store_code AS Код_магазина, 
    mt.sampling_date AS дата_отбора_проб,
    
    'Воздух' AS Тип_исследования,
    air.name_indic AS Наименование_показателя,
    air.result AS Результат,
    air.norm AS Норма,
    CASE 
        WHEN air.conformity_main = TRUE THEN 'соответствует' 
        WHEN air.conformity_main = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_основной_показатель,

    CASE 
        WHEN air.conformity_deviation = TRUE THEN 'соответствует' 
        WHEN air.conformity_deviation = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_показатель_с_отклонением,
    air.norm_doc AS Нормативные_документы,
    
    air.sampling_site AS Место_отбора_пробы,    
    NULL AS Единица_измерения,    
    NULL AS номер_протокола_производственного_контроля,    
    CAST(NULL AS date) AS Дата_протокола_производственного_контроля,    
    NULL AS Акт_производственного_контроля,    
    NULL AS Адрес_отбора_проб_производственного_контроля,    
    NULL AS Текст_заключения,    
    NULL AS Наличие_нарушений_в_заключении,
    
    air.sample_code AS Шифр_проб,
    NULL AS Наименование_товара,      
    NULL AS Дата_производства,       
    NULL AS Изготовитель             
      
FROM main_prot mt
JOIN air ON mt.id = air.main_prot_id

UNION ALL
-- Вода
SELECT
    mt.id AS id_в_бд, 
    mt.number AS номер_основного_протокола, 
    mt.date AS дата_основного_протокола, 
    mt.store_address AS Адрес_магазина, 
    mt.store_code AS Код_магазина, 
    mt.sampling_date AS дата_отбора_проб,
    
    'Вода' AS Тип_исследования,
    
    water.name_indic AS Наименование_показателя,
    water.result AS Результат,
    water.norm AS Норма,
    CASE 
        WHEN water.conformity_main = TRUE THEN 'соответствует' 
        WHEN water.conformity_main = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_основной_показатель,

    CASE 
        WHEN water.conformity_deviation = TRUE THEN 'соответствует' 
        WHEN water.conformity_deviation = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_показатель_с_отклонением,
    
    water.norm_doc AS Нормативные_документы,
    water.test_object AS Место_отбора_пробы,    
    NULL AS Единица_измерения,    
    NULL AS номер_протокола_производственного_контроля,    
    CAST(NULL AS date) AS Дата_протокола_производственного_контроля,    
    NULL AS Акт_производственного_контроля,    
    NULL AS Адрес_отбора_проб_производственного_контроля,    
    NULL AS Текст_заключения,    
    NULL AS Наличие_нарушений_в_заключении,  
    
    water.sample_code AS Шифр_проб,
    
    NULL AS Наименование_товара,      
    NULL AS Дата_производства,        
    NULL AS Изготовитель               

FROM main_prot mt
JOIN water ON mt.id = water.main_prot_id

UNION ALL
-- Смывы
SELECT
    mt.id AS id_в_бд, 
    mt.number AS номер_основного_протокола, 
    mt.date AS дата_основного_протокола, 
    mt.store_address AS Адрес_магазина, 
    mt.store_code AS Код_магазина, 
    mt.sampling_date AS дата_отбора_проб,
    
    'Смывы' AS Тип_исследования,

    washings.name_indic AS Наименование_показателя,
    washings.result AS Результат,
    washings.norm AS Норма,
    CASE 
        WHEN washings.conformity_main = TRUE THEN 'соответствует' 
        WHEN washings.conformity_main = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_основной_показатель,

    CASE 
        WHEN washings.conformity_deviation = TRUE THEN 'соответствует' 
        WHEN washings.conformity_deviation = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_показатель_с_отклонением,    
    washings.norm_doc AS Нормативные_документы,
    
    washings.sampling_site AS Место_отбора_пробы,    
    NULL AS Единица_измерения,    
    NULL AS номер_протокола_производственного_контроля,    
    CAST(NULL AS date) AS Дата_протокола_производственного_контроля,    
    NULL AS Акт_производственного_контроля,    
    NULL AS Адрес_отбора_проб_производственного_контроля,    
    NULL AS Текст_заключения,    
    NULL AS Наличие_нарушений_в_заключении,
    
    NULL AS Шифр_проб, 
    NULL AS Наименование_товара,      
    NULL AS Дата_производства,        
    NULL AS Изготовитель               
      
FROM main_prot mt
JOIN washings ON mt.id = washings.main_prot_id
    
UNION ALL
-- Производственный контроль
SELECT
    mt.id AS id_в_бд, 
    mt.number AS номер_основного_протокола, 
    mt.date AS дата_основного_протокола, 
    mt.store_address AS Адрес_магазина, 
    mt.store_code AS Код_магазина, 
    mt.sampling_date AS дата_отбора_проб,
    
    'Производственный контроль' AS Тип_исследования,
    prod_control.name_indic AS Наименование_показателя,
    prod_control.result AS Результат,
    prod_control.norm AS Норма,
    CASE 
        WHEN prod_control.conformity_main = TRUE THEN 'соответствует' 
        WHEN prod_control.conformity_main = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_основной_показатель,

    CASE 
        WHEN prod_control.conformity_deviation = TRUE THEN 'соответствует' 
        WHEN prod_control.conformity_deviation = FALSE THEN 'не соответствует' 
        ELSE 'неизвестно' 
    END AS Соответствие_нормам_показатель_с_отклонением,        
    
    NULL AS Нормативные_документы,
   
    prod_control.sampling_site AS Место_отбора_пробы,    
    prod_control.unit AS Единица_измерения,    
    prod_control.number AS номер_протокола_производственного_контроля,    
    prod_control.date AS Дата_протокола_производственного_контроля,    
    prod_control.act AS Акт_производственного_контроля,    
    prod_control.address AS Адрес_отбора_проб_производственного_контроля,    
    prod_control.conclusion AS Текст_заключения,   
    CASE 
        WHEN prod_control.conclusion_compl = TRUE THEN 'нарушения отсутствуют' 
        WHEN prod_control.conclusion_compl = FALSE THEN 'имеются нарушения' 
    ELSE 'неизвестно' 
    END AS Наличие_нарушений_в_заключении, 
     
    NULL AS Шифр_проб,
    NULL AS Наименование_товара,      
    NULL AS Дата_производства,        
    NULL AS Изготовитель     
        
FROM main_prot mt
JOIN prod_control ON mt.id = prod_control.main_prot_id  
ORDER BY id_в_бд ASC

"""


def write_db_data_to_xlsx(sql_query: str, output_xlsx: str) -> None:
    """ Извлечь данные по определенному sql запросу и записать
    в xlsx файл. """

    # Создание соединения и выполнение запроса
    with protocols_engine.connect() as connection:
        result = connection.execute(text(sql_query))

        # Получение всех строк результата
        rows = result.fetchall()

        df = pd.DataFrame(rows)
        df = df.sort_values(by='id_в_бд', ascending=True)
        df.to_excel(output_xlsx, index=False)


if __name__ == '__main__':
    XLSX_PATH = 'probe.xlsx'
    write_db_data_to_xlsx(QUERY_ALL, XLSX_PATH)
