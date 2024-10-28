# coding=utf-8
from __future__ import unicode_literals

import unittest
from unittest import mock

from utility import get_env_var_as_int


class TestGetEnvVarAsInt(unittest.TestCase):

    @mock.patch.dict("os.environ", {"TEST_VAR": "10"})
    def test_env_var_as_int(self):
        # Переменная окружения установлена и может быть преобразована в целое число
        self.assertEqual(get_env_var_as_int("TEST_VAR"), 10)

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_env_var_not_set_with_default(self):
        # Переменная окружения не установлена, но задано значение по умолчанию
        self.assertEqual(get_env_var_as_int("TEST_VAR", default_value=20), 20)

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_env_var_not_set_no_default(self):
        # Переменная окружения не установлена, значение по умолчанию отсутствует (ожидается ошибка)
        with self.assertRaises(ValueError) as context:
            get_env_var_as_int("TEST_VAR")
        self.assertIn("Переменная 'TEST_VAR' не установлена", str(context.exception))

    @mock.patch.dict("os.environ", {'TEST_VAR': 'not_an_int'})
    def test_env_var_invalid_int(self):
        # Переменная окружения установлена, но не может быть преобразована в целое число (ожидается ошибка)
        with self.assertRaises(ValueError) as context:
            get_env_var_as_int("TEST_VAR")
        self.assertIn("Переменная 'TEST_VAR' не может быть преобразована в число", str(context.exception))
