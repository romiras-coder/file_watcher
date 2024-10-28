import logging
from logging.handlers import TimedRotatingFileHandler

# Настройка TimedRotatingFileHandler
file_handler = TimedRotatingFileHandler(
    filename='./logs/app.log',
    when='midnight',  # Ротация в полночь
    interval=1,  # Каждые 1 день
    backupCount=7,  # Хранить 7 резервных копий
    encoding='utf-8'
)

# Создаем логгера
logger = logging.getLogger("file_checker")
logger.setLevel(logging.INFO)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Уровень для консоли

# Создаем обработчик для записи в файл
file_handler.setLevel(logging.INFO)  # Уровень для файла

# Определяем формат сообщений
formatter = logging.Formatter("[%(asctime)s]: %(levelname)s | %(funcName)s | Обработка файла: %(message)s")

# Применяем формат к обработчикам
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)
