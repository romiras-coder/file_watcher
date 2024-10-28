# coding=utf-8
from __future__ import unicode_literals

import os
import platform
import stat
from datetime import datetime
from pathlib import Path

from logs_conf import logger


def file_stat_to_json(file_path: str):
    '''
    :param file_path:
    :return:
    '''
    # Получаем информацию о файле с помощью os.stat
    try:
        stat_info = os.stat(file_path)
        # Проверяем тип файла
        if stat.S_ISDIR(stat_info.st_mode):
            file_type = "Directory"
        elif stat.S_ISREG(stat_info.st_mode):
            file_type = "Regular File"
        elif stat.S_ISLNK(stat_info.st_mode):
            file_type = "Symbolic Link"
        elif stat.S_ISCHR(stat_info.st_mode):
            file_type = "Character Device"
        elif stat.S_ISBLK(stat_info.st_mode):
            file_type = "Block Device"
        elif stat.S_ISFIFO(stat_info.st_mode):
            file_type = "FIFO (Named Pipe)"
        elif stat.S_ISSOCK(stat_info.st_mode):
            file_type = "Socket"
        else:
            file_type = "Unknown"

        # Получаем владельца и группу файла
        if platform.system() == "Windows":
            owner = os.getlogin()  # Имя текущего пользователя
            group = "N/A"  # Windows не поддерживает группы, заменяем на "N/A"
        else:
            import pwd
            import grp
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            group = grp.getgrgid(stat_info.st_gid).gr_name

        # Преобразуем os.stat_result в словарь
        stat_dict = {
            "file": file_path,
            "size": stat_info.st_size,
            "accessDateTime": f"{datetime.fromtimestamp(stat_info.st_atime)}",
            "modifyDateTime": f"{datetime.fromtimestamp(stat_info.st_mtime)}",
            "createDateTime": "-",
            "changeDateTime": f"{datetime.fromtimestamp(stat_info.st_ctime)}",
            "permissions": stat.filemode(stat_info.st_mode),
            "owner": owner,
            "group": group,
            "fileType": file_type
        }
        # Преобразуем словарь в JSON
        return stat_dict

    except Exception as err:
        logger.error(f"Ошибка: {err}")
        return None


def check_file_extension(file_path: str, extensions: tuple) -> bool:
    '''
    Проверка расширения файла
    :param file_path: Путь к файлу, абсолютный или относительный
    :param extensions: набор типов файлов для проверки (".svs", )
    :return:
    '''
    file_extension = Path(file_path).suffix
    return file_extension.lower() in [ext.lower() for ext in extensions]
