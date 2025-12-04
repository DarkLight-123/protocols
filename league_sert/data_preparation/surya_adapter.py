"""
Адаптер, который превращает результат Surya-парсинга (parsed_result.json)
в структуру, совместимую с pipeline коллеги:
process_tables → fix_keys → add_conclusions → merge_tables → db_writer.

Использование:
    from league_sert.data_preparation.surya_adapter import load_surya_data

    collector = load_surya_data("parsed/parsed_result.json")
"""

import json
from pathlib import Path

from league_sert.data_preparation.launch_data_preparation import (
    fix_the_keys_in_all_tables,
)
from league_sert.data_preparation.process_tables import process_the_tables
from league_sert.data_preparation.add_conclusions import add_conclusions_for_all_tables
from league_sert.data_preparation.merge_tables import refine_and_merge_tables


class SuryaCollector:
    """
    Класс выполняет только то, что делает MainCollector коллеги,
    но вместо чтения Word — принимает данные из parsed_result.json.
    """

    def __init__(self, surya_json_path: str | Path):
        self.surya_json_path = Path(surya_json_path)

        self.main_number = None           # Отсутствует — Surya не даёт
        self.main_date = None             # Отсутствует — Surya не даёт
        self.prod_control_data = None     # Нам не нужно

        self.data_from_tables = {}        # Главное поле для дальнейшего pipeline

    # ----------------------------------------------------------
    # 1. Превращаем список индикаторов в таблицу RESULTS
    # ----------------------------------------------------------

    def load_surya_table(self):
        """
        Читает parsed_result.json и конвертирует в структуру:
            { (0, "RESULTS"): [ ["Показатель", "Норма", "Результат"], ... ] }
        """

        data = json.loads(self.surya_json_path.read_text(encoding="utf-8"))
        indicators = data.get("indicators", [])

        # Формируем таблицу Word-подобного вида
        table = [
            ["Показатель", "Норма", "Результат"]
        ]

        for item in indicators:
            table.append([
                item.get("name", "").strip(),
                item.get("norm", "").strip() or "-",
                item.get("result", "").strip() or "-"
            ])

        # Записываем таблицу в структуру, ожидаемую pipeline коллеги
        self.data_from_tables = {
            (0, "RESULTS"): table
        }

    # ----------------------------------------------------------
    # 2. Полный запуск всех этапов коллеги на наших данных
    # ----------------------------------------------------------

    def run_full_pipeline(self):
        """
        Выполняет все этапы коллеги:
        - process_tables
        - fix_keys
        - add_conclusions
        - merge_tables

        Результат: структуры таблиц полностью готовы для записи в БД.
        """
        # 1) Обработать таблицу (убрать мусор, соединить строки и т.д.)
        self.data_from_tables = process_the_tables(self.data_from_tables)

        # 2) Исправить ключи (хотя у RESULTS их нет — просто обязательный этап)
        self.data_from_tables = fix_the_keys_in_all_tables(self.data_from_tables)

        # 3) Добавить выводы о соответствии нормам
        self.data_from_tables = add_conclusions_for_all_tables(self.data_from_tables)

        # 4) Финальный merge (типизация таблиц, подготовка формата моделей)
        self.data_from_tables = refine_and_merge_tables(self.data_from_tables)

        return self


# --------------------------------------------------------------
# Функция, которую будет удобно вызывать из других модулей
# --------------------------------------------------------------

def load_surya_data(surya_json_path: str | Path) -> SuryaCollector:
    """
    Главная функция для внешнего использования.

    Возвращает объект collector с полностью подготовленными данными:
        collector.data_from_tables
    """
    collector = SuryaCollector(surya_json_path)
    collector.load_surya_table()
    collector.run_full_pipeline()
    return collector
