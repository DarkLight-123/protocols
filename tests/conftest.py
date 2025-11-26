import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
import pytest

project_root = Path(__file__).resolve().parent.parent  # Adjust as needed
sys.path.append(str(project_root))

from league_sert.models.models import *
from league_sert.models.models_creator import create_main_protocol


PROTOCOLS_DB = 'postgresql://RIMinullin:@localhost:5432/postgres'
TEST_DB_USER = 'test_user'
TEST_DB_NAME = 'test_db'
DB_HOST = 'localhost'
DB_PORT = '5432'
# Движок для работы с БД.
ENGINE = create_engine(PROTOCOLS_DB)


def get_all_db_names():
    """ Получить наименования всех имеющихся БД. """
    with ENGINE.connect() as connection:
        # Подготовка SQL-запроса
        sql_query = text('SELECT datname FROM pg_database;')
        # Выполнение запроса
        result = connection.execute(sql_query)
        # Извлечение результатов
        databases = result.fetchall()
        # Выбрать только наименования
        return [db[0] for db in databases]


def create_test_db():
    """ Создание тестовой БД"""
    with ENGINE.connect() as connection:
        # Разрешите выполнение вне транзакции
        connection.execution_options(isolation_level="AUTOCOMMIT")
        # Создание запроса на удаление БД, если существует, обязательно через функцию text.
        create_db_command = text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME};")
        # Выполните команду создания базы данных
        connection.execute(create_db_command)
        # Создание запроса на создание БД обязательно через функцию text.
        # create_db_command = text(f"CREATE DATABASE {TEST_DB_NAME} OWNER {TEST_DB_USER};")
        create_db_command = text(f"CREATE DATABASE {TEST_DB_NAME} "
                                 f"WITH OWNER = {TEST_DB_USER} "
                                 f"ENCODING = 'UTF8' "
                                 f"LC_COLLATE = 'ru_RU.UTF-8' "
                                 f"LC_CTYPE = 'ru_RU.UTF-8' "
                                 f"TEMPLATE = template0;")

        # Выполнить команду.
        connection.execute(create_db_command)


def drop_test_db():
    """ Удаление тестовой БД"""
    try:
        with ENGINE.connect() as connection:
            # Разрешите выполнение вне транзакции
            connection.execution_options(isolation_level="AUTOCOMMIT")
            # Завершить все соединения с тестовой БД
            terminate_connections_command = text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
                AND pid <> pg_backend_pid();
            """)
            connection.execute(terminate_connections_command)
            # Удалить базу данных
            drop_db_command = text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME};")
            connection.execute(drop_db_command)

    except Exception as e:
        print(f"Ошибка при удалении БД: {e}")


def create_models(session):
    """ Создание моделей. """
    Base.metadata.create_all(bind=session.bind)
    print("Все таблицы созданы")


# Настройка сессии SQLAlchemy
def get_session():
    engine = create_engine(f'postgresql://{TEST_DB_USER}:@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}')
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


@pytest.fixture(scope='function', autouse=False)
def setup_database():
    create_test_db()
    session = get_session()
    create_models(session)
    yield session  # Передаем сессию в тесты
    session.close()
    drop_test_db()
