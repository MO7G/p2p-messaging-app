from socket import gethostname, gethostbyname, gaierror
import netifaces as ni
from metaClass.singleton import SingletonMeta
from config.logger_config import LoggerConfig
import logging

terminalLogFlag = True
logger = LoggerConfig.configure_logger("app_config", level=logging.INFO, log_path='../logs/config', enable_console=terminalLogFlag)

class AppConfig(metaclass=SingletonMeta):
    def __init__(self):
        self.port_tcp = 15600
        self.port_udp = 15500
        self.hostname = self._get_host_address()
        self.max_users = 100

    def _get_host_address(self):
        try:
            return gethostbyname(gethostname())
        except gaierror:
            return ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

    def show_current_configuration(self):
        logger.info(f"TCP Port: {self.port_tcp}")
        logger.info(f"UDP Port: {self.port_udp}")
        logger.info(f"Hostname: {self.hostname}")


AppConfig().show_current_configuration()