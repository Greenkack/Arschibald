import calculations
errors = []
res = calculations.get_pvgis_data(50.0, 10.0, 10.0, 30, 0, errors_list=errors)
print(res)
print(errors)
