import threading

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            try:
                if cls not in cls._instances:
                    print(f"Creating a new instance of {cls.__name__}")
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
                    print(f"Instance of {cls.__name__} created successfully")
                else:
                    print(f"Using existing instance of {cls.__name__}")
            except Exception as e:
                print(f"Error creating instance of {cls.__name__}: {e}")
            return cls._instances[cls]