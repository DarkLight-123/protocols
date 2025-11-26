from datetime import datetime

import pytest

from league_sert.data_preparation.launch_data_preparation import (
    extract_and_prepare_data)
from league_sert.db_operations.db_writer import (
    _write_objects_from_file_to_db)
from league_sert.models.models import (
    MainProtocol, ManufProd, Air, Washings, StoreProd, ProdControl)
from league_sert.models.models_creator import (
    create_all_objects)
from tests.test_league_sert.test_data_preparaton.constants import (
    TEST_WORD_FILES)


@pytest.mark.db_test
def test_write_file_to_db(setup_database):
    """ Тестируется получение данных и их запись в БД
    из одного конкретного файла."""
    session = setup_database
    # Собрать данные из word файла.
    data_from_file = extract_and_prepare_data(TEST_WORD_FILES[0])
    # Создать объекты для записи в БД.
    objects_for_db = create_all_objects(data_from_file)
    # Записать объекты в БД.
    _write_objects_from_file_to_db(objects_for_db, session)

    # Получаем записанные объекты и проверяем их атрибуты, в том числе и связи на main_prot
    main_prots = session.query(MainProtocol).all()
    assert len(main_prots) == 1
    main_prot = main_prots[0]
    assert main_prot.id == 1
    assert main_prot.number == '8281/24-Д'
    assert main_prot.date == datetime.strptime('29.08.2024', '%d.%m.%Y').date()

    store_prods = session.query(StoreProd).all()
    assert len(store_prods) == 17
    store_prod = store_prods[0]

    assert store_prod.sample_code == '8281-1'  # Шифр пробы.
    assert store_prod.prod_name == 'Лепешка томаты с базиликом'  # Наименования продукции.
    assert store_prod.prod_date == '2024-08-13'  # Дата производства продукции
    assert store_prod.manuf == 'АО «ДИКСИ ЮГ»'  # Дата производства продукции
    assert store_prod.main_prot_id == 1  # Дата производства продукции

    airs = session.query(Air).all()
    assert len(airs) == 1
    air = airs[0]

    assert air.sample_code.replace(' ', '') == '8281-2'  # Шифр пробы.
    assert air.main_prot_id == 1  # Дата производства продукции
    air.name_indic = 'Плесневые грибы, КОЕ'
    air.sampling_site = 'Холодильная камера «Молочные продукты»'

    washings = session.query(Washings).all()
    assert len(washings) == 9  # Шифр пробы.
    washing = washings[0]
    assert washing.main_prot_id == 1  # Дата производства продукции
    washing.name_indic = 'БГКП'
    washing.sampling_site = 'Касса'

    prod_contorls = session.query(ProdControl).all()
    assert len(prod_contorls) == 16  # Шифр пробы.
    prod_contorl = prod_contorls[0]
    assert prod_contorl.main_prot_id == 1  # Дата производства продукции
    washing.name_indic = 'Температура воздуха'
    washing.sampling_site = """Отдел
    «Овощи/ фрукты», рабочее место работника торгового зала
    (Па)
    """


@pytest.mark.db_test
def test_write_some_files_to_db(setup_database):
    """ Тестируется получение данных и их запись в БД из 3 файлов
    с протоколами. Проверяется количество записанных объектов в БД. """

    session = setup_database

    # Записать данные из трех файлов в БД.
    for file in TEST_WORD_FILES[:3]:
        data_from_file = extract_and_prepare_data(file)
        objects_for_db = create_all_objects(data_from_file)
        _write_objects_from_file_to_db(objects_for_db, session)

    # Получаем и проверяем количество объектов записанных в БД.
    main_prots = session.query(MainProtocol).all()
    assert len(main_prots) == 3
    manuf_prods = session.query(ManufProd).all()
    assert len(manuf_prods) == 39
    airs = session.query(Air).all()
    assert len(airs) == 3
    washings = session.query(Washings).all()
    assert len(washings) == 18
    prod_controls = session.query(ProdControl).all()
    assert len(prod_controls) == 48
