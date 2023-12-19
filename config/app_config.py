"""
app_config.py

This script defines a thread-safe singleton class, AppConfig, using the __new__ method to ensure a single instance
across multiple threads. The AppConfig class represents a configuration object with default settings such as
TCP and UDP ports, hostname, maximum users, and a thread name. The class uses a lock to guarantee thread safety
during instance creation.

The script also includes a thread_task function that simulates some work in a thread, creating an instance of
AppConfig for each thread. The main block demonstrates the creation of two threads, each running the thread_task
function, and waits for both threads to finish.

This implementation prevents race conditions and ensures that AppConfig instances are created in a thread-safe manner.
"""

from socket import gethostname, gethostbyname, gaierror
import netifaces as ni
import threading
import concurrent.futures
import time
from threading import Thread
from time import sleep
class AppConfig:
    _instance = None
    _lock = threading.Lock()  # Lock for thread-safe instance creation

    # the Difference between __new__ and __init__ is that __new__ is called before __init__
    # we use cls as conventional name with __new__ and self with __init__
    # __new__ creates a new instance of the class but __init__ initialize the state of object
    def __new__(cls, *args, **kwargs):
        # cls._lock is important for multiple threads access to the singleton pattern class for preventing race condition
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AppConfig, cls).__new__(cls)
                cls._instance._initialize(*args, **kwargs)
            return cls._instance

    def _initialize(self, threadName):
        self.port_tcp = 15600
        self.port_udp = 15500
        self.hostname = self._get_host_address()
        self.max_users = 100
        self.threadName = threadName

    def _get_host_address(self):
        try:
            return gethostbyname(gethostname())
        except gaierror:
            return ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

    def show_current_configuration(self):
        print(f"TCP Port: {self.port_tcp}")
        print(f"UDP Port: {self.port_udp}")
        print(f"Hostname: {self.hostname}")
        print(f"Max Users: {self.max_users}")

# Example usage in your main script or module

def thread_task(thread_name):
    # Each thread creates its own instance of AppConfig
    config = AppConfig(thread_name)

    # Simulate some work in the thread
    # sleep(1)
    print(config.threadName)

if __name__ == "__main__":
    # Create two threads
    thread1 = Thread(target=thread_task, args=("Thread 1",))

    thread2 = Thread(target=thread_task, args=("Thread 2",))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()