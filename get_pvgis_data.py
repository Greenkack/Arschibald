import requests

base_url = "https://re.jrc.ec.europa.eu/api/seriescalc"
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
print(res.json())
