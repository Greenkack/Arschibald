"""
Wärmepumpen-Produktdatenbank mit realen Modellen von Viessmann, Buderus und Vaillant
Stand: 2025
"""
__all__ = [
    'HEATPUMP_PRODUCTS',
    'find_suitable_model',
    'get_all_manufacturers',
    'get_available_types_for_manufacturer',
    'get_heatpump_models',
    'get_model_details',
]


HEATPUMP_PRODUCTS = {
    "Viessmann": {
        "Luft-Wasser-Wärmepumpe": [
            {
                "model": "Vitocal 250-A",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    10.0,
                    12.0,
                    15.0
                ],
                "scop": 4.6,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [
                    "Smart Grid Ready",
                    "Active Cooling",
                    "Internet Gateway"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.8,
                "awards": [
                    "Testsieger Stiftung Warentest 2024",
                    "Öko-Test SEHR GUT"
                ]
            },
            {
                "model": "Vitocal 200-A",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    10.0,
                    12.0
                ],
                "scop": 4.5,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [
                    "Smart Grid Ready",
                    "Active Cooling"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.5,
                "awards": [
                    "Preis-Leistung Testsieger"
                ]
            },
            {
                "model": "Vitocal 222-A",
                "heating_power_kw": [
                    8.0,
                    11.0,
                    13.0,
                    16.0
                ],
                "scop": 4.4,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [
                    "Kompakt-Bauweise",
                    "Active Cooling"
                ],
                "refrigerant": "R32",
                "rating": 4.3,
                "awards": []
            },
            {
                "model": "Vitocal 150-A",
                "heating_power_kw": [
                    4.0,
                    6.0,
                    8.0
                ],
                "scop": 4.3,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [
                    "Einfache Bedienung",
                    "Platzsparend"
                ],
                "refrigerant": "R32",
                "rating": 4.0,
                "awards": []
            },
            {
                "model": "7814924",
                "heating_power_kw": [
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01344",
                "heating_power_kw": [
                    12.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01343",
                "heating_power_kw": [
                    12.0,
                    12.6,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01353",
                "heating_power_kw": [
                    12.0,
                    12.4,
                    43.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02928",
                "heating_power_kw": [
                    7.5,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7423120",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02933",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7176014",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7426463",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02938",
                "heating_power_kw": [
                    7.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02959",
                "heating_power_kw": [
                    6.3,
                    7.5,
                    12.0,
                    13.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02960",
                "heating_power_kw": [
                    7.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02939",
                "heating_power_kw": [
                    6.3,
                    7.5,
                    12.0,
                    13.7,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK03024",
                "heating_power_kw": [
                    1.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK03026",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK03027",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "9562053",
                "heating_power_kw": [
                    1.8,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7439114",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7373455",
                "heating_power_kw": [
                    12.0,
                    12.4
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501768",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501769",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01907",
                "heating_power_kw": [
                    1.8,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501781",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "9562054",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987378",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987371",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987376",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987375",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z024663",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7441145",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "9532663",
                "heating_power_kw": [
                    12.0,
                    17.0,
                    29.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02958",
                "heating_power_kw": [
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7175213",
                "heating_power_kw": [
                    1.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01813",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z012684",
                "heating_power_kw": [
                    6.0,
                    12.0,
                    12.4,
                    19.0,
                    29.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02932",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK08004",
                "heating_power_kw": [
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK08005",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK08006",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK08003",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7527615",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7441998",
                "heating_power_kw": [
                    7.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3203016",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7452646",
                "heating_power_kw": [
                    12.0,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501783",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02536",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02537",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02533",
                "heating_power_kw": [
                    1.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02534",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7265008",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z004247",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7182008",
                "heating_power_kw": [
                    12.0,
                    20.2
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7179164",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501773",
                "heating_power_kw": [
                    1.8,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7814681",
                "heating_power_kw": [
                    12.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A06-Z029578",
                "heating_power_kw": [
                    4.8,
                    5.6,
                    10.1,
                    11.0,
                    12.0,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A06-Z029579",
                "heating_power_kw": [
                    4.8,
                    5.6,
                    11.0,
                    12.0,
                    17.5,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A06-Z029580",
                "heating_power_kw": [
                    4.8,
                    5.6,
                    11.0,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A06-Z029581",
                "heating_power_kw": [
                    4.8,
                    5.6,
                    11.0,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A08-Z029582",
                "heating_power_kw": [
                    5.6,
                    6.5,
                    10.1,
                    11.0,
                    12.0,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A08-Z029583",
                "heating_power_kw": [
                    5.6,
                    6.5,
                    11.0,
                    12.0,
                    17.5,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A08-Z029584",
                "heating_power_kw": [
                    5.6,
                    6.5,
                    11.0,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A08-Z029585",
                "heating_power_kw": [
                    5.6,
                    6.5,
                    11.0,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A10-Z029586",
                "heating_power_kw": [
                    7.3,
                    9.7,
                    10.1,
                    11.0,
                    12.0,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A10-Z029587",
                "heating_power_kw": [
                    7.3,
                    9.7,
                    11.0,
                    12.0,
                    17.5,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A10-Z029588",
                "heating_power_kw": [
                    7.3,
                    9.7,
                    11.0,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A10-Z029589",
                "heating_power_kw": [
                    7.3,
                    9.7,
                    11.0,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A13-Z029590",
                "heating_power_kw": [
                    8.1,
                    10.1,
                    11.0,
                    11.1,
                    12.0,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A13-Z029591",
                "heating_power_kw": [
                    8.1,
                    11.0,
                    11.1,
                    12.0,
                    17.5,
                    19.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A13-Z029592",
                "heating_power_kw": [
                    8.1,
                    11.0,
                    11.1,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-A13-Z029593",
                "heating_power_kw": [
                    8.1,
                    11.0,
                    11.1,
                    12.0,
                    19.0,
                    23.0,
                    25.0,
                    32.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987055",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK08001",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7983952",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249277",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249288",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249287",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7441121",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02945",
                "heating_power_kw": [
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02943",
                "heating_power_kw": [
                    12.0,
                    13.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7143928",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7417925",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7143779",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02575",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01400",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987373",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987370",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02929",
                "heating_power_kw": [
                    7.5,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02930",
                "heating_power_kw": [
                    6.3,
                    12.0,
                    12.6,
                    14.7,
                    24.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987377",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK03206",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249273",
                "heating_power_kw": [
                    12.0,
                    12.6,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249272",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7441106",
                "heating_power_kw": [
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249274",
                "heating_power_kw": [
                    12.0,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7450657",
                "heating_power_kw": [
                    12.0,
                    13.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3210482",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3210504",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3210506",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3210484",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3210507",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3210485",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK08163",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-BWC-Z029971",
                "heating_power_kw": [
                    12.0,
                    17.4
                ],
                "scop": 5.2,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017632",
                "heating_power_kw": [
                    0.7,
                    0.9,
                    1.0,
                    1.3,
                    2.6,
                    3.8,
                    4.0,
                    4.2,
                    6.0,
                    7.0,
                    8.0,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017633",
                "heating_power_kw": [
                    0.8,
                    1.0,
                    1.2,
                    2.0,
                    3.1,
                    4.8,
                    5.0,
                    5.5,
                    6.0,
                    6.3,
                    7.0,
                    8.0,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017634",
                "heating_power_kw": [
                    1.0,
                    1.2,
                    1.5,
                    2.3,
                    4.0,
                    5.6,
                    6.0,
                    6.7,
                    7.0,
                    7.5,
                    8.0,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030278",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030274",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030282",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030279",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030275",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030283",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030280",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030276",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030284",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030281",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030277",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-E-AC-Z030285",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030266",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030270",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030267",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030263",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030271",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030268",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030264",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030272",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030269",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030265",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-252-A-AWOT-M-E-AC-Z030273",
                "heating_power_kw": [
                    12.0,
                    13.4
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK07448",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7506157",
                "heating_power_kw": [
                    12.0,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02660",
                "heating_power_kw": [
                    1.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249281",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7438537",
                "heating_power_kw": [
                    12.0,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7373030",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501765",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501766",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7246581",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK03036",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK03037",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7983955",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7441146",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02645",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02646",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7334502",
                "heating_power_kw": [
                    12.0,
                    19.3
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7180662",
                "heating_power_kw": [
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7172825",
                "heating_power_kw": [
                    1.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7506168",
                "heating_power_kw": [
                    6.3,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7248242",
                "heating_power_kw": [
                    10.4,
                    12.0,
                    15.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7248243",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7186663",
                "heating_power_kw": [
                    7.61,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02447",
                "heating_power_kw": [
                    10.4,
                    12.0,
                    29.0,
                    43.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01285",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01286",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01287",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01288",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01289",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01290",
                "heating_power_kw": [
                    10.4,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249305",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7249275",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02931",
                "heating_power_kw": [
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK03023",
                "heating_power_kw": [
                    1.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK02257",
                "heating_power_kw": [
                    1.5,
                    12.0,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7820403",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7820404",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01909",
                "heating_power_kw": [
                    1.8,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501787",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7987374",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501771",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7501772",
                "heating_power_kw": [
                    1.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01890",
                "heating_power_kw": [
                    1.8,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01891",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "9521437",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7373025",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK01415",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-T0E-R290-Z028427",
                "heating_power_kw": [
                    1.2,
                    1.25,
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-T0E-R290-Z028429",
                "heating_power_kw": [
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-T0E-R290-Z028426",
                "heating_power_kw": [
                    1.5,
                    1.58,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-T0E-R290-Z028428",
                "heating_power_kw": [
                    1.5,
                    1.54,
                    2.6,
                    12.0,
                    19.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-T0S-R290-Z028431",
                "heating_power_kw": [
                    1.5,
                    2.6,
                    3.0,
                    12.0,
                    19.0,
                    24.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-T0S-R290-Z028430",
                "heating_power_kw": [
                    1.5,
                    1.54,
                    2.6,
                    12.0,
                    19.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-Z021986",
                "heating_power_kw": [
                    1.5,
                    2.6,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-060-A-Z021987",
                "heating_power_kw": [
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032123",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032195",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032124",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032196",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032125",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032197",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032198",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032126",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032129",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032201",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032130",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032202",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032203",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032131",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032243",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032171",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032244",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032172",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032245",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032173",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032246",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032174",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032249",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032177",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032250",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032178",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032251",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-150-A-Compact-Z032179",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032285",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032267",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032286",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032268",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032287",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032269",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032288",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032270",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032291",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032273",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032292",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032274",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032293",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032275",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033060",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033061",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033062",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033063",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033044",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    11.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033045",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033046",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033047",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033076",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033088",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033077",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033089",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033078",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033090",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033064",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033065",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033066",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033067",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033048",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    11.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033049",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033050",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033051",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033079",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033091",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033080",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033092",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033081",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033093",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033068",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033069",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033070",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033071",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033052",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    11.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033053",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033054",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033055",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033072",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033073",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033074",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033075",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033082",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033094",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033083",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033095",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033084",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033096",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033056",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.0,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033057",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033058",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033059",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033085",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033097",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033086",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033098",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033087",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033099",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032219",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032147",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032220",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032148",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032221",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032149",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032222",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032150",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032225",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032153",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032226",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032154",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032227",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z032155",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033020",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033016",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033024",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033021",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033017",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033025",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033022",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033018",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033026",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033023",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033019",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033027",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033031",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033028",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033034",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033032",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033029",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033035",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033033",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033030",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033036",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z026675",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.3,
                    3.0,
                    3.9,
                    5.0,
                    6.0,
                    7.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    14.7,
                    85.0,
                    101.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z011360",
                "heating_power_kw": [
                    1.97,
                    2.48,
                    2.75,
                    3.89,
                    5.63,
                    6.1,
                    6.7,
                    7.0,
                    8.8,
                    9.7,
                    10.12,
                    10.67,
                    11.38,
                    12.0,
                    12.4,
                    15.03,
                    191.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015198",
                "heating_power_kw": [
                    1.5,
                    1.7,
                    3.0,
                    3.2,
                    5.0,
                    6.0,
                    6.1,
                    7.0,
                    7.6,
                    9.0,
                    10.1,
                    12.0,
                    12.6,
                    13.6,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015195",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    7.0,
                    8.7,
                    9.0,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015199",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.0,
                    3.0,
                    3.6,
                    5.0,
                    6.0,
                    6.7,
                    7.0,
                    8.2,
                    8.9,
                    9.0,
                    11.1,
                    12.0,
                    13.7,
                    14.2,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015200",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.3,
                    3.0,
                    3.9,
                    5.0,
                    6.0,
                    7.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    14.7,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015192",
                "heating_power_kw": [
                    0.7,
                    0.8,
                    0.9,
                    1.3,
                    2.6,
                    3.0,
                    3.8,
                    4.0,
                    4.2,
                    5.0,
                    6.0,
                    7.0,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z026670",
                "heating_power_kw": [
                    0.8,
                    1.0,
                    1.2,
                    2.0,
                    3.0,
                    3.1,
                    4.8,
                    5.0,
                    5.7,
                    6.0,
                    6.3,
                    9.0,
                    12.0,
                    48.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z026713",
                "heating_power_kw": [
                    0.7,
                    0.8,
                    0.9,
                    1.3,
                    2.6,
                    3.0,
                    3.8,
                    4.0,
                    4.2,
                    5.0,
                    6.0,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z026671",
                "heating_power_kw": [
                    1.0,
                    1.2,
                    1.4,
                    2.3,
                    3.0,
                    4.0,
                    5.0,
                    5.6,
                    6.0,
                    6.7,
                    7.5,
                    9.0,
                    12.0,
                    56.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015193",
                "heating_power_kw": [
                    0.8,
                    1.0,
                    1.2,
                    2.0,
                    3.0,
                    3.1,
                    4.8,
                    5.0,
                    5.7,
                    6.0,
                    7.0,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015194",
                "heating_power_kw": [
                    1.0,
                    1.2,
                    1.4,
                    2.3,
                    3.0,
                    4.0,
                    5.0,
                    5.6,
                    6.0,
                    6.7,
                    7.0,
                    7.5,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z026673",
                "heating_power_kw": [
                    1.5,
                    1.7,
                    3.0,
                    3.2,
                    5.0,
                    6.0,
                    6.1,
                    7.0,
                    7.6,
                    9.0,
                    10.1,
                    12.0,
                    12.6,
                    13.6,
                    76.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z026672",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    7.0,
                    8.7,
                    9.0,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z026674",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.0,
                    3.0,
                    3.6,
                    5.0,
                    6.0,
                    6.7,
                    8.2,
                    8.6,
                    8.9,
                    9.0,
                    11.1,
                    12.0,
                    13.7,
                    14.2,
                    85.0,
                    86.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z025740",
                "heating_power_kw": [
                    12.0,
                    27.04,
                    27.77,
                    28.18,
                    37.47,
                    54.0,
                    59.0,
                    88.2,
                    99.0,
                    108.0,
                    112.4,
                    116.9,
                    128.7,
                    139.9,
                    142.0,
                    152.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z025738",
                "heating_power_kw": [
                    7.01,
                    7.2,
                    7.31,
                    9.71,
                    12.0,
                    13.0,
                    15.0,
                    22.1,
                    25.0,
                    27.0,
                    28.1,
                    29.2,
                    32.2,
                    35.0,
                    36.0,
                    38.0,
                    168.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z025739",
                "heating_power_kw": [
                    12.0,
                    13.69,
                    14.06,
                    14.27,
                    18.97,
                    27.0,
                    30.0,
                    44.1,
                    51.0,
                    54.0,
                    56.2,
                    58.5,
                    64.4,
                    66.4,
                    69.9,
                    71.0,
                    76.0,
                    144.0,
                    169.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015533",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    7.0,
                    8.7,
                    9.0,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 50,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015534",
                "heating_power_kw": [
                    1.5,
                    1.7,
                    3.0,
                    3.2,
                    5.0,
                    6.0,
                    6.1,
                    7.0,
                    7.6,
                    9.0,
                    10.1,
                    12.0,
                    12.6,
                    13.6,
                    24.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 50,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015535",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.0,
                    3.0,
                    3.6,
                    5.0,
                    6.0,
                    6.7,
                    7.0,
                    8.2,
                    8.9,
                    9.0,
                    11.1,
                    12.0,
                    13.7,
                    14.2,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 50,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015536",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.3,
                    3.0,
                    3.9,
                    5.0,
                    6.0,
                    7.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    14.7,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 50,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-A-Z015532",
                "heating_power_kw": [
                    1.0,
                    1.2,
                    1.4,
                    2.3,
                    3.0,
                    4.0,
                    5.0,
                    5.6,
                    6.0,
                    6.7,
                    7.0,
                    7.5,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 50,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z028339",
                "heating_power_kw": [
                    12.0,
                    13.2
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z019168",
                "heating_power_kw": [
                    2.2,
                    8.9,
                    9.0,
                    10.0,
                    10.4,
                    11.0,
                    12.0,
                    16.0,
                    17.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z019169",
                "heating_power_kw": [
                    2.85,
                    10.65,
                    12.0,
                    13.0,
                    13.1,
                    13.2
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z019170",
                "heating_power_kw": [
                    3.8,
                    12.0,
                    14.53,
                    16.0,
                    17.0,
                    17.18,
                    17.4
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z019166",
                "heating_power_kw": [
                    1.3,
                    4.67,
                    5.0,
                    5.8,
                    6.0,
                    7.0,
                    9.0,
                    10.0,
                    12.0,
                    69.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z019167",
                "heating_power_kw": [
                    1.6,
                    6.27,
                    7.0,
                    7.5,
                    8.0,
                    9.0,
                    12.0,
                    13.0,
                    143.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z026665",
                "heating_power_kw": [
                    2.2,
                    8.9,
                    10.4,
                    11.0,
                    12.0,
                    17.0,
                    35.0,
                    104.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z026663",
                "heating_power_kw": [
                    1.3,
                    4.67,
                    5.8,
                    6.0,
                    7.0,
                    12.0,
                    17.0,
                    35.0,
                    58.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-G-Z026664",
                "heating_power_kw": [
                    1.6,
                    6.27,
                    7.5,
                    8.0,
                    9.0,
                    12.0,
                    17.0,
                    35.0,
                    75.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z026681",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.4,
                    3.0,
                    3.9,
                    5.0,
                    6.0,
                    7.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    14.7,
                    85.0,
                    101.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015225",
                "heating_power_kw": [
                    1.4,
                    1.5,
                    1.8,
                    3.0,
                    3.2,
                    5.0,
                    5.9,
                    6.0,
                    7.0,
                    7.6,
                    9.0,
                    10.1,
                    12.0,
                    12.6,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015222",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    3.0,
                    5.0,
                    6.0,
                    7.0,
                    8.7,
                    9.0,
                    12.0,
                    12.6,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015226",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.1,
                    3.6,
                    6.0,
                    6.3,
                    7.0,
                    8.0,
                    8.2,
                    8.6,
                    9.0,
                    10.7,
                    11.0,
                    12.0,
                    13.7
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015227",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.4,
                    3.0,
                    3.9,
                    5.0,
                    6.0,
                    7.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    14.7,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z026679",
                "heating_power_kw": [
                    1.4,
                    1.5,
                    1.8,
                    3.0,
                    3.2,
                    5.0,
                    5.9,
                    6.0,
                    7.0,
                    7.6,
                    9.0,
                    10.1,
                    12.0,
                    12.6,
                    76.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z026678",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    3.0,
                    5.0,
                    6.0,
                    7.0,
                    8.7,
                    9.0,
                    12.0,
                    12.6,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z026680",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.1,
                    3.6,
                    6.0,
                    6.3,
                    8.0,
                    8.2,
                    8.6,
                    8.9,
                    9.0,
                    10.7,
                    11.0,
                    12.0,
                    13.7,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022690",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    6.0,
                    7.0,
                    7.8,
                    8.0,
                    8.3,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022674",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.3,
                    6.0,
                    7.0,
                    7.8,
                    8.0,
                    8.3,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022691",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    6.0,
                    7.0,
                    7.8,
                    8.0,
                    8.3,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022675",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.3,
                    6.0,
                    7.0,
                    7.8,
                    8.0,
                    8.3,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015547",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    3.0,
                    5.0,
                    6.0,
                    7.0,
                    8.7,
                    9.0,
                    12.0,
                    12.6,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015548",
                "heating_power_kw": [
                    1.4,
                    1.5,
                    1.8,
                    3.0,
                    3.2,
                    5.0,
                    5.9,
                    6.0,
                    7.0,
                    7.6,
                    9.0,
                    10.1,
                    12.0,
                    12.6,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015549",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.1,
                    3.6,
                    6.0,
                    6.3,
                    7.0,
                    8.0,
                    8.2,
                    8.6,
                    9.0,
                    10.7,
                    11.0,
                    12.0,
                    13.7
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z015550",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.4,
                    3.0,
                    3.9,
                    5.0,
                    6.0,
                    7.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    14.7,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z026747",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    2.0,
                    3.0,
                    3.8,
                    4.0,
                    5.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    7.5,
                    8.0,
                    12.0,
                    38.0,
                    185.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022686",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022670",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0,
                    15.1
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022687",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022671",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z026748",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.0,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    5.0,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    19.07,
                    150.0,
                    175.0,
                    185.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022688",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022672",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022689",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z022673",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-200-S-Z026749",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.0,
                    2.65,
                    3.0,
                    4.0,
                    5.0,
                    5.3,
                    6.0,
                    7.0,
                    7.8,
                    8.0,
                    8.3,
                    9.0,
                    10.4,
                    12.0,
                    150.0,
                    175.0,
                    185.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z016861",
                "heating_power_kw": [
                    1.5,
                    1.7,
                    3.2,
                    6.0,
                    6.1,
                    7.0,
                    7.6,
                    8.0,
                    9.0,
                    10.0,
                    10.1,
                    11.0,
                    12.0,
                    12.6,
                    13.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z016858",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    7.0,
                    8.0,
                    8.7,
                    9.0,
                    10.0,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z016862",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.0,
                    3.6,
                    6.0,
                    6.7,
                    7.0,
                    8.0,
                    8.2,
                    8.9,
                    9.0,
                    11.0,
                    11.1,
                    12.0,
                    13.7,
                    14.2
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z016863",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.3,
                    3.9,
                    7.0,
                    8.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    13.0,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z016855",
                "heating_power_kw": [
                    0.7,
                    0.9,
                    1.0,
                    1.3,
                    2.0,
                    2.6,
                    3.0,
                    3.8,
                    4.0,
                    4.2,
                    5.0,
                    7.0,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z016856",
                "heating_power_kw": [
                    0.8,
                    1.0,
                    1.2,
                    2.0,
                    3.0,
                    3.1,
                    4.8,
                    5.0,
                    5.7,
                    6.0,
                    6.3,
                    7.0,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z016857",
                "heating_power_kw": [
                    1.0,
                    1.2,
                    1.4,
                    2.3,
                    3.0,
                    4.0,
                    5.6,
                    6.0,
                    6.7,
                    7.0,
                    7.5,
                    8.0,
                    9.0,
                    12.0,
                    71.0,
                    163.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017617",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    7.0,
                    8.0,
                    8.7,
                    9.0,
                    10.0,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017621",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    7.0,
                    8.0,
                    8.7,
                    9.0,
                    10.0,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017622",
                "heating_power_kw": [
                    1.5,
                    1.7,
                    3.2,
                    6.0,
                    6.1,
                    7.0,
                    7.6,
                    8.0,
                    9.0,
                    10.0,
                    10.1,
                    11.0,
                    12.0,
                    12.6,
                    13.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017625",
                "heating_power_kw": [
                    1.5,
                    1.7,
                    3.2,
                    6.0,
                    6.1,
                    7.0,
                    7.6,
                    8.0,
                    9.0,
                    10.0,
                    10.1,
                    11.0,
                    12.0,
                    12.6,
                    13.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017623",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.0,
                    3.6,
                    6.0,
                    6.7,
                    7.0,
                    8.0,
                    8.2,
                    8.9,
                    9.0,
                    11.0,
                    11.1,
                    12.0,
                    13.7,
                    14.2
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017626",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.0,
                    3.6,
                    6.0,
                    6.7,
                    7.0,
                    8.0,
                    8.2,
                    8.9,
                    9.0,
                    11.0,
                    11.1,
                    12.0,
                    13.7,
                    14.2
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017624",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.3,
                    3.9,
                    7.0,
                    8.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    13.0,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017627",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.3,
                    3.9,
                    7.0,
                    8.0,
                    9.0,
                    9.2,
                    10.1,
                    11.6,
                    12.0,
                    13.0,
                    14.7
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017614",
                "heating_power_kw": [
                    0.7,
                    0.9,
                    1.0,
                    1.3,
                    2.0,
                    2.6,
                    3.0,
                    3.8,
                    4.0,
                    4.2,
                    5.0,
                    7.0,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017618",
                "heating_power_kw": [
                    0.7,
                    0.9,
                    1.0,
                    1.3,
                    2.0,
                    2.6,
                    3.0,
                    3.8,
                    4.0,
                    4.2,
                    5.0,
                    7.0,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017615",
                "heating_power_kw": [
                    0.8,
                    1.0,
                    1.2,
                    2.0,
                    3.0,
                    3.1,
                    4.8,
                    5.0,
                    5.7,
                    6.0,
                    6.3,
                    7.0,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017619",
                "heating_power_kw": [
                    0.8,
                    1.0,
                    1.2,
                    2.0,
                    3.0,
                    3.1,
                    4.8,
                    5.0,
                    5.7,
                    6.0,
                    6.3,
                    7.0,
                    9.0,
                    12.0,
                    85.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017616",
                "heating_power_kw": [
                    1.0,
                    1.2,
                    1.4,
                    2.3,
                    3.0,
                    4.0,
                    5.6,
                    6.0,
                    6.7,
                    7.0,
                    7.5,
                    8.0,
                    9.0,
                    12.0,
                    71.0,
                    163.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-A-Z017620",
                "heating_power_kw": [
                    1.0,
                    1.2,
                    1.4,
                    2.3,
                    3.0,
                    4.0,
                    5.6,
                    6.0,
                    6.7,
                    7.0,
                    7.5,
                    8.0,
                    9.0,
                    12.0,
                    71.0,
                    163.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-G-Z016843",
                "heating_power_kw": [
                    2.2,
                    8.9,
                    9.0,
                    10.0,
                    10.4,
                    11.0,
                    12.0,
                    16.0,
                    17.0,
                    19.07
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-G-Z022355",
                "heating_power_kw": [
                    2.2,
                    8.9,
                    9.0,
                    10.0,
                    10.4,
                    11.0,
                    12.0,
                    16.0,
                    17.0,
                    19.07
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-G-Z016841",
                "heating_power_kw": [
                    1.3,
                    4.67,
                    5.0,
                    5.8,
                    6.0,
                    7.0,
                    9.0,
                    10.0,
                    10.4,
                    12.0,
                    19.07,
                    69.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-G-Z022353",
                "heating_power_kw": [
                    1.3,
                    4.67,
                    5.0,
                    5.8,
                    6.0,
                    7.0,
                    9.0,
                    10.0,
                    10.4,
                    12.0,
                    17.0,
                    19.07,
                    69.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-G-Z016842",
                "heating_power_kw": [
                    1.6,
                    6.27,
                    7.0,
                    7.5,
                    8.0,
                    9.0,
                    10.4,
                    12.0,
                    13.0,
                    19.07,
                    143.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-G-Z022354",
                "heating_power_kw": [
                    1.6,
                    6.27,
                    7.0,
                    7.5,
                    8.0,
                    9.0,
                    10.4,
                    12.0,
                    13.0,
                    17.0,
                    19.07,
                    143.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z015352",
                "heating_power_kw": [
                    1.4,
                    1.5,
                    1.8,
                    3.2,
                    5.9,
                    6.0,
                    7.0,
                    7.6,
                    8.0,
                    9.0,
                    10.0,
                    10.1,
                    11.0,
                    12.0,
                    12.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z015349",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    8.7,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    12.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z015353",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.1,
                    3.6,
                    6.0,
                    6.3,
                    7.0,
                    8.0,
                    8.2,
                    8.6,
                    9.0,
                    10.0,
                    10.7,
                    11.0,
                    12.0,
                    13.7,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z015354",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.4,
                    3.9,
                    6.0,
                    7.0,
                    8.0,
                    9.0,
                    9.2,
                    10.0,
                    10.1,
                    11.0,
                    11.6,
                    12.0,
                    14.7,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022720",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022722",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022724",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    6.0,
                    7.0,
                    7.4,
                    8.0,
                    8.3,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022740",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    6.0,
                    7.0,
                    7.4,
                    8.0,
                    8.3,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022725",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    6.0,
                    7.0,
                    7.4,
                    8.0,
                    8.3,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025130",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    7.0,
                    7.4,
                    8.0,
                    8.3,
                    9.0,
                    10.0,
                    12.0,
                    19.07,
                    150.0,
                    175.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025133",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    7.0,
                    7.4,
                    8.0,
                    8.3,
                    9.0,
                    10.0,
                    12.0,
                    19.07,
                    150.0,
                    175.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025136",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    7.0,
                    7.4,
                    8.0,
                    8.3,
                    9.0,
                    10.0,
                    12.0,
                    19.07,
                    150.0,
                    175.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017631",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    8.7,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    12.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017635",
                "heating_power_kw": [
                    1.3,
                    1.5,
                    1.7,
                    2.8,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    8.7,
                    9.0,
                    10.0,
                    11.0,
                    12.0,
                    12.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017636",
                "heating_power_kw": [
                    1.4,
                    1.5,
                    1.8,
                    3.2,
                    5.9,
                    6.0,
                    7.0,
                    7.6,
                    8.0,
                    9.0,
                    10.0,
                    10.1,
                    11.0,
                    12.0,
                    12.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017639",
                "heating_power_kw": [
                    1.4,
                    1.5,
                    1.8,
                    3.2,
                    5.9,
                    6.0,
                    7.0,
                    7.6,
                    8.0,
                    9.0,
                    10.0,
                    10.1,
                    11.0,
                    12.0,
                    12.6,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017637",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.1,
                    3.6,
                    6.0,
                    6.3,
                    7.0,
                    8.0,
                    8.2,
                    8.6,
                    9.0,
                    10.0,
                    10.7,
                    11.0,
                    12.0,
                    13.7,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017640",
                "heating_power_kw": [
                    1.6,
                    1.8,
                    2.1,
                    3.6,
                    6.0,
                    6.3,
                    7.0,
                    8.0,
                    8.2,
                    8.6,
                    9.0,
                    10.0,
                    10.7,
                    11.0,
                    12.0,
                    13.7,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017638",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.4,
                    3.9,
                    6.0,
                    7.0,
                    8.0,
                    9.0,
                    9.2,
                    10.0,
                    10.1,
                    11.0,
                    11.6,
                    12.0,
                    14.7,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z017641",
                "heating_power_kw": [
                    1.8,
                    2.0,
                    2.4,
                    3.9,
                    6.0,
                    7.0,
                    8.0,
                    9.0,
                    9.2,
                    10.0,
                    10.1,
                    11.0,
                    11.6,
                    12.0,
                    14.7,
                    51.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022736",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022721",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022737",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025128",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.8,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0,
                    38.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025131",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.8,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0,
                    38.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025134",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    3.0,
                    3.8,
                    4.8,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0,
                    38.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022738",
                "heating_power_kw": [
                    1.1,
                    1.39,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022723",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022739",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    8.5,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025129",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    19.07,
                    150.0,
                    175.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025132",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    19.07,
                    150.0,
                    175.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z025135",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.8,
                    6.95,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    19.07,
                    150.0,
                    175.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-S-Z022741",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.65,
                    3.0,
                    4.0,
                    5.8,
                    6.0,
                    7.0,
                    7.4,
                    8.0,
                    8.3,
                    9.8,
                    10.0,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-SI-Z025267",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    68.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-SI-Z025266",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    68.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-SI-Z025269",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    68.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-SI-Z025268",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    68.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-SI-Z025265",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    68.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-222-SI-Z025264",
                "heating_power_kw": [
                    1.1,
                    1.36,
                    2.25,
                    3.0,
                    4.0,
                    4.5,
                    6.0,
                    6.8,
                    7.0,
                    8.0,
                    9.0,
                    12.0,
                    68.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032444",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032329",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033120",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033116",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033124",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032421",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032306",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032445",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032330",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033121",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033117",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033125",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032422",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032307",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032446",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032331",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033122",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033118",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033126",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032423",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032308",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032447",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032332",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032449",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032334",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033123",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033119",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033127",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033132",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033128",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033136",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032424",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032309",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032426",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032311",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032450",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032335",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033133",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033129",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033137",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032427",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032312",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032451",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032336",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033134",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033130",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033138",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032428",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032313",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032452",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032337",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033135",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033131",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033139",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032429",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z032314",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032513",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032398",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032490",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032375",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032514",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032399",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032491",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032376",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032515",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032400",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032492",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032377",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032516",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032401",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032518",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032403",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032493",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032378",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032495",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032380",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032519",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032404",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032496",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032381",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032520",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032405",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032497",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032382",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032521",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032406",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032498",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Compact-Z032383",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032536",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032554",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032555",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032537",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032556",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032538",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032557",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032539",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032559",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032541",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032560",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032542",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032561",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032543",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032562",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Hybrid-Z032544",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033164",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033165",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033166",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033167",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033148",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    11.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033149",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033150",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033151",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033180",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033192",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033181",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033193",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033182",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033194",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033168",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033169",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033170",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033171",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033152",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    11.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033153",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033154",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033155",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033183",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033195",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033184",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033196",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033185",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033197",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033172",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033173",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033174",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033175",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033156",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    11.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033157",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033158",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033159",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033176",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    13.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033177",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033178",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    26.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033179",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033186",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033198",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033187",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033199",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033188",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033200",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033160",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.0,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033161",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033162",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033163",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    32.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033189",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033201",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    19.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033190",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033202",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    24.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033191",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033203",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    29.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z022164",
                "heating_power_kw": [
                    1.19,
                    1.31,
                    1.38,
                    3.07,
                    5.0,
                    5.8,
                    6.3,
                    7.0,
                    7.3,
                    8.0,
                    9.7,
                    10.0,
                    12.0,
                    12.9,
                    25.0,
                    55.0,
                    145.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032467",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032352",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032468",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032353",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032469",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032354",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032576",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032572",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032470",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032355",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032472",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032357",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032577",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032573",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032473",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032358",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032578",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    17.1,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032574",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    17.1,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032474",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032359",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032579",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    18.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032575",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    18.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032475",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Modular-Z032360",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-A-Z022781",
                "heating_power_kw": [
                    1.56,
                    1.65,
                    1.68,
                    3.75,
                    5.0,
                    6.7,
                    7.0,
                    7.9,
                    8.0,
                    8.1,
                    10.0,
                    11.1,
                    12.0,
                    15.1,
                    55.0,
                    145.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-Z023943",
                "heating_power_kw": [
                    1.56,
                    1.67,
                    1.68,
                    3.75,
                    5.0,
                    6.7,
                    7.0,
                    8.0,
                    8.1,
                    8.2,
                    10.0,
                    11.1,
                    12.0,
                    15.1,
                    55.0,
                    145.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-Z023942",
                "heating_power_kw": [
                    1.23,
                    1.31,
                    1.38,
                    3.07,
                    5.0,
                    5.8,
                    6.5,
                    7.0,
                    7.3,
                    8.0,
                    9.7,
                    10.0,
                    12.0,
                    13.0,
                    55.0,
                    145.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-AH-Z023939",
                "heating_power_kw": [
                    1.19,
                    1.31,
                    1.38,
                    3.07,
                    5.0,
                    6.3,
                    7.0,
                    7.3,
                    8.0,
                    9.7,
                    10.0,
                    12.0,
                    12.9,
                    55.0,
                    145.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-SH-Z024781",
                "heating_power_kw": [
                    1.32,
                    1.72,
                    2.0,
                    2.65,
                    4.0,
                    5.0,
                    5.8,
                    6.0,
                    7.0,
                    7.4,
                    8.3,
                    10.0,
                    11.0,
                    12.0,
                    185.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-250-SH-Z024777",
                "heating_power_kw": [
                    0.95,
                    1.07,
                    1.77,
                    2.0,
                    3.8,
                    4.0,
                    5.0,
                    5.3,
                    5.5,
                    6.0,
                    7.0,
                    8.0,
                    12.0,
                    185.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-262-A-Z027025",
                "heating_power_kw": [
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-262-A-Z027026",
                "heating_power_kw": [
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-262-A-Z027027",
                "heating_power_kw": [
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012778",
                "heating_power_kw": [
                    4.48,
                    12.0,
                    17.0,
                    19.0,
                    21.0,
                    21.1,
                    21.2,
                    22.0,
                    24.0,
                    29.0,
                    31.0,
                    42.8,
                    58.9,
                    85.6,
                    117.8
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012781",
                "heating_power_kw": [
                    4.48,
                    12.0,
                    17.0,
                    19.0,
                    21.0,
                    21.2,
                    22.0,
                    24.0,
                    29.0,
                    31.0,
                    42.8,
                    58.9,
                    85.6,
                    117.8
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012779",
                "heating_power_kw": [
                    5.96,
                    12.0,
                    23.3,
                    26.0,
                    28.8,
                    29.0,
                    30.0,
                    33.0,
                    39.0,
                    42.8,
                    43.0,
                    58.9,
                    85.6,
                    117.8
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012782",
                "heating_power_kw": [
                    5.96,
                    12.0,
                    23.3,
                    26.0,
                    28.8,
                    29.0,
                    30.0,
                    33.0,
                    39.0,
                    42.8,
                    43.0,
                    58.9,
                    85.6,
                    117.8
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012780",
                "heating_power_kw": [
                    3.0,
                    9.28,
                    12.0,
                    34.2,
                    40.0,
                    42.8,
                    43.0,
                    45.0,
                    49.0,
                    58.9,
                    59.0,
                    63.0,
                    85.6,
                    117.8,
                    176.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012783",
                "heating_power_kw": [
                    3.0,
                    9.28,
                    12.0,
                    34.2,
                    40.0,
                    42.8,
                    43.0,
                    45.0,
                    49.0,
                    58.9,
                    59.0,
                    63.0,
                    85.6,
                    117.8,
                    176.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012784",
                "heating_power_kw": [
                    4.48,
                    12.0,
                    17.0,
                    19.0,
                    21.0,
                    21.2,
                    22.0,
                    24.0,
                    29.0,
                    31.0,
                    42.4,
                    42.8,
                    58.9,
                    85.6,
                    117.8
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012785",
                "heating_power_kw": [
                    5.96,
                    12.0,
                    23.3,
                    26.0,
                    28.8,
                    29.0,
                    30.0,
                    33.0,
                    39.0,
                    42.8,
                    43.0,
                    57.6,
                    58.9,
                    85.6,
                    117.8
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z012786",
                "heating_power_kw": [
                    3.0,
                    9.28,
                    12.0,
                    34.2,
                    40.0,
                    42.8,
                    43.0,
                    45.0,
                    49.0,
                    58.9,
                    59.0,
                    63.0,
                    85.6,
                    117.8,
                    176.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z026667",
                "heating_power_kw": [
                    1.1,
                    2.0,
                    4.0,
                    4.4,
                    5.0,
                    5.3,
                    6.0,
                    11.4,
                    12.0,
                    17.0,
                    35.0,
                    42.8,
                    58.9,
                    85.6,
                    117.8,
                    168.0,
                    185.0
                ],
                "scop": 4.9,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z026668",
                "heating_power_kw": [
                    1.5,
                    2.0,
                    4.0,
                    5.0,
                    5.8,
                    6.0,
                    7.4,
                    12.0,
                    13.0,
                    14.0,
                    15.0,
                    15.9,
                    17.0,
                    35.0,
                    42.8,
                    58.9,
                    85.6,
                    117.8,
                    183.0,
                    185.0,
                    187.0
                ],
                "scop": 4.9,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z019443",
                "heating_power_kw": [
                    0.9,
                    3.5,
                    4.3,
                    6.0,
                    8.6,
                    12.0,
                    42.8,
                    58.9,
                    85.6,
                    117.8,
                    163.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z019444",
                "heating_power_kw": [
                    1.1,
                    4.4,
                    5.3,
                    11.4,
                    12.0,
                    42.8,
                    58.9,
                    85.6,
                    117.8,
                    168.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z019533",
                "heating_power_kw": [
                    1.5,
                    5.8,
                    7.4,
                    7.5,
                    12.0,
                    13.0,
                    14.0,
                    15.0,
                    15.9,
                    42.8,
                    58.9,
                    85.6,
                    117.8,
                    183.0,
                    187.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z026666",
                "heating_power_kw": [
                    0.9,
                    2.0,
                    3.5,
                    4.0,
                    4.3,
                    5.0,
                    6.0,
                    8.6,
                    12.0,
                    17.0,
                    35.0,
                    42.8,
                    58.9,
                    85.6,
                    117.8,
                    163.0,
                    185.0
                ],
                "scop": 4.9,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-333-G-Z016844",
                "heating_power_kw": [
                    0.9,
                    3.5,
                    4.3,
                    6.0,
                    8.6,
                    11.4,
                    12.0,
                    19.07,
                    163.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-333-G-Z022356",
                "heating_power_kw": [
                    0.9,
                    3.5,
                    4.3,
                    6.0,
                    8.6,
                    11.4,
                    12.0,
                    17.0,
                    19.07,
                    163.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-333-G-Z016845",
                "heating_power_kw": [
                    1.1,
                    4.4,
                    5.3,
                    8.6,
                    11.4,
                    12.0,
                    19.07,
                    168.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-333-G-Z022357",
                "heating_power_kw": [
                    1.1,
                    4.4,
                    5.3,
                    8.6,
                    11.4,
                    12.0,
                    17.0,
                    19.07,
                    168.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z013399",
                "heating_power_kw": [
                    5.9,
                    12.0,
                    23.0,
                    28.7,
                    29.0,
                    30.0,
                    32.0,
                    34.0,
                    35.0,
                    36.0,
                    57.4,
                    84.6,
                    153.0,
                    195.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z013400",
                "heating_power_kw": [
                    6.5,
                    12.0,
                    22.0,
                    26.3,
                    32.7,
                    33.0,
                    34.0,
                    37.0,
                    38.0,
                    40.0,
                    41.0,
                    65.4,
                    84.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-300-G-Z013401",
                "heating_power_kw": [
                    8.7,
                    12.0,
                    33.6,
                    42.0,
                    42.3,
                    43.0,
                    48.0,
                    49.0,
                    52.0,
                    53.0,
                    84.6,
                    117.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-350-G-Z013390",
                "heating_power_kw": [
                    12.0,
                    20.5,
                    84.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-350-G-Z013391",
                "heating_power_kw": [
                    12.0,
                    28.7,
                    84.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-350-G-Z013392",
                "heating_power_kw": [
                    12.0,
                    32.7,
                    84.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Vitocal-350-G-Z013393",
                "heating_power_kw": [
                    12.0,
                    42.3,
                    84.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033037",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033038",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033039",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033040",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033041",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033042",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033043",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033140",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033141",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033142",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033143",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033144",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033145",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033146",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033147",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033001",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033008",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033002",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033009",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033003",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033010",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    5.7,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033004",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033011",
                "heating_power_kw": [
                    4.55,
                    7.3,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033005",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033012",
                "heating_power_kw": [
                    4.8,
                    7.4,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033006",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033013",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033007",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033014",
                "heating_power_kw": [
                    7.2,
                    9.1,
                    12.0,
                    12.4,
                    14.9,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033100",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033108",
                "heating_power_kw": [
                    2.3,
                    3.8,
                    4.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033101",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033109",
                "heating_power_kw": [
                    3.6,
                    4.8,
                    5.6,
                    6.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033102",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033110",
                "heating_power_kw": [
                    3.7,
                    5.6,
                    6.5,
                    8.0,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033104",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033112",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033103",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033111",
                "heating_power_kw": [
                    4.55,
                    9.7,
                    12.0,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033105",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033113",
                "heating_power_kw": [
                    5.4,
                    8.1,
                    11.1,
                    12.0,
                    13.4,
                    15.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033106",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033114",
                "heating_power_kw": [
                    7.2,
                    8.5,
                    11.7,
                    12.0,
                    15.0,
                    17.1,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033107",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Z033115",
                "heating_power_kw": [
                    7.2,
                    9.0,
                    12.0,
                    12.3,
                    15.0,
                    18.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7262983",
                "heating_power_kw": [
                    12.0,
                    12.4
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7484782",
                "heating_power_kw": [
                    12.0,
                    12.4
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "9570169",
                "heating_power_kw": [
                    9.0,
                    12.0,
                    12.4
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "ZK08164",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            }
        ],
        "Sole-Wasser-Wärmepumpe": [
            {
                "model": "Vitocal 300-G",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    10.0,
                    13.0,
                    17.0,
                    22.0
                ],
                "scop": 5.1,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [
                    "Erdwärmesonden",
                    "Erdwärmekollektor",
                    "Smart Grid"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.9,
                "awards": [
                    "Beste Erdwärmepumpe 2024"
                ]
            },
            {
                "model": "Vitocal 200-G",
                "heating_power_kw": [
                    5.0,
                    7.0,
                    10.0,
                    13.0
                ],
                "scop": 4.9,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [
                    "Erdwärmesonden",
                    "Erdwärmekollektor"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.6,
                "awards": []
            }
        ],
        "Wasser-Wasser-Wärmepumpe": [
            {
                "model": "Vitocal 350-G Pro",
                "heating_power_kw": [
                    8.0,
                    12.0,
                    16.0,
                    21.0,
                    27.0
                ],
                "scop": 5.4,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [
                    "Grundwasser-Nutzung",
                    "Smart Grid",
                    "Kühlfunktion"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 5.0,
                "awards": [
                    "Premium Testsieger 2024",
                    "Höchste Effizienz"
                ]
            }
        ]
    },
    "Buderus": {
        "Luft-Wasser-Wärmepumpe": [
            {
                "model": "Logatherm WLW196i AR",
                "heating_power_kw": [
                    5.0,
                    7.0,
                    9.0,
                    11.0,
                    14.0,
                    17.0
                ],
                "scop": 4.7,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [
                    "Inverter-Technologie",
                    "Smart Home",
                    "Active Cooling"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.7,
                "awards": [
                    "Top-Produkt 2024"
                ]
            },
            {
                "model": "Logatherm WLW186i AR",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    10.0,
                    13.0
                ],
                "scop": 4.5,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [
                    "Inverter-Technologie",
                    "Smart Home"
                ],
                "refrigerant": "R32",
                "rating": 4.4,
                "awards": []
            },
            {
                "model": "Logatherm WLW176i AR",
                "heating_power_kw": [
                    8.0,
                    11.0,
                    14.0
                ],
                "scop": 4.4,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [
                    "Kompakt",
                    "Split-Gerät möglich"
                ],
                "refrigerant": "R32",
                "rating": 4.2,
                "awards": []
            },
            {
                "model": "Logatherm WLW166 AR E",
                "heating_power_kw": [
                    5.0,
                    7.0,
                    9.0
                ],
                "scop": 4.2,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": [
                    "Economy-Serie",
                    "Einfache Installation"
                ],
                "refrigerant": "R410A",
                "rating": 3.9,
                "awards": []
            },
            {
                "model": "8738201410",
                "heating_power_kw": [
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738201409",
                "heating_power_kw": [
                    11.0,
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738205045",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738205044",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-25-3",
                "heating_power_kw": [
                    12.0,
                    12.1,
                    25.0,
                    25.2,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-28-3",
                "heating_power_kw": [
                    12.0,
                    14.2,
                    25.0,
                    28.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-33-3",
                "heating_power_kw": [
                    12.0,
                    16.3,
                    25.0,
                    33.5,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-40-3",
                "heating_power_kw": [
                    12.0,
                    19.5,
                    25.0,
                    40.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-45-3",
                "heating_power_kw": [
                    12.0,
                    21.9,
                    25.0,
                    45.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-50-3",
                "heating_power_kw": [
                    12.0,
                    24.3,
                    25.0,
                    50.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-56-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    27.4,
                    56.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-62-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    29.9,
                    61.5,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-67-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    32.6,
                    67.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-73-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    38.0,
                    73.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-79-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    38.0,
                    78.5,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-85-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    39.8,
                    85.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-90-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    39.8,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-25-3",
                "heating_power_kw": [
                    12.0,
                    12.1,
                    25.0,
                    25.2,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-28-3",
                "heating_power_kw": [
                    12.0,
                    14.2,
                    25.0,
                    28.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-33-3",
                "heating_power_kw": [
                    12.0,
                    16.3,
                    25.0,
                    33.5,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-40-3",
                "heating_power_kw": [
                    12.0,
                    19.5,
                    25.0,
                    40.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-45-3",
                "heating_power_kw": [
                    12.0,
                    21.9,
                    25.0,
                    45.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-50-3",
                "heating_power_kw": [
                    12.0,
                    24.3,
                    25.0,
                    50.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-56-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    27.4,
                    56.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-62-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    29.9,
                    61.5,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-67-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    32.6,
                    67.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-73-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    38.0,
                    73.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-79-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    38.0,
                    78.5,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-85-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    39.8,
                    85.0,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "AF5301A-A-C-90-3",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    39.8,
                    90.0
                ],
                "scop": 4.46,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "5354210",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718586815",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738209567",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7719003366",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718544963",
                "heating_power_kw": [
                    12.0,
                    40.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738204928",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738331557",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "67900475",
                "heating_power_kw": [
                    12.0,
                    25.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i",
                "heating_power_kw": [
                    11.7,
                    12.0,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7719003329",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7735600330",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7747204683",
                "heating_power_kw": [
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7747204682",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7747204681",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7747204680",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600165",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600209",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7748000025",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7748000026",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599200",
                "heating_power_kw": [
                    12.0,
                    50.0,
                    80.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599201",
                "heating_power_kw": [
                    12.0,
                    80.0,
                    150.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599202",
                "heating_power_kw": [
                    12.0,
                    15.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599203",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599204",
                "heating_power_kw": [
                    12.0,
                    50.0,
                    70.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599205",
                "heating_power_kw": [
                    12.0,
                    15.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599377",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599378",
                "heating_power_kw": [
                    12.0,
                    80.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599379",
                "heating_power_kw": [
                    12.0,
                    70.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718599380",
                "heating_power_kw": [
                    12.0,
                    80.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718590658",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3868354",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718542444",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739615492",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738206183",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738206184",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "82567096",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738319546",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "GBH172i-2-15-DW-H",
                "heating_power_kw": [
                    12.0,
                    17.0,
                    19.3,
                    30.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "GBH172i-2-30-DW-H",
                "heating_power_kw": [
                    12.0,
                    30.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739615438",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739615437",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739606862",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739606860",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7719003241",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600163",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600207",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600162",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600161",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600206",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW166i",
                "heating_power_kw": [
                    1.0,
                    9.6,
                    12.0,
                    18.0,
                    25.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-4",
                "heating_power_kw": [
                    3.9,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-5",
                "heating_power_kw": [
                    5.4,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-7",
                "heating_power_kw": [
                    6.7,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7735600332",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612623",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612624",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612625",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612626",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612627",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612628",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739615460",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739615461",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612629",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612630",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612631",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612632",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612633",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739612634",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600168",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600212",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738208122",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738205009",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738205007",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739613392",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739613391",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738307341",
                "heating_power_kw": [
                    6.0,
                    12.0,
                    24.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738110103",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718581709",
                "heating_power_kw": [
                    6.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7747204694",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7739613142",
                "heating_power_kw": [
                    12.0,
                    17.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8738202915",
                "heating_power_kw": [
                    12.0,
                    30.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718592386",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7747204698",
                "heating_power_kw": [
                    6.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "63041999",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7735600273",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "5024886",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "5024888",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "63012350",
                "heating_power_kw": [
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "63210008",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600166",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600210",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718544956",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738110906",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600164",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600208",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "67900470",
                "heating_power_kw": [
                    12.0,
                    15.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "67900471",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "67900472",
                "heating_power_kw": [
                    12.0,
                    50.0,
                    70.0,
                    150.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600167",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "7738600211",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-10-MB-A-H",
                "heating_power_kw": [
                    5.0,
                    7.0,
                    9.6,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-12-MB-A-H",
                "heating_power_kw": [
                    5.0,
                    7.0,
                    10.0,
                    11.6,
                    12.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-5-MB-A-H",
                "heating_power_kw": [
                    5.0,
                    5.4,
                    7.0,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-7-MB-A-H",
                "heating_power_kw": [
                    5.0,
                    6.7,
                    7.0,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-B-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.48,
                    5.5,
                    6.15,
                    6.2,
                    7.57,
                    9.0,
                    12.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-B-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.4,
                    7.91,
                    9.0,
                    12.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-E-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.48,
                    5.5,
                    6.15,
                    6.2,
                    7.57,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-E-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.4,
                    7.91,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-MB-A-H",
                "heating_power_kw": [
                    5.0,
                    7.0,
                    9.6,
                    10.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-10-MB-AR",
                "heating_power_kw": [
                    4.0,
                    5.0,
                    7.0,
                    9.6,
                    10.0,
                    11.7,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-12-MB-AR",
                "heating_power_kw": [
                    4.0,
                    5.0,
                    7.0,
                    10.0,
                    11.6,
                    12.0,
                    12.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-T190-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.48,
                    5.5,
                    6.15,
                    6.2,
                    7.57,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-T190-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.4,
                    7.91,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-TP120-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.48,
                    5.5,
                    6.15,
                    6.2,
                    7.57,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-TS185-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.48,
                    5.5,
                    6.15,
                    6.2,
                    7.57,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-TS185-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.4,
                    7.91,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-10-AR-E",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-10-AR-T180",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-10-AR-TP70",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-12-AR-E",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-12-AR-T180",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW176i-12-AR-TP70",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-10-AR-E",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    11.6,
                    12.0,
                    35.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-10-AR-E-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-10-AR-T180",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-10-AR-T180-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-10-AR-TP70",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-10-AR-TP70-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    9.6,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-AR-E",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-AR-E-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-AR-T180",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-AR-T180-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-AR-TP70",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-AR-TP70-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-E",
                "heating_power_kw": [
                    9.0,
                    11.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-EW",
                "heating_power_kw": [
                    9.0,
                    11.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-T180",
                "heating_power_kw": [
                    9.0,
                    11.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-T180W",
                "heating_power_kw": [
                    9.0,
                    11.5,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-TP70",
                "heating_power_kw": [
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-12-TP70W",
                "heating_power_kw": [
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-4-AR-E",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    3.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-4-AR-E-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    3.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-4-AR-T180",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    3.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-4-AR-T180-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    3.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-4-AR-TP70",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    3.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-4-AR-TP70-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    3.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-5-AR-E",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    5.4,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-5-AR-E-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    5.4,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-5-AR-T180",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    5.4,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-5-AR-T180-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-5-AR-TP70",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    5.4,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-5-AR-TP70-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    5.4,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-7-AR-E",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-7-AR-E-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-7-AR-T180",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-7-AR-T180-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-7-AR-TP70",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW186i-7-AR-TP70-W",
                "heating_power_kw": [
                    2.1,
                    2.4,
                    2.9,
                    4.0,
                    4.6,
                    5.0,
                    6.7,
                    7.0,
                    9.0,
                    10.0,
                    11.6,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196-14-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-A-H-S-plus",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-AR-TP120",
                "heating_power_kw": [
                    5.18,
                    7.0,
                    7.2,
                    8.86,
                    9.0,
                    10.73,
                    11.0,
                    11.12,
                    11.7,
                    11.71,
                    12.0,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-AR-TP120",
                "heating_power_kw": [
                    5.63,
                    7.2,
                    7.86,
                    9.0,
                    10.17,
                    11.92,
                    12.0,
                    13.02,
                    14.0,
                    14.37,
                    14.4
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-4-AR-TP120",
                "heating_power_kw": [
                    2.03,
                    2.3,
                    2.79,
                    4.0,
                    4.12,
                    4.61,
                    5.3,
                    5.86,
                    9.0,
                    12.0,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-AR-TP120",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.83,
                    6.0,
                    6.18,
                    6.3,
                    6.71,
                    7.6,
                    9.0,
                    12.0,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-AR-TP120",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.32,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.7,
                    12.0,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-11-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-AR-B",
                "heating_power_kw": [
                    5.18,
                    7.0,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.0,
                    10.7,
                    10.73,
                    11.0,
                    11.12,
                    11.71,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-AR-E",
                "heating_power_kw": [
                    5.18,
                    7.0,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.0,
                    10.73,
                    11.0,
                    11.12,
                    11.71,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-AR-T190",
                "heating_power_kw": [
                    5.18,
                    7.0,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.7,
                    10.73,
                    11.0,
                    11.12,
                    11.71,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-AR-TS185",
                "heating_power_kw": [
                    5.18,
                    7.0,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.7,
                    10.73,
                    11.0,
                    11.12,
                    11.71,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-IR-B",
                "heating_power_kw": [
                    5.11,
                    7.11,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.0,
                    10.99,
                    11.12,
                    12.0,
                    13.1,
                    13.7,
                    14.0,
                    25.0,
                    28.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-IR-E",
                "heating_power_kw": [
                    5.11,
                    7.11,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.0,
                    10.99,
                    11.12,
                    12.0,
                    13.1,
                    13.7,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-IR-T190",
                "heating_power_kw": [
                    5.11,
                    7.11,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.99,
                    11.12,
                    12.0,
                    13.1,
                    13.7,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-IR-TP120",
                "heating_power_kw": [
                    5.11,
                    7.11,
                    7.2,
                    8.86,
                    9.0,
                    10.0,
                    10.99,
                    11.12,
                    11.7,
                    12.0,
                    13.1,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-11-IR-TS185",
                "heating_power_kw": [
                    5.11,
                    7.11,
                    7.2,
                    8.0,
                    8.86,
                    9.0,
                    10.99,
                    11.12,
                    12.0,
                    13.1,
                    13.7,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-AR-B",
                "heating_power_kw": [
                    5.63,
                    7.2,
                    7.86,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    13.02,
                    14.0,
                    14.37,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-AR-E",
                "heating_power_kw": [
                    5.63,
                    7.2,
                    7.86,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    13.0,
                    13.02,
                    14.0,
                    14.37,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-AR-T190",
                "heating_power_kw": [
                    5.63,
                    7.2,
                    7.86,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    13.02,
                    14.0,
                    14.37,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-AR-TS185",
                "heating_power_kw": [
                    5.63,
                    7.2,
                    7.86,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    13.02,
                    14.0,
                    14.37,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-IR-B",
                "heating_power_kw": [
                    4.8,
                    7.2,
                    7.42,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    12.45,
                    14.0,
                    16.0,
                    25.0,
                    28.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-IR-E",
                "heating_power_kw": [
                    4.8,
                    7.2,
                    7.42,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    12.45,
                    14.0,
                    16.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-IR-T190",
                "heating_power_kw": [
                    4.8,
                    7.2,
                    7.42,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    12.45,
                    14.0,
                    16.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-IR-TS185",
                "heating_power_kw": [
                    4.8,
                    7.2,
                    7.42,
                    8.0,
                    9.0,
                    10.0,
                    10.17,
                    11.92,
                    12.0,
                    12.45,
                    14.0,
                    16.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-4-AR-B",
                "heating_power_kw": [
                    2.03,
                    2.3,
                    2.79,
                    4.0,
                    4.12,
                    4.61,
                    5.6,
                    5.86,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-4-AR-E",
                "heating_power_kw": [
                    2.03,
                    2.3,
                    2.79,
                    4.0,
                    4.12,
                    4.61,
                    5.6,
                    5.86,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-4-AR-T190",
                "heating_power_kw": [
                    2.03,
                    2.3,
                    2.79,
                    4.0,
                    4.12,
                    4.61,
                    5.6,
                    5.86,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-4-AR-TS185",
                "heating_power_kw": [
                    2.03,
                    2.3,
                    2.79,
                    4.0,
                    4.12,
                    4.61,
                    5.6,
                    5.86,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-6-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-AR-B",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.83,
                    5.0,
                    6.0,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-AR-E",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.83,
                    5.0,
                    6.0,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-AR-T190",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.83,
                    5.0,
                    6.0,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-AR-TS185",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.83,
                    5.0,
                    6.0,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-AR-TS185",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.83,
                    6.18,
                    6.71,
                    7.6,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-IR-B",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.0,
                    4.83,
                    5.0,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0,
                    28.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-IR-E",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.0,
                    4.83,
                    5.0,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-IR-T190",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.0,
                    4.83,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-IR-TS185",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.0,
                    4.83,
                    6.18,
                    6.71,
                    7.6,
                    7.7,
                    8.0,
                    9.0,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW-8-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-AR-B",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.32,
                    7.0,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.5,
                    10.7,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-AR-E",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.32,
                    7.0,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.5,
                    10.7,
                    12.0,
                    14.0,
                    25.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-AR-T190",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.32,
                    7.0,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.5,
                    10.7,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-IR-B",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.0,
                    6.32,
                    7.0,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.5,
                    10.7,
                    12.0,
                    14.0,
                    25.0,
                    28.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-IR-E",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.0,
                    6.32,
                    7.0,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.5,
                    10.7,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-IR-T190",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.0,
                    6.32,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.5,
                    10.7,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-IR-TS185",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.0,
                    6.32,
                    8.0,
                    8.43,
                    9.0,
                    9.25,
                    10.5,
                    10.7,
                    12.0,
                    14.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-A-H",
                "heating_power_kw": [
                    6.0,
                    8.0,
                    11.0,
                    12.0,
                    14.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-14-IR-TP120",
                "heating_power_kw": [
                    4.8,
                    7.2,
                    7.42,
                    9.0,
                    10.17,
                    11.92,
                    12.0,
                    12.45,
                    14.0,
                    14.5,
                    16.0,
                    17.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-6-IR-TP120",
                "heating_power_kw": [
                    2.96,
                    3.2,
                    3.9,
                    4.83,
                    5.7,
                    6.0,
                    6.18,
                    6.71,
                    7.6,
                    9.0,
                    12.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-8-IR-TP120",
                "heating_power_kw": [
                    3.32,
                    3.6,
                    5.04,
                    6.32,
                    8.0,
                    8.2,
                    8.43,
                    9.0,
                    9.25,
                    10.7,
                    12.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-B-W-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.0,
                    5.48,
                    5.5,
                    6.0,
                    6.15,
                    7.57,
                    12.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-E-W-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.0,
                    5.48,
                    5.5,
                    6.0,
                    6.15,
                    7.57,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-T190-W-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.0,
                    5.48,
                    5.5,
                    6.0,
                    6.15,
                    7.57,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-4-AR-TP120-W-S-plus",
                "heating_power_kw": [
                    2.53,
                    2.82,
                    3.2,
                    4.0,
                    4.24,
                    4.44,
                    4.76,
                    4.99,
                    5.0,
                    5.48,
                    5.5,
                    6.0,
                    6.15,
                    7.57,
                    9.0,
                    12.0,
                    21.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-B-W-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.0,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.91,
                    12.0,
                    25.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-E-W-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.0,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.91,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-T190-W-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.0,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.91,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-TP120-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.0,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.91,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW196i-2-6-AR-TP120-W-S-plus",
                "heating_power_kw": [
                    2.54,
                    3.6,
                    4.0,
                    4.01,
                    5.66,
                    6.0,
                    6.2,
                    6.79,
                    7.29,
                    7.3,
                    7.39,
                    7.91,
                    9.0,
                    12.0,
                    73.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-16-IPC",
                "heating_power_kw": [
                    12.0,
                    13.9,
                    16.0,
                    35.0,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-19-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    16.9,
                    35.0,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-24-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    24.0,
                    30.9,
                    35.0,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-24-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    20.8,
                    35.0,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-24",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    24.0,
                    30.9,
                    35.0,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-31-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    31.0,
                    35.0,
                    47.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-31-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    26.5,
                    35.0,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-31",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    31.0,
                    35.0,
                    47.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-36-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    36.0,
                    47.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-36-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    30.3,
                    35.0,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-36",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    36.0,
                    47.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-41-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    41.0,
                    52.1,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-41-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    35.8,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-41",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    41.0,
                    52.1,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-53-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    48.2,
                    53.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-53-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    48.2,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-53",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    48.2,
                    53.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-53-P",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    48.2,
                    53.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-53-V",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    48.2,
                    53.5,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-59-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    52.4,
                    58.2,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-59-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    52.4,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-59",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    52.4,
                    58.2,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-59-P",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    52.4,
                    58.2,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-59-V",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    52.4,
                    58.2,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-75-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    63.4,
                    65.5,
                    70.4,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-75-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    63.4,
                    65.5,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-75",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    63.4,
                    65.5,
                    70.4,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-75-P",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    63.4,
                    65.5,
                    70.4,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-75-V",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    63.4,
                    65.5,
                    70.4,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-89-IP",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    65.5,
                    82.8,
                    89.0,
                    92.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-89-IPC",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    65.5,
                    82.8,
                    89.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-89",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    65.5,
                    82.8,
                    89.0,
                    92.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-89-P",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    65.5,
                    82.8,
                    89.0,
                    92.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW276-89-V",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    35.0,
                    65.5,
                    82.8,
                    89.0,
                    92.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW286-22-A",
                "heating_power_kw": [
                    4.5,
                    12.0,
                    14.1,
                    22.0,
                    22.3,
                    38.0,
                    50.0,
                    150.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW286",
                "heating_power_kw": [
                    2.5,
                    4.0,
                    6.0,
                    9.0,
                    12.0,
                    22.3
                ],
                "scop": 4.0,
                "max_flow_temp": 60,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WLW286-38-A",
                "heating_power_kw": [
                    12.0,
                    22.0,
                    26.6,
                    38.0,
                    50.0,
                    150.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-10-1",
                "heating_power_kw": [
                    2.18,
                    9.0,
                    10.0,
                    10.4,
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-10-K-1",
                "heating_power_kw": [
                    1.0,
                    4.1,
                    4.8,
                    9.0,
                    10.0,
                    10.4,
                    11.0,
                    12.0,
                    17.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-13-1",
                "heating_power_kw": [
                    2.75,
                    9.0,
                    12.0,
                    12.8,
                    13.0,
                    13.1,
                    13.3,
                    14.0,
                    50.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-17-1",
                "heating_power_kw": [
                    3.63,
                    9.0,
                    12.0,
                    16.1,
                    17.0,
                    18.0,
                    19.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-6-1",
                "heating_power_kw": [
                    1.35,
                    5.6,
                    5.8,
                    6.0,
                    7.0,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-6-K-1",
                "heating_power_kw": [
                    1.0,
                    2.5,
                    4.8,
                    5.6,
                    5.8,
                    6.0,
                    9.0,
                    10.0,
                    12.0,
                    17.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-8-1",
                "heating_power_kw": [
                    3.0,
                    7.0,
                    7.3,
                    7.4,
                    7.6,
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPS-8-K-1",
                "heating_power_kw": [
                    1.0,
                    3.0,
                    4.8,
                    7.3,
                    7.6,
                    8.0,
                    9.0,
                    10.0,
                    12.0,
                    17.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPT200-4-A",
                "heating_power_kw": [
                    1.5,
                    2.1,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPT200-4-AS",
                "heating_power_kw": [
                    1.5,
                    2.1,
                    2.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPT260-4-A",
                "heating_power_kw": [
                    1.5,
                    2.1,
                    2.6,
                    12.0,
                    20.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WPT260-4-AS",
                "heating_power_kw": [
                    1.5,
                    2.1,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-12",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    12.0,
                    12.53
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-16",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-6",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.85,
                    6.0,
                    9.0,
                    12.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-8",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-12-T180",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    12.0,
                    12.53,
                    17.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-6-T180",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.85,
                    6.0,
                    9.0,
                    12.0,
                    17.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-8-T180",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0,
                    17.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-12-TP50",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    12.0,
                    12.53
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-16-TP50",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-6-TP50",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.85,
                    6.0,
                    9.0,
                    12.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-8-TP50",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW186i-16-T180",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    14.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-6",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.85,
                    6.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-8",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-12",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    12.0,
                    12.53,
                    16.0,
                    50.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-16",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-12-T180",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    12.0,
                    12.53,
                    16.0,
                    17.0,
                    50.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-6-T180",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.85,
                    6.0,
                    9.0,
                    12.0,
                    16.0,
                    17.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-8-T180",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0,
                    16.0,
                    17.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-12-TP50",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    12.0,
                    12.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-16-TP50",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-6-TP50",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.85,
                    6.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-8-TP50",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-12-T180W",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    11.0,
                    12.0,
                    12.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-12-TP50-W",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    11.0,
                    12.0,
                    12.53,
                    13.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-12W",
                "heating_power_kw": [
                    1.3,
                    4.88,
                    6.0,
                    9.0,
                    11.0,
                    12.0,
                    12.53,
                    13.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-16-T180",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    14.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-16-T180W",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    14.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-16-TP50-W",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    14.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-16W",
                "heating_power_kw": [
                    1.26,
                    4.8,
                    6.0,
                    9.0,
                    12.0,
                    14.0,
                    15.0,
                    15.53,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-6-T180W",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.0,
                    5.85,
                    6.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-6-TP50-W",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.0,
                    5.85,
                    6.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-6W",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    5.0,
                    5.85,
                    6.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-8-T180W",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-8-TP50-W",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "WSW196i-2-8W",
                "heating_power_kw": [
                    0.74,
                    2.67,
                    6.0,
                    7.0,
                    7.61,
                    8.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 5.55,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8718592384",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            }
        ],
        "Sole-Wasser-Wärmepumpe": [
            {
                "model": "Logatherm WSW196i T",
                "heating_power_kw": [
                    6.0,
                    9.0,
                    12.0,
                    15.0,
                    19.0
                ],
                "scop": 5.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [
                    "Erdwärmesonden",
                    "Inverter",
                    "Kühlung"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.7,
                "awards": [
                    "Empfohlen von Experten"
                ]
            },
            {
                "model": "Logatherm WSW186i T",
                "heating_power_kw": [
                    5.0,
                    8.0,
                    11.0,
                    14.0
                ],
                "scop": 4.8,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [
                    "Erdwärmesonden",
                    "Erdwärmekollektor"
                ],
                "refrigerant": "R32",
                "rating": 4.4,
                "awards": []
            }
        ],
        "Wasser-Wasser-Wärmepumpe": [
            {
                "model": "Logatherm WWW196i",
                "heating_power_kw": [
                    10.0,
                    14.0,
                    18.0,
                    23.0
                ],
                "scop": 5.3,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": [
                    "Grundwasser",
                    "Höchste Effizienz",
                    "Smart Home"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.9,
                "awards": [
                    "Effizienz-Champion"
                ]
            }
        ]
    },
    "Vaillant": {
        "Luft-Wasser-Wärmepumpe": [
            {
                "model": "aroTHERM plus",
                "heating_power_kw": [
                    5.0,
                    7.0,
                    10.0,
                    12.0,
                    15.0
                ],
                "scop": 4.7,
                "max_flow_temp": 75,
                "price_range": "€€€",
                "features": [
                    "R290 Naturkältemittel",
                    "myVAILLANT App",
                    "Active Cooling"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.8,
                "awards": [
                    "Öko-Testsieger",
                    "Design Award"
                ]
            },
            {
                "model": "aroTHERM split",
                "heating_power_kw": [
                    3.0,
                    5.0,
                    7.0,
                    10.0,
                    12.0
                ],
                "scop": 4.6,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": [
                    "Split-Gerät",
                    "Flüsterleise",
                    "myVAILLANT"
                ],
                "refrigerant": "R32",
                "rating": 4.6,
                "awards": [
                    "Leise-Testsieger"
                ]
            },
            {
                "model": "flexoTHERM exclusive",
                "heating_power_kw": [
                    5.0,
                    8.0,
                    11.0,
                    15.0
                ],
                "scop": 4.5,
                "max_flow_temp": 75,
                "price_range": "€€€",
                "features": [
                    "Hybrid Ready",
                    "Premium Design",
                    "Active Cooling"
                ],
                "refrigerant": "R32",
                "rating": 4.5,
                "awards": [
                    "Premium Qualität"
                ]
            },
            {
                "model": "aroTHERM compact",
                "heating_power_kw": [
                    7.0,
                    10.0,
                    12.0
                ],
                "scop": 4.3,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [
                    "Kompakt",
                    "Platzsparend",
                    "Easy Installation"
                ],
                "refrigerant": "R32",
                "rating": 4.1,
                "awards": []
            },
            {
                "model": "000376",
                "heating_power_kw": [
                    12.0,
                    21.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020205774",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020250220",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020250219",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020205412",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020229713",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "aroSTOR-plus",
                "heating_power_kw": [
                    0.79,
                    1.2,
                    1.27,
                    1.54,
                    12.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-185-3-AS",
                "heating_power_kw": [
                    3.3,
                    3.6,
                    4.2,
                    7.0,
                    12.0,
                    18.0,
                    18.1,
                    18.9,
                    20.1,
                    21.1,
                    26.5,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-255-3-AS",
                "heating_power_kw": [
                    3.3,
                    3.5,
                    4.2,
                    7.0,
                    12.0,
                    18.0,
                    26.0,
                    27.3,
                    28.0,
                    30.6,
                    35.0,
                    37.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010021120",
                "heating_power_kw": [
                    2.0,
                    2.7,
                    3.0,
                    4.6,
                    5.3,
                    5.8,
                    7.3,
                    8.1,
                    8.7,
                    9.2,
                    9.6,
                    10.0,
                    10.9,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010036237",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.3,
                    5.5,
                    5.8,
                    8.1,
                    8.5,
                    8.7,
                    9.0,
                    9.2,
                    10.9,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "aroTHERM-plus",
                "heating_power_kw": [
                    1.08,
                    4.46,
                    5.69,
                    8.0,
                    10.0,
                    10.58,
                    12.0,
                    14.4,
                    18.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010021122",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.7,
                    5.9,
                    8.1,
                    8.5,
                    8.8,
                    10.8,
                    11.4,
                    12.0,
                    12.2,
                    14.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010036238",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.5,
                    5.7,
                    5.9,
                    8.5,
                    8.8,
                    9.0,
                    10.8,
                    12.0,
                    12.2,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010021116",
                "heating_power_kw": [
                    2.0,
                    2.2,
                    3.3,
                    3.4,
                    3.6,
                    3.9,
                    3.95,
                    4.0,
                    4.5,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010036234",
                "heating_power_kw": [
                    2.0,
                    2.2,
                    3.3,
                    3.4,
                    3.6,
                    3.9,
                    4.5,
                    4.8,
                    5.3,
                    5.5,
                    8.5,
                    9.0,
                    12.0,
                    18.0,
                    35.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010021117",
                "heating_power_kw": [
                    2.0,
                    2.6,
                    3.4,
                    3.5,
                    3.9,
                    4.5,
                    4.8,
                    5.3,
                    5.4,
                    5.8,
                    6.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010036235",
                "heating_power_kw": [
                    2.0,
                    2.6,
                    3.4,
                    3.5,
                    3.9,
                    4.5,
                    4.8,
                    5.3,
                    5.4,
                    5.5,
                    8.5,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010021118",
                "heating_power_kw": [
                    2.8,
                    3.1,
                    4.1,
                    4.6,
                    4.8,
                    5.2,
                    5.6,
                    6.4,
                    7.0,
                    7.6,
                    8.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010036236",
                "heating_power_kw": [
                    2.8,
                    3.1,
                    4.1,
                    4.6,
                    4.8,
                    5.2,
                    5.5,
                    6.4,
                    7.0,
                    8.5,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "aroTHERM-Split-plus-VWL-35",
                "heating_power_kw": [
                    3.0,
                    3.55,
                    5.0,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "aroTHERM-Split-plus-VWL-55",
                "heating_power_kw": [
                    3.0,
                    4.89,
                    5.0,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "aroTHERM-Split-plus-VWL-75",
                "heating_power_kw": [
                    3.0,
                    5.0,
                    5.4,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-125-5-AS",
                "heating_power_kw": [
                    1.0,
                    2.45,
                    3.64,
                    4.0,
                    4.54,
                    4.92,
                    5.71,
                    8.23,
                    8.5,
                    10.25,
                    11.8,
                    12.0,
                    12.78,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-35-5-AS",
                "heating_power_kw": [
                    1.0,
                    2.46,
                    3.05,
                    3.11,
                    3.13,
                    3.56,
                    3.75,
                    4.0,
                    4.83,
                    4.89,
                    5.64,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-55-5-AS",
                "heating_power_kw": [
                    1.0,
                    2.67,
                    3.04,
                    3.37,
                    3.67,
                    4.0,
                    4.42,
                    4.68,
                    4.83,
                    4.88,
                    5.43,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-75-5-AS",
                "heating_power_kw": [
                    1.0,
                    2.64,
                    3.68,
                    3.87,
                    4.0,
                    4.51,
                    4.58,
                    5.24,
                    5.78,
                    6.3,
                    6.68,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8000034652",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010029009",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020205773",
                "heating_power_kw": [
                    12.0,
                    24.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWH-B-150-1",
                "heating_power_kw": [
                    1.0,
                    1.5,
                    1.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWH-B-200-1",
                "heating_power_kw": [
                    1.2,
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWH-B-270-1",
                "heating_power_kw": [
                    1.2,
                    1.5,
                    2.6,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020252090",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020252091",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020250226",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010029010",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-118-4",
                "heating_power_kw": [
                    3.0,
                    3.4,
                    3.83,
                    4.8,
                    8.4,
                    9.0,
                    10.27,
                    12.0,
                    12.1,
                    12.12,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-58-4",
                "heating_power_kw": [
                    3.3,
                    4.14,
                    4.3,
                    4.4,
                    4.94,
                    5.63,
                    6.42,
                    6.6,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-88-4",
                "heating_power_kw": [
                    3.2,
                    3.91,
                    4.74,
                    6.5,
                    7.8,
                    8.6,
                    8.98,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-117-4",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    9.0,
                    11.18,
                    11.33,
                    12.0,
                    35.0,
                    55.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-157-4",
                "heating_power_kw": [
                    3.14,
                    4.69,
                    9.0,
                    12.0,
                    14.39,
                    14.65,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-197-4",
                "heating_power_kw": [
                    3.18,
                    4.54,
                    9.0,
                    12.0,
                    19.62,
                    19.94,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-57-4",
                "heating_power_kw": [
                    2.89,
                    4.41,
                    5.28,
                    5.34,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWF-87-4",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    8.82,
                    8.94,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWS-260-3-S1",
                "heating_power_kw": [
                    2.8,
                    4.4,
                    12.0,
                    35.0,
                    55.0,
                    78.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWS-400-3-S1",
                "heating_power_kw": [
                    3.0,
                    4.7,
                    12.0,
                    35.0,
                    55.0,
                    78.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWS-780-3-S1",
                "heating_power_kw": [
                    2.8,
                    4.4,
                    12.0,
                    35.0,
                    55.0,
                    78.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Hydraulikstation",
                "heating_power_kw": [
                    7.0,
                    8.55,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020212718",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020212716",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020212717",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020212715",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020087227",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020115490",
                "heating_power_kw": [
                    12.0,
                    19.0,
                    27.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020087831",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020115491",
                "heating_power_kw": [
                    12.0,
                    19.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020205408",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "307591",
                "heating_power_kw": [
                    12.0,
                    27.0,
                    50.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020269259",
                "heating_power_kw": [
                    12.0,
                    27.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8000034640",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020205775",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "aroTHERM-plus-Paket",
                "heating_power_kw": [
                    1.08,
                    2.0,
                    3.4,
                    4.26,
                    4.46,
                    6.79,
                    12.0,
                    18.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020212521",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020003518",
                "heating_power_kw": [
                    12.0,
                    23.6
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020087826",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020112803",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010016721",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010016722",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020257890",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "2-33",
                "heating_power_kw": [
                    12.0,
                    21.3,
                    22.0,
                    22.4,
                    22.9,
                    23.5,
                    65.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "2-34",
                "heating_power_kw": [
                    12.0,
                    21.3,
                    22.0,
                    22.4,
                    22.9,
                    23.5,
                    65.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "2-35",
                "heating_power_kw": [
                    12.0,
                    21.3,
                    22.0,
                    22.4,
                    22.9,
                    23.5,
                    65.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "2-36",
                "heating_power_kw": [
                    12.0,
                    21.3,
                    22.0,
                    22.4,
                    22.9,
                    23.5,
                    65.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3-49",
                "heating_power_kw": [
                    12.0,
                    14.7,
                    15.75,
                    15.8,
                    35.0,
                    70.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "3-50",
                "heating_power_kw": [
                    12.0,
                    14.7,
                    15.75,
                    15.8,
                    35.0,
                    70.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0101",
                "heating_power_kw": [
                    1.0,
                    3.11,
                    3.75,
                    4.0,
                    4.89,
                    5.64,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0102",
                "heating_power_kw": [
                    1.0,
                    2.67,
                    3.67,
                    4.0,
                    4.68,
                    5.43,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0103",
                "heating_power_kw": [
                    1.0,
                    2.64,
                    3.68,
                    4.0,
                    4.58,
                    5.24,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0105",
                "heating_power_kw": [
                    1.0,
                    2.45,
                    3.64,
                    4.0,
                    4.54,
                    4.92,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0201",
                "heating_power_kw": [
                    1.0,
                    3.11,
                    3.75,
                    4.0,
                    4.89,
                    5.64,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0202",
                "heating_power_kw": [
                    1.0,
                    2.67,
                    3.67,
                    4.0,
                    4.68,
                    5.43,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0203",
                "heating_power_kw": [
                    1.0,
                    2.64,
                    3.68,
                    4.0,
                    4.58,
                    5.24,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0205",
                "heating_power_kw": [
                    1.0,
                    2.45,
                    3.64,
                    4.0,
                    4.54,
                    4.92,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0206",
                "heating_power_kw": [
                    0.71,
                    3.0,
                    3.54,
                    3.55,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0207",
                "heating_power_kw": [
                    0.92,
                    3.0,
                    4.51,
                    4.89,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0208",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    5.0,
                    5.07,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0213",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    5.0,
                    5.07,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-024",
                "heating_power_kw": [
                    1.0,
                    2.5,
                    3.1,
                    3.6,
                    4.0,
                    5.5,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-025",
                "heating_power_kw": [
                    1.0,
                    3.4,
                    4.0,
                    4.4,
                    4.9,
                    5.5,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-026",
                "heating_power_kw": [
                    1.0,
                    4.0,
                    4.5,
                    5.5,
                    5.8,
                    6.7,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-028",
                "heating_power_kw": [
                    1.0,
                    4.0,
                    8.2,
                    8.5,
                    10.3,
                    11.8,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0307",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    3.54,
                    5.0,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0308",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    4.51,
                    5.0,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0309",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    5.0,
                    5.07,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0310",
                "heating_power_kw": [
                    0.71,
                    3.0,
                    3.54,
                    3.55,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0311",
                "heating_power_kw": [
                    0.92,
                    3.0,
                    4.51,
                    4.89,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0312",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    5.0,
                    5.07,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0313",
                "heating_power_kw": [
                    0.71,
                    3.0,
                    3.54,
                    3.55,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0314",
                "heating_power_kw": [
                    0.92,
                    3.0,
                    4.51,
                    4.89,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0315",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    5.0,
                    5.07,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0401",
                "heating_power_kw": [
                    0.71,
                    3.0,
                    3.54,
                    3.55,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0402",
                "heating_power_kw": [
                    0.92,
                    3.0,
                    4.51,
                    4.89,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0403",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    5.0,
                    5.07,
                    5.4,
                    5.42,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-050",
                "heating_power_kw": [
                    2.0,
                    2.2,
                    3.3,
                    3.6,
                    3.9,
                    4.3,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0501",
                "heating_power_kw": [
                    1.0,
                    2.64,
                    3.68,
                    4.0,
                    4.58,
                    5.24,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-0503",
                "heating_power_kw": [
                    1.0,
                    2.45,
                    3.64,
                    4.0,
                    4.54,
                    4.92,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0505",
                "heating_power_kw": [
                    0.71,
                    3.0,
                    3.55,
                    5.0,
                    5.07,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0506",
                "heating_power_kw": [
                    0.92,
                    3.0,
                    4.89,
                    5.0,
                    5.07,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-0507",
                "heating_power_kw": [
                    0.98,
                    3.0,
                    5.0,
                    5.07,
                    5.4,
                    6.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-051",
                "heating_power_kw": [
                    2.0,
                    2.6,
                    3.4,
                    3.9,
                    4.3,
                    4.8,
                    5.3,
                    5.4,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-052",
                "heating_power_kw": [
                    3.1,
                    4.6,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-053",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.3,
                    5.8,
                    6.0,
                    8.1,
                    9.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-054",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.7,
                    5.9,
                    8.5,
                    12.0,
                    12.2,
                    18.0,
                    35.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-065",
                "heating_power_kw": [
                    1.0,
                    2.5,
                    3.1,
                    3.6,
                    4.0,
                    5.5,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-066",
                "heating_power_kw": [
                    1.0,
                    3.4,
                    4.0,
                    4.4,
                    4.9,
                    5.5,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-067",
                "heating_power_kw": [
                    1.0,
                    4.0,
                    4.5,
                    5.5,
                    5.8,
                    6.7,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-069",
                "heating_power_kw": [
                    1.0,
                    4.0,
                    8.2,
                    8.5,
                    10.3,
                    11.8,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-301",
                "heating_power_kw": [
                    2.0,
                    2.2,
                    3.3,
                    3.6,
                    3.9,
                    4.3,
                    4.8,
                    5.3,
                    5.5,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3104",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.7,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3106",
                "heating_power_kw": [
                    2.2,
                    3.9,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    21.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3107",
                "heating_power_kw": [
                    2.6,
                    3.9,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    35.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3108",
                "heating_power_kw": [
                    2.8,
                    4.1,
                    4.8,
                    5.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-311",
                "heating_power_kw": [
                    2.0,
                    2.6,
                    3.4,
                    3.9,
                    4.3,
                    4.8,
                    5.3,
                    5.4,
                    5.5,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3110",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.7,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3202",
                "heating_power_kw": [
                    2.8,
                    4.1,
                    4.8,
                    5.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3206",
                "heating_power_kw": [
                    2.2,
                    3.9,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3207",
                "heating_power_kw": [
                    2.6,
                    3.9,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3208",
                "heating_power_kw": [
                    2.8,
                    4.1,
                    4.8,
                    5.2,
                    12.0,
                    18.0,
                    35.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3209",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-321",
                "heating_power_kw": [
                    3.1,
                    4.6,
                    5.5,
                    7.0,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3210",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.7,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3306",
                "heating_power_kw": [
                    0.69,
                    3.3,
                    3.6,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3307",
                "heating_power_kw": [
                    0.71,
                    3.4,
                    5.4,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3308",
                "heating_power_kw": [
                    0.96,
                    4.6,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3309",
                "heating_power_kw": [
                    1.53,
                    7.0,
                    8.1,
                    9.0,
                    9.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-331",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.3,
                    5.5,
                    5.8,
                    8.1,
                    8.5,
                    9.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3310",
                "heating_power_kw": [
                    1.57,
                    7.0,
                    8.5,
                    9.0,
                    12.0,
                    12.2,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3311",
                "heating_power_kw": [
                    0.69,
                    3.3,
                    3.6,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3312",
                "heating_power_kw": [
                    0.71,
                    3.4,
                    5.4,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3313",
                "heating_power_kw": [
                    0.96,
                    4.6,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3314",
                "heating_power_kw": [
                    1.53,
                    7.0,
                    8.1,
                    9.0,
                    9.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3315",
                "heating_power_kw": [
                    1.57,
                    7.0,
                    8.5,
                    9.0,
                    12.0,
                    12.2,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3316",
                "heating_power_kw": [
                    0.69,
                    3.3,
                    3.6,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3317",
                "heating_power_kw": [
                    0.71,
                    3.4,
                    5.4,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3318",
                "heating_power_kw": [
                    0.96,
                    4.6,
                    7.0,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3319",
                "heating_power_kw": [
                    1.53,
                    7.0,
                    8.1,
                    9.0,
                    9.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Paket-4-3320",
                "heating_power_kw": [
                    1.57,
                    7.0,
                    8.5,
                    9.0,
                    12.0,
                    12.2,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3402",
                "heating_power_kw": [
                    2.2,
                    3.9,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3403",
                "heating_power_kw": [
                    2.6,
                    3.9,
                    4.8,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3404",
                "heating_power_kw": [
                    1.5,
                    2.8,
                    3.0,
                    4.1,
                    4.8,
                    5.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3405",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3406",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.7,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-341",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.5,
                    5.7,
                    5.9,
                    6.0,
                    8.5,
                    12.0,
                    12.2,
                    18.0,
                    27.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3504",
                "heating_power_kw": [
                    2.8,
                    4.1,
                    4.8,
                    5.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3505",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.3,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3506",
                "heating_power_kw": [
                    2.7,
                    4.6,
                    5.4,
                    5.7,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-371",
                "heating_power_kw": [
                    3.1,
                    4.6,
                    5.5,
                    7.0,
                    8.5,
                    12.0,
                    18.0,
                    35.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3901",
                "heating_power_kw": [
                    3.1,
                    4.6,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-396",
                "heating_power_kw": [
                    1.0,
                    4.0,
                    4.51,
                    5.78,
                    6.68,
                    8.5,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-431",
                "heating_power_kw": [
                    2.89,
                    4.41,
                    5.3,
                    5.4,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-432",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    8.9,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-433",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    9.0,
                    11.2,
                    11.4,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-441",
                "heating_power_kw": [
                    3.2,
                    4.12,
                    4.14,
                    5.0,
                    5.3,
                    5.4,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-442",
                "heating_power_kw": [
                    3.12,
                    3.21,
                    3.91,
                    4.8,
                    8.9,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-443",
                "heating_power_kw": [
                    2.94,
                    3.28,
                    3.83,
                    4.9,
                    9.0,
                    11.2,
                    11.4,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-451",
                "heating_power_kw": [
                    2.94,
                    4.7,
                    5.3,
                    5.4,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-452",
                "heating_power_kw": [
                    3.47,
                    5.17,
                    8.9,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-453",
                "heating_power_kw": [
                    3.36,
                    5.22,
                    9.0,
                    11.2,
                    11.4,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6101",
                "heating_power_kw": [
                    2.89,
                    4.41,
                    5.3,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6102",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    8.9,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6103",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    9.0,
                    11.2,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6104",
                "heating_power_kw": [
                    2.89,
                    4.4,
                    4.41,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6105",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    6.5,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6106",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    8.4,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6107",
                "heating_power_kw": [
                    2.89,
                    4.41,
                    6.4,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6108",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    9.0,
                    10.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6109",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    9.0,
                    12.0,
                    12.9,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6201",
                "heating_power_kw": [
                    2.89,
                    4.41,
                    5.3,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6202",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    8.9,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6203",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    9.0,
                    11.2,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6204",
                "heating_power_kw": [
                    2.89,
                    4.4,
                    4.41,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6205",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    6.5,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6206",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    8.4,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6207",
                "heating_power_kw": [
                    2.89,
                    4.41,
                    6.4,
                    9.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6208",
                "heating_power_kw": [
                    3.22,
                    4.84,
                    9.0,
                    10.0,
                    12.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6209",
                "heating_power_kw": [
                    3.1,
                    4.77,
                    9.0,
                    12.0,
                    12.9,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "flexoTHERM-exclusive-VWF-57",
                "heating_power_kw": [
                    1.2,
                    5.0,
                    5.28,
                    9.0,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "flexoTHERM-exclusive-VWF-87",
                "heating_power_kw": [
                    1.82,
                    8.0,
                    8.82,
                    9.0,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "flexoTHERM-exclusive-VWF-117",
                "heating_power_kw": [
                    2.34,
                    9.0,
                    11.0,
                    11.18,
                    12.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6501",
                "heating_power_kw": [
                    3.14,
                    4.69,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-6502",
                "heating_power_kw": [
                    3.18,
                    4.54,
                    9.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3103",
                "heating_power_kw": [
                    3.1,
                    4.2,
                    4.46,
                    5.17,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-3105",
                "heating_power_kw": [
                    2.7,
                    3.72,
                    4.1,
                    5.08,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-914",
                "heating_power_kw": [
                    3.1,
                    4.2,
                    4.46,
                    5.17,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-915",
                "heating_power_kw": [
                    2.9,
                    4.2,
                    4.46,
                    5.17,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-916",
                "heating_power_kw": [
                    2.7,
                    3.72,
                    4.1,
                    5.08,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-9200",
                "heating_power_kw": [
                    1.0,
                    3.1,
                    4.0,
                    4.04,
                    4.46,
                    5.17,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-9201",
                "heating_power_kw": [
                    1.0,
                    2.86,
                    4.0,
                    4.04,
                    4.46,
                    5.17,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "4-9202",
                "heating_power_kw": [
                    1.0,
                    2.72,
                    3.72,
                    4.0,
                    4.02,
                    5.08,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020087224",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020087225",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020087226",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020269273",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-39-5",
                "heating_power_kw": [
                    1.0,
                    2.85,
                    3.1,
                    3.26,
                    3.68,
                    4.0,
                    4.04,
                    4.46,
                    4.85,
                    4.92,
                    5.17,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-59-5",
                "heating_power_kw": [
                    1.0,
                    2.85,
                    2.86,
                    3.1,
                    3.26,
                    4.0,
                    4.04,
                    4.46,
                    4.85,
                    4.92,
                    5.17,
                    5.4,
                    5.73,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-79-5",
                "heating_power_kw": [
                    1.0,
                    2.72,
                    3.55,
                    3.72,
                    4.0,
                    4.02,
                    4.14,
                    5.08,
                    5.4,
                    5.77,
                    6.15,
                    7.0,
                    7.24,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020191788",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020191814",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020191813",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020191817",
                "heating_power_kw": [
                    12.0,
                    27.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020252903",
                "heating_power_kw": [
                    12.0,
                    16.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020115870",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Set-aroTHERM-plus",
                "heating_power_kw": [
                    5.69,
                    8.0,
                    10.58,
                    12.0,
                    14.4,
                    18.0,
                    35.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 75,
                "price_range": "€€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "Set-aroTHERM-Split-plus",
                "heating_power_kw": [
                    0.71,
                    3.0,
                    3.54,
                    3.55,
                    5.0,
                    5.4,
                    5.42,
                    7.0,
                    12.0,
                    18.0,
                    35.0,
                    45.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 62,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "000474",
                "heating_power_kw": [
                    2.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "000473",
                "heating_power_kw": [
                    6.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8000035192",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020093781",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020147182",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020060434",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020059561",
                "heating_power_kw": [
                    11.0,
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "uniTOWER-plus-VIH-QW-190-E",
                "heating_power_kw": [
                    9.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "uniTOWER-plus",
                "heating_power_kw": [
                    8.55,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "uniTOWER-VWL-128-IS",
                "heating_power_kw": [
                    6.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "uniTOWER-VWL-58-IS",
                "heating_power_kw": [
                    5.4,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "uniTOWER-VWL-78-IS",
                "heating_power_kw": [
                    6.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "uniTOWER-VWL-78-IS-C2",
                "heating_power_kw": [
                    5.4,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020170505",
                "heating_power_kw": [
                    2.0,
                    12.0,
                    27.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-37-5",
                "heating_power_kw": [
                    2.85,
                    3.1,
                    3.18,
                    3.6,
                    4.2,
                    4.46,
                    4.85,
                    4.92,
                    5.17,
                    5.4,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-57-5",
                "heating_power_kw": [
                    2.85,
                    2.9,
                    3.1,
                    3.18,
                    4.2,
                    4.46,
                    4.85,
                    4.92,
                    5.17,
                    5.4,
                    5.65,
                    7.0,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-77-5",
                "heating_power_kw": [
                    2.7,
                    3.55,
                    3.72,
                    4.1,
                    5.08,
                    5.4,
                    5.77,
                    6.15,
                    7.0,
                    7.2,
                    12.0,
                    18.0,
                    35.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "307556",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "307597",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020213871",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "306787",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010016715",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010016719",
                "heating_power_kw": [
                    11.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010016720",
                "heating_power_kw": [
                    12.0,
                    19.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020129148",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020136828",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020022302",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020022301",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020145030",
                "heating_power_kw": [
                    6.0,
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020143800",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020221248",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020212523",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020106265",
                "heating_power_kw": [
                    6.0,
                    12.0,
                    38.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "8000035574",
                "heating_power_kw": [
                    12.0,
                    63.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020250224",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020250225",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0010029007",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-B-200-5",
                "heating_power_kw": [
                    1.2,
                    1.22,
                    1.5,
                    2.6,
                    3.19,
                    3.57,
                    12.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-B-270-5",
                "heating_power_kw": [
                    1.19,
                    1.2,
                    1.44,
                    1.5,
                    2.6,
                    3.14,
                    3.58,
                    12.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-BM-200-5",
                "heating_power_kw": [
                    1.2,
                    1.26,
                    1.47,
                    1.5,
                    2.6,
                    2.99,
                    3.47,
                    12.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "VWL-BM-270-5",
                "heating_power_kw": [
                    1.2,
                    1.24,
                    1.39,
                    1.5,
                    2.6,
                    3.0,
                    3.53,
                    12.0,
                    55.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020022303",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020112792",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020112793",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020229714",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020170503",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020170502",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            },
            {
                "model": "0020220369",
                "heating_power_kw": [
                    12.0
                ],
                "scop": 4.0,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": [],
                "refrigerant": "",
                "rating": 0.0,
                "awards": []
            }
        ],
        "Sole-Wasser-Wärmepumpe": [
            {
                "model": "flexoTHERM exclusive VWF",
                "heating_power_kw": [
                    5.0,
                    8.0,
                    11.0,
                    14.0,
                    19.0,
                    24.0
                ],
                "scop": 5.2,
                "max_flow_temp": 75,
                "price_range": "€€€€",
                "features": [
                    "Erdwärmesonden",
                    "Erdkollektor",
                    "Natural Cooling"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 4.9,
                "awards": [
                    "Premium Erdwärmepumpe"
                ]
            },
            {
                "model": "flexoTHERM compact VWF",
                "heating_power_kw": [
                    6.0,
                    9.0,
                    12.0,
                    16.0
                ],
                "scop": 4.9,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": [
                    "Erdwärmesonden",
                    "Kompakt-Bauweise"
                ],
                "refrigerant": "R32",
                "rating": 4.5,
                "awards": []
            }
        ],
        "Wasser-Wasser-Wärmepumpe": [
            {
                "model": "flexoTHERM exclusive VWW",
                "heating_power_kw": [
                    9.0,
                    13.0,
                    17.0,
                    22.0,
                    27.0
                ],
                "scop": 5.5,
                "max_flow_temp": 75,
                "price_range": "€€€€",
                "features": [
                    "Grundwasser",
                    "Höchste Effizienz",
                    "Natural Cooling"
                ],
                "refrigerant": "R290 (Propan)",
                "rating": 5.0,
                "awards": [
                    "Beste Wasser-Wasser WP 2024"
                ]
            }
        ]
    }
}


def get_heatpump_models(manufacturer: str, heatpump_type: str) -> list[dict]:
    """
    Gibt alle Modelle einer bestimmten Marke und eines bestimmten Typs zurück
    NUR PRODUKTE DIE IN DER ECHTEN PRODUKTDATENBANK EXISTIEREN!
    
    Args:
        manufacturer: Hersteller-Name ("Viessmann", "Buderus", "Vaillant")
        heatpump_type: Typ der Wärmepumpe
        
    Returns:
        Liste von Modell-Dictionaries (nur Produkte aus product_db.py)
    """
    if manufacturer not in HEATPUMP_PRODUCTS:
        return []
    
    if heatpump_type not in HEATPUMP_PRODUCTS[manufacturer]:
        return []
    
    # VALIDIERE GEGEN ECHTE PRODUKTDATENBANK
    try:
        from product_db import get_product_by_model_name
        
        validated_models = []
        for model in HEATPUMP_PRODUCTS[manufacturer][heatpump_type]:
            model_name = model.get("model", "")
            # Prüfe ob Produkt in echter Datenbank existiert
            db_product = get_product_by_model_name(model_name)
            if db_product is not None:
                # Produkt existiert in Datenbank
                validated_models.append(model)
            # Sonst: Überspringen (Fake-Produkt)
        
        return validated_models
    except Exception as e:
        # Fallback: Bei Fehler alle zurückgeben (aber mit Warnung)
        print(f"WARNUNG: Konnte Produktdatenbank nicht validieren: {e}")
        return HEATPUMP_PRODUCTS[manufacturer][heatpump_type]


def get_all_manufacturers() -> list[str]:
    """Gibt alle verfügbaren Hersteller zurück"""
    return list(HEATPUMP_PRODUCTS.keys())


def get_available_types_for_manufacturer(manufacturer: str) -> list[str]:
    """Gibt alle verfügbaren Wärmepumpentypen für einen Hersteller zurück"""
    if manufacturer not in HEATPUMP_PRODUCTS:
        return []
    return list(HEATPUMP_PRODUCTS[manufacturer].keys())


def find_suitable_model(
    manufacturer: str,
    heatpump_type: str,
    required_power_kw: float,
    max_flow_temp_required: int = 55
) -> dict | None:
    """
    Findet das passende Modell basierend auf Leistung und Vorlauftemperatur
    
    Args:
        manufacturer: Hersteller-Name
        heatpump_type: Typ der Wärmepumpe
        required_power_kw: Benötigte Heizleistung in kW
        max_flow_temp_required: Erforderliche max. Vorlauftemperatur
        
    Returns:
        Dict mit Modell-Informationen oder None
    """
    models = get_heatpump_models(manufacturer, heatpump_type)
    
    suitable_models = []
    for model in models:
        # Prüfe ob Vorlauftemperatur ausreichend
        if model["max_flow_temp"] < max_flow_temp_required:
            continue
            
        # Finde passende Leistungsvariante
        for power in model["heating_power_kw"]:
            if power >= required_power_kw:
                model_variant = model.copy()
                model_variant["selected_power_kw"] = power
                suitable_models.append(model_variant)
                break
    
    # Sortiere nach Leistung (kleinste passende zuerst)
    if suitable_models:
        suitable_models.sort(key=lambda x: x["selected_power_kw"])
        return suitable_models[0]
    
    return None


def get_model_details(manufacturer: str, heatpump_type: str, model_name: str) -> dict | None:
    """
    Gibt detaillierte Informationen zu einem spezifischen Modell zurück
    
    Args:
        manufacturer: Hersteller-Name
        heatpump_type: Typ der Wärmepumpe
        model_name: Modellbezeichnung
        
    Returns:
        Dict mit Modell-Details oder None
    """
    models = get_heatpump_models(manufacturer, heatpump_type)
    
    for model in models:
        if model["model"] == model_name:
            return model
    
    return None
