# app_config.py

from socket import gethostname, gethostbyname, gaierror
import netifaces as ni

class AppConfig:
    def __init__(self):
        # Default settings
        self.port_tcp = 15600
        self.port_udp = 15500
        self.hostname = self._get_host_address()
        self.max_users = 100  # Default value, you can change it

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
if __name__ == "__main__":
    config = AppConfig()
    config.show_current_configuration()
