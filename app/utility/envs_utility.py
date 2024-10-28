# coding=utf-8
from __future__ import unicode_literals

import os


def get_env_var_as_int(var_name: str = None, default_value=None):
    # Получаем значение переменной окружения
    value = os.getenv(var_name)

    if value is None:
        if default_value is not None:
            return default_value
        raise ValueError(f"Переменная '{var_name}' не установлена.")

    try:
        # Преобразуем значение в целое число
        return int(value)
    except ValueError:
        raise ValueError(f"Переменная '{var_name}' не может быть преобразована в число.")
