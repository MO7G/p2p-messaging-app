import unittest
from config.port_manager import PortManager  # Replace 'your_module' with the actual module name

class TestPortManager(unittest.TestCase):
    def setUp(self):
        self.port_manager = PortManager()

    def test_initialize_ports(self):
        self.port_manager.initialize_ports()
        # Check if the correct number of login and room ports are initialized
        self.assertEqual(len(self.port_manager.available_login_ports), self.port_manager.total_ports)
        self.assertEqual(len(self.port_manager.available_room_ports), self.port_manager.total_rooms)

    def test_take_and_release_login_port(self):
        self.port_manager.initialize_ports()
        # Take a login port
        login_port = self.port_manager.take_random_login_port()
        # Check if the port is now unavailable
        self.assertNotIn(login_port, self.port_manager.available_login_ports)
        self.assertIn(login_port, self.port_manager.unavailable_login_ports)

        # Release the login port
        self.port_manager.release_login_port(login_port)
        # Check if the port is now available again
        self.assertIn(login_port, self.port_manager.available_login_ports)
        self.assertNotIn(login_port, self.port_manager.unavailable_login_ports)

    def test_take_and_release_room_port(self):
        self.port_manager.initialize_ports()
        # Take a room port
        room_port = self.port_manager.take_random_room_port()
        # Check if the port is now unavailable
        self.assertNotIn(room_port, self.port_manager.available_room_ports)
        self.assertIn(room_port, self.port_manager.unavailable_room_ports)

        # Release the room port
        self.port_manager.release_room_port(room_port)
        # Check if the port is now available again
        self.assertIn(room_port, self.port_manager.available_room_ports)
        self.assertNotIn(room_port, self.port_manager.unavailable_room_ports)

    def test_invalid_release(self):
        # Try to release a port that was not taken
        with self.assertRaises(ValueError):
            self.port_manager.release_login_port(9999)

    def test_no_available_ports(self):
        # Take all available login ports
        self.port_manager.initialize_ports()
        for _ in range(self.port_manager.total_ports):
            self.port_manager.take_random_login_port()

        # Try to take another login port (should raise an error)
        with self.assertRaises(ValueError):
            self.port_manager.take_random_login_port()

    def tearDown(self):
        # Clean up any resources if needed
        pass

if __name__ == '__main__':
    unittest.main()
