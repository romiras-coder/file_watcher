# coding=utf-8
from __future__ import unicode_literals

import os

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from logs_conf import logger
from .envs_utility import get_env_var_as_int

# URL CALLBACK
CALLBACK_LINK = os.getenv("CALLBACK_LINK", "http://192.168.101.244:8000/api/pathomorphology/filesCallback/")
# Количество попыток
HTTP_RETRIES = get_env_var_as_int("HTTP_RETRIES", 5)
# Фактор задержки между попытками (увеличивается экспоненциально)
HTTP_BACKOFF_FACTOR = get_env_var_as_int("HTTP_BACKOFF_FACTOR", 2)


def requests_session_with_retries(retries: int, backoff_factor: int, status_forcelist: list) -> Session:
    '''
    Функция для настройки сессии с попытками повторов
    :param retries: Общее количество попыток
    :param backoff_factor: Фактор задержки между попытками
    :param status_forcelist: Коды статусов, при которых следует повторить попытку
    :return: None
    '''
    # Настраиваем стратегию повторов
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    # Создаем адаптер с настроенной стратегией повторов
    adapter = HTTPAdapter(max_retries=retry_strategy)

    # Создаем сессию и добавляем адаптер к ней
    session = Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def send_callback(file_path: str, data: dict) -> None:
    '''
    Отправка callback
    :param file_path: путь к файлу
    :param data: данные для отправки
    :return:
    '''
    logger.info(f"'{file_path}' {data}")

    # Создаем сессию с повторными попытками
    session = requests_session_with_retries(HTTP_RETRIES, HTTP_BACKOFF_FACTOR, [500, 502, 503, 504])

    # Делаем запрос с сессией
    try:
        response = session.post(
            url=CALLBACK_LINK,
            json=data,
            timeout=5
        )
        response.raise_for_status()  # Проверяем наличие HTTP ошибок
        logger.info(
            f"'{file_path}' Статус код: {response.status_code} | Ответ: {response.json()}")  # Выводим текст ответа
    except requests.exceptions.RequestException as err:
        logger.error(f"Запрос не удался, ошибка: {err}")
