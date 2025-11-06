"""
Wärmepumpen-Produktdatenbank mit realen Modellen von Viessmann, Buderus und Vaillant
Stand: 2025
"""

HEATPUMP_PRODUCTS = {
    "Viessmann": {
        "Luft-Wasser-Wärmepumpe": [
            {
                "model": "Vitocal 250-A",
                "heating_power_kw": [6.0, 8.0, 10.0, 12.0, 15.0],
                "scop": 4.6,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": ["Smart Grid Ready", "Active Cooling", "Internet Gateway"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.8,
                "awards": ["Testsieger Stiftung Warentest 2024", "Öko-Test SEHR GUT"]
            },
            {
                "model": "Vitocal 200-A",
                "heating_power_kw": [6.0, 8.0, 10.0, 12.0],
                "scop": 4.5,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": ["Smart Grid Ready", "Active Cooling"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.5,
                "awards": ["Preis-Leistung Testsieger"]
            },
            {
                "model": "Vitocal 222-A",
                "heating_power_kw": [8.0, 11.0, 13.0, 16.0],
                "scop": 4.4,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": ["Kompakt-Bauweise", "Active Cooling"],
                "refrigerant": "R32",
                "rating": 4.3,
                "awards": []
            },
            {
                "model": "Vitocal 150-A",
                "heating_power_kw": [4.0, 6.0, 8.0],
                "scop": 4.3,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": ["Einfache Bedienung", "Platzsparend"],
                "refrigerant": "R32",
                "rating": 4.0,
                "awards": []
            }
        ],
        "Sole-Wasser-Wärmepumpe": [
            {
                "model": "Vitocal 300-G",
                "heating_power_kw": [6.0, 8.0, 10.0, 13.0, 17.0, 22.0],
                "scop": 5.1,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": ["Erdwärmesonden", "Erdwärmekollektor", "Smart Grid"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.9,
                "awards": ["Beste Erdwärmepumpe 2024"]
            },
            {
                "model": "Vitocal 200-G",
                "heating_power_kw": [5.0, 7.0, 10.0, 13.0],
                "scop": 4.9,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": ["Erdwärmesonden", "Erdwärmekollektor"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.6,
                "awards": []
            }
        ],
        "Wasser-Wasser-Wärmepumpe": [
            {
                "model": "Vitocal 350-G Pro",
                "heating_power_kw": [8.0, 12.0, 16.0, 21.0, 27.0],
                "scop": 5.4,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": ["Grundwasser-Nutzung", "Smart Grid", "Kühlfunktion"],
                "refrigerant": "R290 (Propan)",
                "rating": 5.0,
                "awards": ["Premium Testsieger 2024", "Höchste Effizienz"]
            }
        ]
    },
    "Buderus": {
        "Luft-Wasser-Wärmepumpe": [
            {
                "model": "Logatherm WLW196i AR",
                "heating_power_kw": [5.0, 7.0, 9.0, 11.0, 14.0, 17.0],
                "scop": 4.7,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": ["Inverter-Technologie", "Smart Home", "Active Cooling"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.7,
                "awards": ["Top-Produkt 2024"]
            },
            {
                "model": "Logatherm WLW186i AR",
                "heating_power_kw": [6.0, 8.0, 10.0, 13.0],
                "scop": 4.5,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": ["Inverter-Technologie", "Smart Home"],
                "refrigerant": "R32",
                "rating": 4.4,
                "awards": []
            },
            {
                "model": "Logatherm WLW176i AR",
                "heating_power_kw": [8.0, 11.0, 14.0],
                "scop": 4.4,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": ["Kompakt", "Split-Gerät möglich"],
                "refrigerant": "R32",
                "rating": 4.2,
                "awards": []
            },
            {
                "model": "Logatherm WLW166 AR E",
                "heating_power_kw": [5.0, 7.0, 9.0],
                "scop": 4.2,
                "max_flow_temp": 60,
                "price_range": "€",
                "features": ["Economy-Serie", "Einfache Installation"],
                "refrigerant": "R410A",
                "rating": 3.9,
                "awards": []
            }
        ],
        "Sole-Wasser-Wärmepumpe": [
            {
                "model": "Logatherm WSW196i T",
                "heating_power_kw": [6.0, 9.0, 12.0, 15.0, 19.0],
                "scop": 5.0,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": ["Erdwärmesonden", "Inverter", "Kühlung"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.7,
                "awards": ["Empfohlen von Experten"]
            },
            {
                "model": "Logatherm WSW186i T",
                "heating_power_kw": [5.0, 8.0, 11.0, 14.0],
                "scop": 4.8,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": ["Erdwärmesonden", "Erdwärmekollektor"],
                "refrigerant": "R32",
                "rating": 4.4,
                "awards": []
            }
        ],
        "Wasser-Wasser-Wärmepumpe": [
            {
                "model": "Logatherm WWW196i",
                "heating_power_kw": [10.0, 14.0, 18.0, 23.0],
                "scop": 5.3,
                "max_flow_temp": 70,
                "price_range": "€€€€",
                "features": ["Grundwasser", "Höchste Effizienz", "Smart Home"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.9,
                "awards": ["Effizienz-Champion"]
            }
        ]
    },
    "Vaillant": {
        "Luft-Wasser-Wärmepumpe": [
            {
                "model": "aroTHERM plus",
                "heating_power_kw": [5.0, 7.0, 10.0, 12.0, 15.0],
                "scop": 4.7,
                "max_flow_temp": 75,
                "price_range": "€€€",
                "features": ["R290 Naturkältemittel", "myVAILLANT App", "Active Cooling"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.8,
                "awards": ["Öko-Testsieger", "Design Award"]
            },
            {
                "model": "aroTHERM split",
                "heating_power_kw": [3.0, 5.0, 7.0, 10.0, 12.0],
                "scop": 4.6,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": ["Split-Gerät", "Flüsterleise", "myVAILLANT"],
                "refrigerant": "R32",
                "rating": 4.6,
                "awards": ["Leise-Testsieger"]
            },
            {
                "model": "flexoTHERM exclusive",
                "heating_power_kw": [5.0, 8.0, 11.0, 15.0],
                "scop": 4.5,
                "max_flow_temp": 75,
                "price_range": "€€€",
                "features": ["Hybrid Ready", "Premium Design", "Active Cooling"],
                "refrigerant": "R32",
                "rating": 4.5,
                "awards": ["Premium Qualität"]
            },
            {
                "model": "aroTHERM compact",
                "heating_power_kw": [7.0, 10.0, 12.0],
                "scop": 4.3,
                "max_flow_temp": 65,
                "price_range": "€",
                "features": ["Kompakt", "Platzsparend", "Easy Installation"],
                "refrigerant": "R32",
                "rating": 4.1,
                "awards": []
            }
        ],
        "Sole-Wasser-Wärmepumpe": [
            {
                "model": "flexoTHERM exclusive VWF",
                "heating_power_kw": [5.0, 8.0, 11.0, 14.0, 19.0, 24.0],
                "scop": 5.2,
                "max_flow_temp": 75,
                "price_range": "€€€€",
                "features": ["Erdwärmesonden", "Erdkollektor", "Natural Cooling"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.9,
                "awards": ["Premium Erdwärmepumpe"]
            },
            {
                "model": "flexoTHERM compact VWF",
                "heating_power_kw": [6.0, 9.0, 12.0, 16.0],
                "scop": 4.9,
                "max_flow_temp": 70,
                "price_range": "€€",
                "features": ["Erdwärmesonden", "Kompakt-Bauweise"],
                "refrigerant": "R32",
                "rating": 4.5,
                "awards": []
            }
        ],
        "Wasser-Wasser-Wärmepumpe": [
            {
                "model": "flexoTHERM exclusive VWW",
                "heating_power_kw": [9.0, 13.0, 17.0, 22.0, 27.0],
                "scop": 5.5,
                "max_flow_temp": 75,
                "price_range": "€€€€",
                "features": ["Grundwasser", "Höchste Effizienz", "Natural Cooling"],
                "refrigerant": "R290 (Propan)",
                "rating": 5.0,
                "awards": ["Beste Wasser-Wasser WP 2024"]
            }
        ]
    }
}


def get_heatpump_models(manufacturer: str, heatpump_type: str) -> list[dict]:
    """
    Gibt alle Modelle einer bestimmten Marke und eines bestimmten Typs zurück
    
    Args:
        manufacturer: Hersteller-Name ("Viessmann", "Buderus", "Vaillant")
        heatpump_type: Typ der Wärmepumpe
        
    Returns:
        Liste von Modell-Dictionaries
    """
    if manufacturer not in HEATPUMP_PRODUCTS:
        return []
    
    if heatpump_type not in HEATPUMP_PRODUCTS[manufacturer]:
        return []
    
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
