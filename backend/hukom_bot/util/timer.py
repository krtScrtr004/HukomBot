import time

class Timer:
    def __init__(self, label="Process"):
        self.label = label
        self.elapsed = 0.0
        self._start = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self  # Binds 'self' to the 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self._start
        # Returning False allows any internal exceptions to raise normally
        return False