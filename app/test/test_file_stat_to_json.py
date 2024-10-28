# coding=utf-8
from __future__ import unicode_literals

import logging
import os
import platform
import stat
import tempfile
import unittest
from unittest import mock

from utility import file_stat_to_json


class TestFileStatToJson(unittest.TestCase):

    @mock.patch("os.stat")
    @mock.patch("os.getlogin")
    def test_regular_file(self, mock_getlogin, mock_stat):
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file_path = tmp_file.name

        # Настраиваем mock-объекты
        mock_stat.return_value = mock.Mock(
            st_size=1024,
            st_atime=1672531200,  # Примерный timestamp для access
            st_mtime=1672531300,  # Примерный timestamp для modify
            st_ctime=1672531400,  # Примерный timestamp для change
            st_mode=stat.S_IFREG,  # Regular file
            st_uid=1000,
            st_gid=1000
        )

        # Настройка для Windows или Unix
        if platform.system() == "Windows":
            mock_getlogin.return_value = "testuser"
            expected_owner = "testuser"
            expected_group = "N/A"
        else:
            mock_stat.return_value.pw_name = "testuser"
            mock_stat.return_value.gr_name = "testgroup"
            expected_owner = "testuser"
            expected_group = "testgroup"

        # Ожидаемый результат
        expected_result = {
            "file": tmp_file_path,
            "size": 1024,
            "accessDateTime": "2023-01-01 03:00:00",
            "modifyDateTime": "2023-01-01 03:01:40",
            "createDateTime": "-",
            "changeDateTime": "2023-01-01 03:03:20",
            "permissions": '-rw-r--r--',  # Стандартное разрешение
            "owner": expected_owner,
            "group": expected_group,
            "fileType": "Regular File"
        }

        # Вызов функции
        result = file_stat_to_json(tmp_file_path)

        # Удаление временного файла
        os.remove(tmp_file_path)

        # Проверка всех ключевых полей результата
        self.assertEqual(result["file"], expected_result["file"])
        self.assertEqual(result["size"], expected_result["size"])
        self.assertEqual(result["accessDateTime"], expected_result["accessDateTime"])
        self.assertEqual(result["modifyDateTime"], expected_result["modifyDateTime"])
        self.assertEqual(result["changeDateTime"], expected_result["changeDateTime"])
        self.assertEqual(result["permissions"], expected_result["permissions"])
        self.assertEqual(result["owner"], expected_result["owner"])
        self.assertEqual(result["group"], expected_result["group"])
        self.assertEqual(result["fileType"], expected_result["fileType"])

    def test_file_not_exist(self):
        # Проверяем обработку ошибки при отсутствии файла
        non_existent_file = "/non_existent_file"
        logger = logging.getLogger("file_checker")
        with self.assertLogs(logger) as log:
            file_stat_to_json(non_existent_file)
            self.assertIn("Ошибка", log.output[0])

    @mock.patch("os.stat")
    def test_directory(self, mock_stat):
        # Создаем временный каталог
        with tempfile.TemporaryDirectory() as tmp_dir:
            mock_stat.return_value.st_mode = stat.S_IFDIR
            result = file_stat_to_json(tmp_dir)
            self.assertEqual(result["fileType"], "Directory")
