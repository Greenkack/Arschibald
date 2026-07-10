with open("calculations.py", "r") as f:
    content = f.read()

search = """        specific_yield_kwh_kwp_pa = (
            data.get("outputs", {})
            .get("totals", {})
            .get("fixed", {})
            .get("Yield_y", 0.0)
        )  # Korrigierter Key 'Yield_y'"""

replace = """        specific_yield_kwh_kwp_pa = (
            data.get("outputs", {})
            .get("totals", {})
            .get("fixed", {})
            .get("E_y", 0.0) / peak_power_kwp if peak_power_kwp > 0 else 0.0
        )  # PVcalc doesn't return Yield_y always"""

content = content.replace(search, replace)
with open("calculations.py", "w") as f:
    f.write(content)
