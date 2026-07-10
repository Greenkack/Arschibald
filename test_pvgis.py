import calculations
import time
start = time.time()
res1 = calculations.get_pvgis_data(50.0, 10.0, 10.0, 30, 0)
print(f"Call 1 took: {time.time() - start:.2f}s, cached: {res1 is not None}")

start = time.time()
res2 = calculations.get_pvgis_data(50.0, 10.0, 10.0, 30, 0)
print(f"Call 2 took: {time.time() - start:.2f}s, cached: {res2 is not None}")
