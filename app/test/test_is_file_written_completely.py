# coding=utf-8
from __future__ import unicode_literals

import logging
import unittest
from unittest import mock

from file_checker import is_file_written_completely


class TestIsFileWrittenCompletely(unittest.TestCase):

    @mock.patch('os.stat')
    @mock.patch('utility.send_callback')  # Подменяем send_callback
    @mock.patch('utility.file_stat_to_json')  # Подменяем file_stat_to_json
    def test_file_written_completely(self, mock_file_stat_to_json, mock_send_callback, mock_stat):
        # Подготавливаем mock для stat
        mock_stat.return_value.st_size = 1024  # Начальный размер файла

        result = is_file_written_completely('test_file.txt', wait_time=1, attempts=3)

        # Проверяем, что функция вернула True
        self.assertTrue(result)

        # Проверяем, что callback был отправлен
        mock_send_callback.assert_called_once()

        # Проверяем, что file_stat_to_json был вызван
        mock_file_stat_to_json.assert_called_once_with('test_file.txt')

    @mock.patch('os.stat')
    def test_file_still_writing(self, mock_stat):
        # Подготавливаем mock для stat
        mock_stat.side_effect = [512, 1024]  # Изменяем размер файла

        result = is_file_written_completely('test_file.txt', wait_time=1, attempts=3)

        # Проверяем, что функция вернула False
        self.assertFalse(result)

    @mock.patch('os.stat')
    def test_file_not_found(self, mock_stat):
        # Настраиваем mock, чтобы выбросить FileNotFoundError
        mock_stat.side_effect = FileNotFoundError

        logger = logging.getLogger("file_checker")
        with self.assertLogs(logger) as log:
            result = is_file_written_completely('non_existent_file.txt', wait_time=1, attempts=3)
        # Проверяем, что функция вернула None
        self.assertIsNone(result)
        # Проверяем, что сообщение об ошибке записано в логах
        self.assertIn("Файл не найден.", log.output[-1])

    @mock.patch('os.stat')
    def test_other_exception(self, mock_stat):
        # Настраиваем mock, чтобы выбросить другую ошибку
        mock_stat.side_effect = PermissionError
        logger = logging.getLogger("file_checker")
        with self.assertLogs(logger) as log:
            result = is_file_written_completely('test_file.txt', wait_time=1, attempts=3)
        # Проверяем, что функция вернула None
        self.assertIsNone(result)
        # Проверяем, что сообщение об ошибке записано в логах
        self.assertIn("Ошибка:", log.output[-1])
