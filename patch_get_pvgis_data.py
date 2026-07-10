import re

with open('calculations.py', 'r') as f:
    content = f.read()

# First add global variables before get_pvgis_data
globals_str = """
_pvgis_cache = {}
_last_pvgis_call = 0.0
_MIN_PVGIS_INTERVAL = 1.0

def get_pvgis_data(
"""

content = content.replace('def get_pvgis_data(\n', globals_str)

# Now inject cache lookup and rate limiting at the start of get_pvgis_data
search_str = """    effective_errors_list = errors_list if errors_list is not None else local_errors"""
replace_str = """    effective_errors_list = errors_list if errors_list is not None else local_errors

    global _last_pvgis_call

    # Cache lookup
    cache_key = (latitude, longitude, peak_power_kwp, tilt, azimuth, system_loss_percent)
    if cache_key in _pvgis_cache:
        # Cache Hit - keine Wartezeit nötig
        return _pvgis_cache[cache_key]

    # Rate-Limit anwenden
    elapsed = time.time() - _last_pvgis_call
    if elapsed < _MIN_PVGIS_INTERVAL:
        time.sleep(_MIN_PVGIS_INTERVAL - elapsed)

    _last_pvgis_call = time.time()"""

content = content.replace(search_str, replace_str)

# Now cache the result before returning
search_return = """        return {
            "monthly_production_kwh": monthly_production_kwh,
            "annual_production_kwh": annual_production_kwh,
            "specific_yield_kwh_kwp_pa": specific_yield_kwh_kwp_pa,
            "pvgis_source": data.get("meta", {}).get(
                "source", "PVGIS-TMY"
            ),  # Quelle der Daten (z.B. TMY, ERA5)
        }"""

replace_return = """        result = {
            "monthly_production_kwh": monthly_production_kwh,
            "annual_production_kwh": annual_production_kwh,
            "specific_yield_kwh_kwp_pa": specific_yield_kwh_kwp_pa,
            "pvgis_source": data.get("meta", {}).get(
                "source", "PVGIS-TMY"
            ),  # Quelle der Daten (z.B. TMY, ERA5)
        }
        # Im Cache speichern
        _pvgis_cache[cache_key] = result
        return result"""

content = content.replace(search_return, replace_return)

with open('calculations.py', 'w') as f:
    f.write(content)

print("Patched calculations.py")
