import calculations
import time
start = time.time()
calculations.get_pvgis_data(50.0, 10.0, 10.0, 30, 0)
calculations.get_pvgis_data(51.0, 10.0, 10.0, 30, 0) # Diff key -> rate limit should apply
end = time.time()
print(end - start)
