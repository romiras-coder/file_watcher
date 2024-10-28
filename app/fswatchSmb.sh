#!/bin/bash

# Мониторинг папки при появлении файла с расширением *.svs -
# происходит callback в API для последующей обработки

# Папка для мониторинг
DIR_TO_WATCH="$MONITORING_PATH"
# Формат времени
DATETIME_FORMAT="%Y-%m-%dT%H:%M:%S,%N"
# Файл логов
LOG_FILE=/app/logs/fswatch.log

echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: ############# Старт мониторинга папки $DIR_TO_WATCH #############"
echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: ############# Старт мониторинга папки $DIR_TO_WATCH #############" >>$LOG_FILE

# Запуск fswatch для мониторинга изменений
# %p: полный путь к измененному файлу.
# %f: событие
fswatch --monitor=poll_monitor --format "%p %f" -l 2 -r "$DIR_TO_WATCH" | while read -r NEWFILE; do

  #  echo "$NEWFILE"
  file=$(echo "$NEWFILE" | awk '{ $NF=""; print $0 }' | xargs) # Извлекаем имя файла
  event=$(echo "$NEWFILE" | awk '{ print $NF }' | xargs)       # Извлекаем событие

  # Получаем расширение файла
  EXT=".${file##*.}"

  # Выводим результат
  echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Путь: '$file'"
  echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Путь: '$file'" >>$LOG_FILE

  # Проверка типа события (создание файла)
  if [[ "$event" == *"Created"* && -f "$file" && "$EXT" == "$FILE_TYPE" ]]; then
    echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Создан файл: '$file'"
    echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Создан файл: '$file'" >>$LOG_FILE

    # Действие при создании файла
    echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Передаем на мониторинг '$file'.... "
    echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Передаем на мониторинг '$file'.... " >>$LOG_FILE
    #    /app/scanDir.sh "$event" "$file"
    python3 file_checker.py -e "$event" -p "$file" &
  fi

  # Действие при удалении файла
  if [[ ! -f "$file" && ! -e "$file" && "$event" == *"Removed"* ]]; then
    echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Директория или файл удалены: '$file'"
    echo "[$(date +$DATETIME_FORMAT | cut -b1-23)]: Событие: $event | Директория или файл удалены: '$file'" >>$LOG_FILE
    python3 file_checker.py -e "$event" -p "$file" &
  fi

done
