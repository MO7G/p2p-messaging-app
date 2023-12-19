
import unittest
from socket import socket

from registry import initialize_sockets  # Replace 'your_module' with the actual module name

class TestRegistery(unittest.TestCase):
    def test_initialize_sockets(self):
        host = "127.0.0.1"
        tcp_port = 8080
        udp_port = 9090
        max_of_users = 5

        # Call the function to initialize sockets
        tcp_socket, udp_socket = initialize_sockets(host, tcp_port, udp_port, max_of_users)

        try:
            # Check if the sockets are instances of the socket class
            self.assertIsInstance(tcp_socket, socket)
            self.assertIsInstance(udp_socket, socket)

            # Check if the sockets are bound to the correct host and ports
            self.assertEqual(tcp_socket.getsockname(), (host, tcp_port))
            self.assertEqual(udp_socket.getsockname(), (host, udp_port))

            # Additional assertions if needed
        finally:
            # Close the sockets to avoid resource leaks
            tcp_socket.close()
            udp_socket.close()


if __name__ == '__main__':
    unittest.main()
