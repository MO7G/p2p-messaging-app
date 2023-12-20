import logging
import os
import colorlog


class LoggerConfig:
    def __init__(self, name, level=logging.INFO, log_path='logs', enable_console=True):
        self.name = name
        self.level = level
        self.log_path = log_path
        self.enable_console = enable_console

        # Create a logger instance
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create a log folder if it doesn't exist
        os.makedirs(log_path, exist_ok=True)

        # Configure a file handler
        log_filename = f'{log_path}/{name}.log'
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(level)

        # Create a formatter for the file handler (without colors)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

        # Optionally configure a console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Create a colored formatter for the console handler
            console_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s')
            console_handler.setFormatter(console_formatter)

            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
