import random
import threading
import logging
import socket
import psutil
from config.app_config import AppConfig
from metaClass.singleton import SingletonMeta
from config.logger_config import LoggerConfig
terminalLogFlag = True
logger  = LoggerConfig("port_manager", level=logging.INFO, log_path='./logs/config',enable_console=terminalLogFlag).get_logger()
conf = AppConfig()

class PortManager(metaclass=SingletonMeta):
    def __init__(self):
        self.total_ports = conf.max_users
        self.total_rooms = conf.max_users
        self.initialPortValue = 4000
        self.available_login_ports = set()
        self.unavailable_login_ports = set()
        self.available_room_ports = set()
        self.unavailable_room_ports = set()
        self.initialize_ports()
        self.kill_ports()

    def kill_ports(self):
        logger.info(f'freeing ports from {self.initialPortValue} to {self.initialPortValue + self.total_ports + self.total_rooms}')
        for port in range(self.initialPortValue, self.total_ports + self.total_rooms + self.initialPortValue):
            self.terminate_process_using_port(port)

    def initialize_ports(self):
        self.available_login_ports = set(range(self.initialPortValue, self.total_ports + self.initialPortValue))
        self.available_room_ports = set(range(self.initialPortValue + self.total_ports, self.total_rooms + self.initialPortValue + self.total_ports))

    def take_random_login_port(self):
        if not self.available_login_ports:
            logger.warning("No available login ports.")
            return None  # Indicate that no port is available
        port = random.choice(list(self.available_login_ports))
        self.available_login_ports.remove(port)
        self.unavailable_login_ports.add(port)
        return port

    def take_random_room_port(self):
        if not self.available_room_ports:
            logger.warning("No available room ports.")
            return None  # Indicate that no port is available
        port = random.choice(list(self.available_room_ports))
        self.available_room_ports.remove(port)
        self.unavailable_room_ports.add(port)
        return port

    def release_login_port(self, port):
        if port not in self.unavailable_login_ports:
            logger.warning(f"Login port {port} was not taken.")
        else:
            self.unavailable_login_ports.remove(port)
            self.available_login_ports.add(port)

    def release_room_port(self, port):
        if port not in self.unavailable_room_ports:
            logger.warning(f"Room port {port} was not taken.")
        else:
            self.unavailable_room_ports.remove(port)
            self.available_room_ports.add(port)

    def is_port_in_use(self, port):
        # Create a socket to check if the port is in use
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Attempt to bind to the specified port
                s.bind((conf._hostname, port))
            except OSError as e:
                # If the port is in use, return True
                if e.errno == socket.errno.EADDRINUSE:
                    return True
                else:
                    # If another OSError occurs, handle it as needed
                    logger.error(f"Error binding to port {port}: {e}")
                    return False  # Indicate that an error occurred
        # If the port is not in use, return False
        return False

    def terminate_process_using_port(self, port):
        if self.is_port_in_use(port):
            try:
                # Find processes using the specified port
                for conn in psutil.net_connections(kind='inet'):
                    if conn.laddr.port == port:
                        pid = conn.pid
                        process = psutil.Process(pid)
                        process.terminate()
                        process.wait()
                        logger.info(f"Terminated process with PID {pid} using port {port}.")
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
        else:
             #logger.info(f"No process found using port {port}.")
            pass

