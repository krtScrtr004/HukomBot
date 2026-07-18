import time
from contextlib import contextmanager

@contextmanager
def timer(label="Process"):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        return end - start