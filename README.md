# file_watcher

Сервис мониторинга папки на наличие создания нового файла с проверкой записи файла на диск

## ENV

    # Папка для мониторинга
    MONITORING_PATH=/mnt/shared_images_2
    # Тип файла
    FILE_TYPE=.svs
    # Ожидание между проверками файла
    FILE_WAIT_TIME=20
    # Количество попыток проверки файла
    FILE_ATTEMPTS=10
    # URL CALLBACK
    CALLBACK_LINK=http://filesCallback/
    # Количество попыток
    HTTP_RETRIES=5
    # Фактор задержки между попытками (увеличивается экспоненциально)
    HTTP_BACKOFF_FACTOR=2
    # Статусы ошибок, при которых будут попытки повторов
    HTTP_STATUS_FORCE_LIST=500,502,503,504

Для корректной работы необходимо что бы этот сервис и сервис который принимает callback видели одну и туже папку.