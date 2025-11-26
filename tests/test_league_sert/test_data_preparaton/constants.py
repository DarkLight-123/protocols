import os

from tests.test_league_sert.test_data_preparaton.data_for_test.test_data_main_collectors import (
    expected_collector_1, expected_collector_2, expected_collector_3)

TEST_FILES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'test_files')

TEST_WORD_FILES = [
    os.path.join(TEST_FILES_DIR, 'test_word_file_1.docx'),
    os.path.join(TEST_FILES_DIR, 'test_word_file_2.docx'),
    os.path.join(TEST_FILES_DIR, 'test_word_file_3.docx'),
    os.path.join(TEST_FILES_DIR, 'table_1.docx'),
]

COLLECTORS = [
    expected_collector_1,
    expected_collector_2,
    expected_collector_3
]
