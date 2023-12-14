import threading
import time
import db

class Loader:
    def __init__(self, desc="Loading...", timeout=0.1):
        self.desc = desc
        self.timeout = timeout
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        while not self.done:
            print(f"\r{self.desc}", end="", flush=True)
            time.sleep(self.timeout)
            print(" ", end="", flush=True)

    def stop(self):
        self.done = True
        self._thread.join()  # Wait for the thread to finish
        print("\r", end="", flush=True)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()



def loaderHelper(message , Func):
    with Loader(message):
        Func();

