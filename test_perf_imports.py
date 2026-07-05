import time
import sys

sys.path.append('.')

start_time = time.time()
from heatpump_pricing import load_heatpump_components
print(f"Import took: {time.time() - start_time:.4f} seconds")

start_time = time.time()
load_heatpump_components()
print(f"First call took: {time.time() - start_time:.4f} seconds")

start_time = time.time()
load_heatpump_components()
print(f"Second call took: {time.time() - start_time:.4f} seconds")
