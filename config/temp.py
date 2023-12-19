import socket
import timeit
import psutil

def is_port_in_use(port):
    # Create a socket to check if the port is in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Attempt to bind to the specified port
            s.bind(('127.0.1.1', port))
        except OSError as e:
            # If the port is in use, return True
            if e.errno == socket.errno.EADDRINUSE:
                return True
            else:
                # If another OSError occurs, handle it as needed
                raise
    # If the port is not in use, return False
    return False

def terminate_process_using_port(port):
    if is_port_in_use(port):
        try:
            # Find processes using the specified port
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port:
                    pid = conn.pid
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait()
                    print(f"Terminated process with PID {pid} using port {port}.")
        except Exception as e:
            print(f"Error terminating process: {e}")
    else:
        print(f"No process found using port {port}.")

# Example usage:
port_to_terminate = 5000

# Corrected timeit call with the lambda function
time_taken = timeit.timeit(lambda: terminate_process_using_port(port_to_terminate), number=1)

print(f"Execution time: {time_taken} seconds")
