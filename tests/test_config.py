from config.app_config import AppConfig
import unittest
from threading import Thread
from time import sleep
from config.app_config import AppConfig

class TestAppConfig(unittest.TestCase):
    def setUp(self):
        # Reset the singleton instance before each test
        AppConfig._instance = None

    def test_singleton_instance(self):
        # Ensure that only one instance is created
        instance1 = AppConfig("Thread 1")
        instance2 = AppConfig("Thread 2")

        self.assertIs(instance1, instance2)

    def test_configuration_values(self):
        # Ensure that the configuration values are set correctly
        instance = AppConfig("Thread 1")

        self.assertEqual(instance.port_tcp, 15600)
        self.assertEqual(instance.port_udp, 15500)
        self.assertIsInstance(instance.hostname, str)
        self.assertEqual(instance.max_users, 100)
        self.assertEqual(instance.threadName, "Thread 1")

    def test_thread_safety(self):
        # Create a list to store the results from the threads
        results = []

        # Create two threads that simultaneously access AppConfig
        def thread_task(inputThreadName):
            instance = AppConfig(inputThreadName)
            results.append(instance.threadName)

        # Create threads and start them
        thread1 = Thread(target=thread_task,args=("Thread-1",))
        thread2 = Thread(target=thread_task,args=("Thread-2",))

        thread1.start()
        thread2.start()

        # Wait for both threads to finish
        thread1.join()
        thread2.join()

        # Retrieve the thread names from the results list
        thread1_name, thread2_name = results

        # Assert that the thread names are equal
        self.assertEqual(thread1_name, thread2_name, "Thread names should be equal")


if __name__ == "__main__":
    unittest.main()
