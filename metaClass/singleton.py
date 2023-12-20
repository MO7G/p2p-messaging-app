import threading
from config.logger_config import LoggerConfig
import logging
terminalLogFlag = True
logger = LoggerConfig("singleton_meta", level=logging.INFO, log_path='./logs/metaClass', enable_console=terminalLogFlag).get_logger()

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            try:
                if cls not in cls._instances:
                    logger.info(f"Creating a new instance of {cls.__name__}")
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
                    logger.info(f"Instance of {cls.__name__} created successfully")
                else:
                    logger.info(f"Using an existing instance of {cls.__name__}")
            except Exception as e:
                logger.error(f"Error creating instance of {cls.__name__}: {e}")
            return cls._instances[cls]

