# coding=utf-8
from __future__ import unicode_literals

import argparse
import os
import threading
import time

from logs_conf import logger
from utility import file_stat_to_json, get_env_var_as_int, send_callback, check_file_extension

# Ожидание между проверками файла
FILE_WAIT_TIME = get_env_var_as_int("FILE_WAIT_TIME", 2)
# Количество попыток проверки файла
FILE_ATTEMPTS = get_env_var_as_int("FILE_ATTEMPTS", 10)
# Тип файла
FILE_TYPE = os.getenv("FILE_TYPE", ".svs")


def is_file_written_completely(file_path: str, wait_time: int, attempts: int):
    '''
    Функция для проверки записи файла
    :param file_path: путь к файлу проверки
    :param wait_time: время ожидания между проверками
    :param attempts: кол-во попыток
    :return:
    '''
    logger.info(f" '{file_path}'")
    previous_size = -1
    try:
        for attempt in range(attempts):
            logger.info(f"'{file_path}' | Попытка проверки {attempt}")
            current_size = os.stat(file_path).st_size
            logger.info(f"'{file_path}' | Начальная кол-во блоков на диске: : {current_size}")
            if current_size == previous_size:
                logger.info(
                    f"'{file_path}' | Файл записан и не меняется в течении: {wait_time} секунд | проверок: {attempt}"
                )
                if current_size > 16:
                    post_data = file_stat_to_json(file_path)
                    logger.info(f"'{file_path}' | Отправляется callback...")
                    send_callback(file_path=file_path, data=post_data)
                else:
                    logger.info(
                        f"'{file_path}' | Успешно записан на диск - callback НЕ БУДЕТ ОТПРАВЛЕН, "
                        f"размер файла {current_size} байт"
                    )
                return True  # Размер файла не изменился, значит запись завершена
            previous_size = current_size
            time.sleep(wait_time)  # Ждем перед следующей проверкой
        return False  # Файл всё еще изменяется
    except FileNotFoundError:
        logger.error(f"'{file_path}' | Файл не найден.")
    except Exception as err:
        logger.error(f"'{file_path}' | Ошибка: {err}")


# Основная часть программы
if __name__ == "__main__":
    # Настраиваем argparse для получения пути к файлу из аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Обработка файла в отдельном потоке. по событию."
                    "Обрабатывается только событие Created"
    )
    parser.add_argument("-e", dest="event", choices=["Created", "Removed"], help="Событие", required=True)
    parser.add_argument("-p", dest="file_path", type=str, help="Путь к файлу для обработки", required=True)
    args = parser.parse_args()

    if args.event == "Removed":
        logger.info(f"Файл удален '{args.file_path}'")
    else:
        if check_file_extension(args.file_path, (FILE_TYPE,)) and args.event == "Created":
            # Создаем поток для обработки файла
            file_thread = threading.Thread(
                target=is_file_written_completely,
                args=(
                    args.file_path,
                    FILE_WAIT_TIME,
                    FILE_ATTEMPTS
                )
            )
            logger.info(f"Событие: {args.event} | Путь к файлу: {args.file_path}")

            # Запускаем поток
            file_thread.start()
