import requests

base_url = "https://re.jrc.ec.europa.eu/api/PVcalc"
params = {
    "lat": 50.0,
    "lon": 10.0,
    "peakpower": 10.0,
    "loss": 14.0,
    "pvtechchoice": "crystSi",
    "mountingplace": "building",
    "angle": 30,
    "aspect": 0,
    "outputformat": "json",
    "browser": 0,
}
res = requests.get(base_url, params=params)
data = res.json()

m = data.get("outputs", {}).get("monthly", {})
print("Type of monthly:", type(m))
if isinstance(m, dict):
    print("Keys of monthly:", m.keys())
    m = m.get("fixed", [])
    print("Type of fixed:", type(m))
