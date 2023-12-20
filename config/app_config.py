import time
from functools import lru_cache
from socket import gethostname, gethostbyname, gaierror
import netifaces as ni
from metaClass.singleton import SingletonMeta
from config.logger_config import LoggerConfig
import logging

terminalLogFlag = True
logger = LoggerConfig("app_config", level=logging.INFO, log_path='./logs/config', enable_console=terminalLogFlag).get_logger()

class AppConfig(metaclass=SingletonMeta):
    def __init__(self):
        self.port_tcp = 5000
        self.port_udp = 6000
        self.max_users = 100

    @property
    @lru_cache(maxsize=1)  # Cache size of 1 means it will only store the latest result
    def _hostname(self):
        try:
            host_result = gethostbyname(gethostname())
            logger.info(f'Operating System host name is {host_result}')
            return host_result
        except gaierror:
            logger.info(f'Operating System host name is {host_result}')
            return ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

    def show_current_configuration(self):
        logger.info(f"TCP Port: {self.port_tcp}")
        logger.info(f"UDP Port: {self.port_udp}")
        logger.info(f"Hostname: {self._hostname}")

