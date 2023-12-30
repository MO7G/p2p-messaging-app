import time
from functools import lru_cache

from socket import *
import netifaces as ni
from config.logger_config import LoggerConfig
import logging
import os
import signal


terminalLogFlag = True
logger = LoggerConfig("app_config", level=logging.INFO, log_path='./logs/config', enable_console=terminalLogFlag).get_logger()

class AppConfig():
    def __init__(self):
        self.port_tcp = 5000
        self.port_udp = 6000
        self.max_users = 100
        self.registryWaiting = 100
        self.peerSendTime = 50
        self.hostname = self._hostname_property

    @property
    @lru_cache(maxsize=1)
    def _hostname_property(self):
        try:
            host_result = gethostbyname(gethostname())
            logger.info(f'Operating System host name is {host_result}')
            return host_result
        except gaierror:
            fallback_result = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
            logger.info(f'Operating System host name is {fallback_result}')
            return fallback_result

    def show_current_configuration(self):
        logger.info(f"TCP Port: {self.port_tcp}")
        logger.info(f"UDP Port: {self.port_udp}")
        logger.info(f"Hostname: {self._hostname_property}")


    def get_random_port(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind((self.hostname, 0))
            return s.getsockname()[1]

    def kill_port(self, port):
        # Get all process IDs (PIDs) associated with the given port
        command = f"lsof -ti :{port}"
        print(f"killing port {port} ....")
        try:
            pids = [int(pid) for pid in os.popen(command).read().split()]
        except ValueError:
            print(f"No processes found on port {port}")
            return

        # Send a termination signal to each process
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(3)
                print(f"Process with PID {pid} on port {port} terminated successfully.")
            except SystemExit:
                pass  # Ignore the SystemExit exception
            except ProcessLookupError:
                print(f"Process with PID {pid} on port {port} not found.")
            except Exception as e:
                print(f"Error terminating process with PID {pid} on port {port}: {e}")


TEMP = AppConfig()

