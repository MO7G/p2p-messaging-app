import unittest
from config.app_config import AppConfig

class TestAppConfig(unittest.TestCase):
    def test_singleton_instance(self):
        # Ensure that multiple instances are the same
        instance1 = AppConfig()
        instance2 = AppConfig()
        self.assertIs(instance1, instance2)

    def test_configuration_values(self):
        # Ensure that default configuration values are set correctly
        instance = AppConfig()
        self.assertEqual(instance.port_tcp, 15600)
        self.assertEqual(instance.port_udp, 15500)
        self.assertIsInstance(instance.hostname, str)
        self.assertGreaterEqual(instance.max_users, 0)

    def test_get_host_address(self):
        # Ensure that _get_host_address returns a valid IP address
        instance = AppConfig()
        host_address = instance._get_host_address()
        self.assertIsInstance(host_address, str)
        # Assuming a valid IPv4 address for simplicity in this example
        self.assertRegex(host_address, r'^\d+\.\d+\.\d+\.\d+$')

if __name__ == '__main__':
    unittest.main()
