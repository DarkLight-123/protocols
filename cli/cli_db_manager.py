"""
CLI для взаимодействия с БД. При работе с БД необходимо ввести пароль.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent

if BASE_DIR not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils import divider
from database.base import Base
from database.db_config_postgres import protocols_engine, prot_session_maker
from database.db_manager import DBManager

load_dotenv()

# Настройки подключения
DB_PWD_CLI = os.getenv('DB_PWD_CLI')  # имя пользователя


def input_password():
    """ Запросить пароль для манипуляций с таблицами. При получении
    сравнить с паролем, который хранится в .env файле """
    divider()
    while True:
        pwd_from_user = input(
            'Для работы с таблицами введите пароль, затем нажмите <Enter>\n'
            'Для выхода из данного введите 0, затем нажмите <Enter>\n'
            '>>>'
        )
        if pwd_from_user == DB_PWD_CLI:
            print('Вход выполнен.')
            return True
        elif pwd_from_user == '0':  # Сравнение с '0', так как input возвращает строку
            return False
        else:
            print('Пароль неверен.')
            divider()


def cli_db_manager():
    """ CLI для работы с таблицами в БД."""
    choice_of_user = True
    divider()
    print('Меню для работы с таблицами в Базе данных.')
    if input_password():
        while choice_of_user:
            divider()
            choice_of_user = int(input(
                'Введите 1 и нажмите <Enter> если хотите удалить все таблицы из БД.\n'
                'Введите 2 и нажмите <Enter> если хотите создать все таблицы в БД.\n'
                'Введите 3 и нажмите <Enter> если хотите удалить определенную таблицу.\n'
                'Введите 4 и нажмите <Enter> если хотите просмотреть названия таблиц.\n'
                'Введите 0 и нажмите <Enter> если хотите выйти.\n'
                '>>>'
            ))
            db_worker = DBManager(Base, protocols_engine, prot_session_maker)
            if choice_of_user == 1:
                db_worker.drop_all_tables()
            elif choice_of_user == 2:
                db_worker.create_all_tables()
            elif choice_of_user == 3:
                table_name = input('Введите название таблицы и нажмите <Enter>\n>>>')
                db_worker.drop_the_table(table_name)
            elif choice_of_user == 4:
                tables = db_worker.get_all_tables()
                for i in tables:
                    print('--' + i)
            elif choice_of_user == 0:
                choice_of_user = False
    else:
        return False
