import logging
import os

class LoggerConfig:
    @staticmethod
    def configure_logger(name, level=logging.INFO, log_path='logs', enable_console=True):
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Create a log folder if it doesn't exist
        os.makedirs(log_path, exist_ok=True)

        # Configure a file handler
        log_filename = f'{log_path}/{name}.log'
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(level)

        # Create a formatter and attach it to the file handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

        # Optionally configure a console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger
