import time
from contextlib import contextmanager

@contextmanager
def timer(label="Process"):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"[{label}] Elapsed time: {end - start:.6f} seconds")