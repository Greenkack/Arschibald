with open("calculations.py", "r") as f:
    content = f.read()

search = """        monthly_production_kwh = [
            m.get(
                "E_m",
                0.0) for m in data.get(
                "outputs",
                {}).get(
                "monthly",
                [])]"""

replace = """        # In PVcalc API, 'monthly' is a dict containing 'fixed', which is a list.
        monthly_data = data.get("outputs", {}).get("monthly", {})
        if isinstance(monthly_data, dict) and "fixed" in monthly_data:
            monthly_list = monthly_data["fixed"]
        else:
            monthly_list = monthly_data if isinstance(monthly_data, list) else []

        monthly_production_kwh = [
            m.get("E_m", 0.0) for m in monthly_list
        ]"""

content = content.replace(search, replace)
with open("calculations.py", "w") as f:
    f.write(content)
