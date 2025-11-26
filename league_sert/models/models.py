"""

Модели для протоколов типа ЛИГА-СЕРТ.

Основная связующая таблица - MainProtocol: основные данные из протокола - 4 колонки.
Остальные таблицы - модели(подразделяются в зависимости от объекта исследований)
связаны внешними ключами с основными данными.

"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from database.base import Base


class MainProtocol(Base):
    """ Основная часть протокола - основные общие данные. """

    __tablename__ = 'main_prot'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)

    # Обычные поля
    number = Column(String, nullable=False, unique=True)
    date = Column(Date, nullable=True)
    store_address = Column(String, nullable=True)  # Место отбора проб.
    store_code = Column(Integer, nullable=True)
    sampling_date = Column(Date, nullable=True)  # Дата и время отбора проб.

    # Связи с другими сущностями: различными составляющими протокола
    prod_control = relationship("ProdControl", back_populates="main_prot")
    manuf_prod = relationship("ManufProd", back_populates="main_prot")
    store_prod = relationship("StoreProd", back_populates="main_prot")
    air = relationship("Air", back_populates="main_prot")
    water = relationship("Water", back_populates="main_prot")
    washings = relationship("Washings", back_populates="main_prot")


class ProdControl(Base):
    """ Протокол измерений по производственному контролю  """
    __tablename__ = 'prod_control'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    # Обычные поля
    number = Column(String)
    date = Column(Date)
    act = Column(String)  # Акт и дата проведения измерений.
    address = Column(String)  # Адрес проведения измерений.
    conclusion = Column(String)  # Заключение
    conclusion_compl = Column(Boolean)  # Установлены ли нарушения в заключении

    # Индикаторы
    name_indic = Column(String)
    result = Column(String)
    norm = Column(String)
    conformity_main = Column(Boolean)
    conformity_deviation = Column(Boolean)
    sampling_site = Column(String)
    unit = Column(String)

    # Связь с основными данными.
    main_prot_id = Column(Integer, ForeignKey('main_prot.id'))
    main_prot = relationship('MainProtocol', back_populates='prod_control')


class ManufProd(Base):
    """ Данные о пробе - продукция производителя. """
    __tablename__ = 'manuf_prod'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)

    # Обычные поля
    sample_code = Column(String)  # Шифр пробы.
    prod_name = Column(String)  # Наименования продукции.
    prod_date = Column(String)  # Дата производства продукции
    manuf = Column(String)  # Производитель.

    # Индикаторы
    name_indic = Column(String)
    result = Column(String)
    norm = Column(String)
    conformity_main = Column(Boolean)
    conformity_deviation = Column(Boolean)
    norm_doc = Column(String)

    # Связь с основными данными.
    main_prot_id = Column(Integer, ForeignKey('main_prot.id'))
    main_prot = relationship('MainProtocol', back_populates='manuf_prod')


class StoreProd(Base):
    """ Данные о пробе - производство магазина. """
    __tablename__ = 'store_prod'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)

    # Обычные поля
    sample_code = Column(String)  # Шифр пробы.
    prod_name = Column(String)  # Наименования продукции.
    prod_date = Column(String)  # Дата производства продукции
    manuf = Column(String)  # Производитель.

    # Индикаторы
    name_indic = Column(String)
    result = Column(String)
    norm = Column(String)
    conformity_main = Column(Boolean)
    conformity_deviation = Column(Boolean)
    norm_doc = Column(String)

    # Связь с основными данными.
    main_prot_id = Column(Integer, ForeignKey('main_prot.id'))
    main_prot = relationship('MainProtocol', back_populates='store_prod')


class Air(Base):
    """ Объект исследования - воздух. """
    __tablename__ = 'air'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)

    # Обычные поля
    sample_code = Column(String)  # Шифр пробы.

    # Индикаторы
    name_indic = Column(String)
    sampling_site = Column(String)
    result = Column(String)
    norm = Column(String)
    conformity_main = Column(Boolean)
    conformity_deviation = Column(Boolean)
    norm_doc = Column(String)

    # Связь с основными данными.
    main_prot_id = Column(Integer, ForeignKey('main_prot.id'))
    main_prot = relationship('MainProtocol', back_populates='air')


class Water(Base):
    """ Объект исследования - вода. """
    __tablename__ = 'water'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    test_object = Column(String)  # Объект исследований.
    sample_code = Column(String)  # Шифр пробы.

    # Индикаторы
    name_indic = Column(String)
    result = Column(String)
    norm = Column(String)
    conformity_main = Column(Boolean)
    conformity_deviation = Column(Boolean)
    norm_doc = Column(String)

    # Связь с основными данными.
    main_prot_id = Column(Integer, ForeignKey('main_prot.id'))
    main_prot = relationship('MainProtocol', back_populates='water')


class Washings(Base):
    """ Объект исследования - Смывы. """
    __tablename__ = 'washings'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)

    # Индикаторы
    name_indic = Column(String)
    sampling_site = Column(String)
    result = Column(String)
    norm = Column(String)
    conformity_main = Column(Boolean)
    conformity_deviation = Column(Boolean)
    norm_doc = Column(String)

    # Связь с основными данными.
    main_prot_id = Column(Integer, ForeignKey('main_prot.id'))
    main_prot = relationship('MainProtocol', back_populates='washings')
