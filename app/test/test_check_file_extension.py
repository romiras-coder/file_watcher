# coding=utf-8
from __future__ import unicode_literals

import unittest

from utility import check_file_extension


class TestCheckFileExtension(unittest.TestCase):

    def test_valid_extension(self):
        # Проверка на корректное расширение
        self.assertTrue(check_file_extension("file.txt", (".txt", ".doc")))
        self.assertTrue(check_file_extension("/asd/file.txt", (".txt", ".doc")))
        self.assertTrue(check_file_extension("/asd/file.txt", (".txt",)))
        self.assertFalse(check_file_extension("/asd/file.txtt", (".txt", ".doc")))
        self.assertFalse(check_file_extension("/asd/file.txtt", (".txt",)))

    def test_invalid_extension(self):
        # Проверка на некорректное расширение
        self.assertFalse(check_file_extension("file.pdf", (".txt", ".doc")))

    def test_extension_case_insensitive(self):
        # Проверка на регистронезависимость
        self.assertTrue(check_file_extension("file.TXT", (".txt", ".doc")))
        self.assertTrue(check_file_extension("/mnt/shared_images_2/1138679 — копия.SVS", (".svs",)))

    def test_no_extension(self):
        # Проверка на файл без расширения
        self.assertFalse(check_file_extension("file", (".txt", ".doc")))

    def test_multiple_extensions(self):
        # Проверка на несколько корректных расширений
        self.assertTrue(check_file_extension("image.jpeg", (".png", ".jpg", ".jpeg")))
        self.assertFalse(check_file_extension("image.bmp", (".png", ".jpg", ".jpeg")))
