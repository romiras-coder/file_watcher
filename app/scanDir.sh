#!/bin/bash

# Мониторинг папки при появлении файла с расширением *.svs -
# происходит callback в API для последующей обработки

# URL-адрес для callback
CALLBACK_LINK="$CALLBACK_LINK"
# Формат времени
DATETIME_FORMAT="%d-%m-%YT%H:%M:%S"
# Файл логов
LOG_FILE=/var/log/fswatch/fswatch.log
# Тип события (создание, изменение или удаление)
EVENT_TYPE=$1
# Путь к файлу, вызвавшему событие
FILE=$2
# Максимальное количество попыток
max_attempts=5
# Начальное количество попыток
attempt=1
# Задержка перед следующей попыткой в секундах используется sleep
latency_attempts=5

sendCallBack() {
  # Получаем информацию о файле с помощью stat и преобразуем в JSON
  #  %A - права доступа;
  #  %b - количество занятых блоков;
  #  %F - тип файла;
  #  %g - идентификатор группы файла;
  #  %G - имя группы файла;
  #  %i - идентификатор Inode;
  #  %n - имя файла;
  #  %s - размер файла;
  #  %u - идентификатор владельца файла;
  #  %U - имя владельца файла;
  #  %x - время последнего доступа;
  #  %y - время последней модификации контента;
  #  %z - время последнего изменения контента или атрибутов.
  stat_output=$(stat --format='{"file":"%n", "size":%s, "accessDateTime":"%x", "modifyDateTime":"%y", "createDateTime":"%w", "changeDateTimeime":"%z", "permissions":"%A", "owner":"%U", "group":"%G", "fileType":"%F"}' "$FILE")
  echo "[$(date +$DATETIME_FORMAT)]: URL : $CALLBACK_LINK"
  echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Data: $stat_output"
  echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Data: $stat_output" >>$LOG_FILE
  # Выполнение запроса с ограниченным количеством попыток
  while [ $attempt -le $max_attempts ]; do
    echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Попытка $attempt из $max_attempts..."
    echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Попытка $attempt из $max_attempts..." >>$LOG_FILE

    # Выполняем команду curl
    response=$(curl --write-out "%{http_code}" --silent --output /dev/null -X 'POST' $CALLBACK_LINK -H 'accept: application/json' -H 'Content-Type: application/json' -d "$stat_output")

    # Проверяем код ответа
    if [[ "$response" -eq 200 || "$response" -eq 201 ]]; then
      echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Запрос успешен: HTTP код $response"
      echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Запрос успешен: HTTP код $response" >>$LOG_FILE
      break
    else
      echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Ошибка: HTTP код $response"
      echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Ошибка: HTTP код $response" >>$LOG_FILE
      attempt=$((attempt + 1))
      echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Ожидание перед следующей попыткой..."
      echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: Ожидание перед следующей попыткой..." >>$LOG_FILE
      sleep $latency_attempts # Задержка перед следующей попыткой
    fi
  done

  if [ $attempt -gt $max_attempts ]; then
    echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: !!! Достигнуто максимальное количество попыток. Запрос не удался !!!"
    echo "[$(date +$DATETIME_FORMAT)]: Отправка callback: !!! Достигнуто максимальное количество попыток. Запрос не удался !!!" >>$LOG_FILE
  fi
}

# Функция для вычисления MD5 контрольной суммы файла
calculateFilesBlock() {
  stat -c '%b' "$1"
}

# Устанавливаем таймер
no_change_count=0
threshold=5 # Количество циклов, в течение которых значение не меняется

if [[ "$EVENT_TYPE" == *"Created"* ]]; then

  # Получаем начальную MD5 контрольную сумму файла
  lastBlockSize=$(calculateFilesBlock "$FILE")
  echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: '$FILE'"
  echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: '$FILE'" >>$LOG_FILE
  echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: '$FILE' Начальная кол-во блоков на диске: $lastBlockSize"
  echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: '$FILE' Начальная кол-во блоков на диске: $lastBlockSize" >>$LOG_FILE

  while true; do
    # Вычисляем новую MD5 контрольную сумму
    currentBlockSize=$(calculateFilesBlock "$FILE")

    # Сравниваем текущее значение с последним
    if [[ "$currentBlockSize" == "$lastBlockSize" ]]; then
      ((no_change_count++)) # Увеличиваем счетчик, если значение не изменилось
    else
      no_change_count=0 # Сбрасываем счетчик, если значение изменилось
    fi

    # Если значение не меняется в течение заданного количества циклов
    if ((no_change_count >= threshold)); then
      echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: Кол-во блоков на диске файл '$FILE' не меняется в течение $threshold проверок: $currentBlockSize"
      echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: Кол-во блоков на диске файл '$FILE' не меняется в течение $threshold проверок: $currentBlockSize" >>$LOG_FILE

      fileSize=$(stat "$FILE" --format='%s')
      if [ $fileSize -gt 16 ]; then
        echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: Файл '$FILE' успешно записан на диск - отправлаеся callback..."
        echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: Файл '$FILE' успешно записан на диск - отправлаеся callback..." >>$LOG_FILE
        # Здесь отправляем callback
        sendCallBack
      else
        echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: Файл '$FILE' успешно записан на диск - callback НЕ БУДЕТ ОТПРАВЛЕН, размер файла $fileSize байт"
        echo "[$(date +$DATETIME_FORMAT)]: Обработка файла: Файл '$FILE' успешно записан на диск - callback НЕ БУДЕТ ОТПРАВЛЕН, размер файла $fileSize байт" >>$LOG_FILE
      fi

      break # выйти из цикла
    fi

    # Обновляем последнее значение
    lastBlockSize=$currentBlockSize

    sleep 5 # Задержка между проверками

  done

fi
