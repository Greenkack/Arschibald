import calculations
import time

start = time.time()
res1 = calculations.get_pvgis_data(50.0, 10.0, 10.0, 30, 0)
print(f"Call 1 took: {time.time() - start:.2f}s, res is None: {res1 is None}")

start = time.time()
res2 = calculations.get_pvgis_data(50.0, 10.0, 10.0, 30, 0)
print(f"Call 2 took: {time.time() - start:.2f}s, res is None: {res2 is None}")

res2["monthly_production_kwh"] = []
res3 = calculations.get_pvgis_data(50.0, 10.0, 10.0, 30, 0)
print(f"Call 3 res modified? {res3['monthly_production_kwh'] == []}")
