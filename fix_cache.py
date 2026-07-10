with open("calculations.py", "r") as f:
    content = f.read()

# Replace unbounded dictionary with functools.lru_cache on an inner function
# and use thread locking for the rate limit.

search = """_pvgis_cache = {}
_last_pvgis_call = 0.0
_MIN_PVGIS_INTERVAL = 1.0

def get_pvgis_data(
    latitude: float,
    longitude: float,
    peak_power_kwp: float,
    tilt: int,
    azimuth: int,
    system_loss_percent: float = 14.0,
    texts: dict[str, str] | None = None,
    errors_list: list[str] | None = None,
    debug_mode_enabled: bool = False) -> dict[str, Any] | None:
    \"\"\"Holt PV-Produktionsdaten von der PVGIS API.\"\"\"
    local_errors: list[str] = []  # Für interne Fehler dieser Funktion
    # Sicherstellen, dass texts ein Dict ist
    texts = texts if texts is not None else {}
    effective_errors_list = errors_list if errors_list is not None else local_errors

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

import threading
replace = """import threading
import copy

_last_pvgis_call = 0.0
_MIN_PVGIS_INTERVAL = 1.0
_pvgis_lock = threading.Lock()

@lru_cache(maxsize=100)
def _get_pvgis_data_cached(latitude: float, longitude: float, peak_power_kwp: float, tilt: int, azimuth: int, system_loss_percent: float) -> dict[str, Any] | None:
    # Inner cached function that actually calls the API
    global _last_pvgis_call

    with _pvgis_lock:
        elapsed = time.time() - _last_pvgis_call
        if elapsed < _MIN_PVGIS_INTERVAL:
            time.sleep(_MIN_PVGIS_INTERVAL - elapsed)
        _last_pvgis_call = time.time()

    base_url = "https://re.jrc.ec.europa.eu/api/PVcalc"
    params = {
        "lat": latitude,
        "lon": longitude,
        "peakpower": peak_power_kwp,
        "loss": system_loss_percent,
        "pvtechchoice": "crystSi",
        "mountingplace": "building",
        "angle": tilt,
        "aspect": azimuth,
        "outputformat": "json",
        "browser": 0,  # Wichtig, um HTML-Antworten zu vermeiden
    }

    error_msg_pvgis = ""  # Initialisiere Fehlermeldung

    try:
        response = requests.get(
            base_url, params=params, timeout=25
        )  # Timeout von 25 Sekunden

        response.raise_for_status()  # Löst HTTPError für 4xx/5xx Status Codes
        data = response.json()

        # In PVcalc API, 'monthly' is a dict containing 'fixed', which is a list.
        monthly_data = data.get("outputs", {}).get("monthly", {})
        if isinstance(monthly_data, dict) and "fixed" in monthly_data:
            monthly_list = monthly_data["fixed"]
        else:
            monthly_list = monthly_data if isinstance(monthly_data, list) else []

        monthly_production_kwh = [
            m.get("E_m", 0.0) for m in monthly_list
        ]

        annual_production_kwh = (
            data.get(
                "outputs",
                {}).get(
                "totals",
                {}).get(
                "fixed",
                {}).get(
                    "E_y",
                0.0))
        specific_yield_kwh_kwp_pa = (
            data.get("outputs", {})
            .get("totals", {})
            .get("fixed", {})
            .get("E_y", 0.0) / peak_power_kwp if peak_power_kwp > 0 else 0.0
        )  # PVcalc doesn't return Yield_y always

        if (
            not monthly_production_kwh
            or len(monthly_production_kwh) != 12
            or (annual_production_kwh == 0.0 and peak_power_kwp > 0)
        ):
            return {"error": "pvgis_incomplete_data"}

        result = {
            "monthly_production_kwh": monthly_production_kwh,
            "annual_production_kwh": annual_production_kwh,
            "specific_yield_kwh_kwp_pa": specific_yield_kwh_kwp_pa,
            "pvgis_source": data.get("meta", {}).get(
                "source", "PVGIS-TMY"
            ),  # Quelle der Daten (z.B. TMY, ERA5)
        }
        return result

    except requests.exceptions.HTTPError as e_http:
        status_code_val = (
            e_http.response.status_code if e_http.response is not None else "N/A")
        return {"error": "pvgis_http_error", "status_code": status_code_val}
    except requests.exceptions.Timeout:
        return {"error": "pvgis_timeout_error"}
    except requests.exceptions.ConnectionError as e_conn:
        return {"error": "pvgis_connection_error", "details": str(e_conn)}
    except requests.exceptions.RequestException as e_req:
        return {"error": "pvgis_request_error", "details": str(e_req)}
    except json.JSONDecodeError:
        return {"error": "pvgis_json_decode_error"}
    except Exception as e_pvgis_unknown:
        return {"error": "pvgis_unknown_error", "details": str(e_pvgis_unknown)}

    return None

def get_pvgis_data(
    latitude: float,
    longitude: float,
    peak_power_kwp: float,
    tilt: int,
    azimuth: int,
    system_loss_percent: float = 14.0,
    texts: dict[str, str] | None = None,
    errors_list: list[str] | None = None,
    debug_mode_enabled: bool = False) -> dict[str, Any] | None:
    \"\"\"Holt PV-Produktionsdaten von der PVGIS API.\"\"\"
    local_errors: list[str] = []  # Für interne Fehler dieser Funktion
    # Sicherstellen, dass texts ein Dict ist
    texts = texts if texts is not None else {}
    effective_errors_list = errors_list if errors_list is not None else local_errors"""

content = content.replace(search, replace)

# Delete the rest of get_pvgis_data logic that we've now refactored into the cached function
search_to_delete = """    # Validierung der Eingabeparameter
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        actual_error_msg = (
            texts.get(
                "pvgis_invalid_lat_lon", "PVGIS: Ungültige Breiten- oder Längengrade."
            )
            or ""
        ) + f" (Lat: {latitude}, Lon: {longitude})"
        effective_errors_list.append(actual_error_msg)
        # if debug_mode_enabled: print(f"PVGIS Error: {actual_error_msg}") #
        # Bereinigt
        return None
    if peak_power_kwp <= 0:
        actual_error_msg = (
            texts.get(
                "pvgis_invalid_peak_power",
                "PVGIS: Installierte Leistung muss positiv sein.")
            or ""
        )
        effective_errors_list.append(actual_error_msg)
        # if debug_mode_enabled: print(f"PVGIS Error: {actual_error_msg}") #
        # Bereinigt
        return None

    base_url = "https://re.jrc.ec.europa.eu/api/PVcalc"
    params = {
        "lat": latitude,
        "lon": longitude,
        "peakpower": peak_power_kwp,
        "loss": system_loss_percent,
        "pvtechchoice": "crystSi",
        "mountingplace": "building",
        "angle": tilt,
        "aspect": azimuth,
        "outputformat": "json",
        "browser": 0,  # Wichtig, um HTML-Antworten zu vermeiden
    }

    # if debug_mode_enabled: # Bereinigt
    #     try:
    #         prepared_request = requests.Request('GET', base_url, params=params).prepare()
    #         print(f"PVGIS Anfrage URL: {prepared_request.url}")
    #     except Exception as e_prep:
    #         print(f"PVGIS: Fehler Vorbereitung Request-URL: {e_prep}")

    error_msg_pvgis = ""  # Initialisiere Fehlermeldung

    try:
        response = requests.get(
            base_url, params=params, timeout=25
        )  # Timeout von 25 Sekunden

        # if debug_mode_enabled: print(f"PVGIS Response Status Code:
        # {response.status_code}") # Bereinigt

        response.raise_for_status()  # Löst HTTPError für 4xx/5xx Status Codes
        data = response.json()

        # if debug_mode_enabled: # Bereinigt
        #     try:
        #         print(f"PVGIS JSON Antwort (Auszug): {json.dumps(data.get('outputs', {}).get('totals', {}), indent=2, ensure_ascii=False)}")
        #     except Exception as e_json_debug:
        #         print(f"PVGIS: Fehler Ausgabe JSON-Antwort: {e_json_debug}")

        # In PVcalc API, 'monthly' is a dict containing 'fixed', which is a list.
        monthly_data = data.get("outputs", {}).get("monthly", {})
        if isinstance(monthly_data, dict) and "fixed" in monthly_data:
            monthly_list = monthly_data["fixed"]
        else:
            monthly_list = monthly_data if isinstance(monthly_data, list) else []

        monthly_production_kwh = [
            m.get("E_m", 0.0) for m in monthly_list
        ]
        annual_production_kwh = (
            data.get(
                "outputs",
                {}).get(
                "totals",
                {}).get(
                "fixed",
                {}).get(
                    "E_y",
                0.0))
        specific_yield_kwh_kwp_pa = (
            data.get("outputs", {})
            .get("totals", {})
            .get("fixed", {})
            .get("E_y", 0.0) / peak_power_kwp if peak_power_kwp > 0 else 0.0
        )  # PVcalc doesn't return Yield_y always

        if (
            not monthly_production_kwh
            or len(monthly_production_kwh) != 12
            or (annual_production_kwh == 0.0 and peak_power_kwp > 0)
        ):
            error_msg_pvgis = (
                texts.get(
                    "pvgis_incomplete_data",
                    "PVGIS: Antwort erhalten, aber Daten scheinen unvollständig oder null.") or "")
            # if debug_mode_enabled: print(f"PVGIS: Unvollständige Daten:
            # monthly_empty={not monthly_production_kwh},
            # len_monthly={len(monthly_production_kwh)},
            # annual_zero={annual_production_kwh == 0 and peak_power_kwp > 0}")
            # # Bereinigt
            effective_errors_list.append(error_msg_pvgis)
            return None

        result = {
            "monthly_production_kwh": monthly_production_kwh,
            "annual_production_kwh": annual_production_kwh,
            "specific_yield_kwh_kwp_pa": specific_yield_kwh_kwp_pa,
            "pvgis_source": data.get("meta", {}).get(
                "source", "PVGIS-TMY"
            ),  # Quelle der Daten (z.B. TMY, ERA5)
        }
        # Im Cache speichern
        _pvgis_cache[cache_key] = result
        return result

    except requests.exceptions.HTTPError as e_http:
        status_code_val = (
            e_http.response.status_code if e_http.response is not None else "N/A")
        error_msg_pvgis = (
            texts.get("pvgis_http_error", "PVGIS API HTTP-Fehler") or ""
        ) + f": Status {status_code_val}"
        response_text_detail = ""
        if e_http.response is not None:  # Response-Objekt könnte None sein
            try:
                response_text_detail = e_http.response.json().get(
                    "message", e_http.response.text
                )
            except json.JSONDecodeError:
                response_text_detail = e_http.response.text
            except Exception:
                response_text_detail = "Konnte Fehlerdetails nicht extrahieren."
        # Begrenze Länge
        error_msg_pvgis += f" - Details: {response_text_detail[:200]}"
    except requests.exceptions.Timeout:
        error_msg_pvgis = (
            texts.get(
                "pvgis_timeout_error",
                "PVGIS API Zeitüberschreitung (Timeout nach 25s). Bitte Netzwerkverbindung prüfen.") or "")
    except requests.exceptions.ConnectionError as e_conn:
        error_msg_pvgis = (
            texts.get(
                "pvgis_connection_error",
                "PVGIS API Verbindungsfehler. Ist das Internet verfügbar und die API erreichbar?") or "") + f" Details: {e_conn}"
    except (
        requests.exceptions.RequestException
    ) as e_req:  # Allgemeinerer Request-Fehler
        error_msg_pvgis = (
            texts.get(
                "pvgis_request_error",
                "PVGIS API Allgemeiner Anfragefehler.") or "") + f" Details: {e_req}"
    except json.JSONDecodeError:
        error_msg_pvgis = (
            texts.get(
                "pvgis_json_decode_error",
                "PVGIS API: Fehler beim Lesen der JSON-Antwort. Möglicherweise temporäres API-Problem.") or "")
    except Exception as e_pvgis_unknown:
        error_msg_pvgis = (
            texts.get("pvgis_unknown_error", "PVGIS API: Unbekannter Fehler.") or ""
        ) + f" Details: {e_pvgis_unknown}"
        # if debug_mode_enabled: traceback.print_exc() # Bereinigt

    if error_msg_pvgis:  # Nur wenn ein Fehler aufgetreten ist
        effective_errors_list.append(error_msg_pvgis)
        # if debug_mode_enabled: print(f"PVGIS Fehler: {error_msg_pvgis}") #
        # Bereinigt
    return None"""

replace_new = """    # Validierung der Eingabeparameter
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        actual_error_msg = (
            texts.get(
                "pvgis_invalid_lat_lon", "PVGIS: Ungültige Breiten- oder Längengrade."
            )
            or ""
        ) + f" (Lat: {latitude}, Lon: {longitude})"
        effective_errors_list.append(actual_error_msg)
        return None
    if peak_power_kwp <= 0:
        actual_error_msg = (
            texts.get(
                "pvgis_invalid_peak_power",
                "PVGIS: Installierte Leistung muss positiv sein.")
            or ""
        )
        effective_errors_list.append(actual_error_msg)
        return None

    result_raw = _get_pvgis_data_cached(latitude, longitude, peak_power_kwp, tilt, azimuth, system_loss_percent)

    if not result_raw:
        return None

    # Check for error dict
    if "error" in result_raw:
        error_key = result_raw["error"]

        if error_key == "pvgis_incomplete_data":
            error_msg_pvgis = texts.get("pvgis_incomplete_data", "PVGIS: Antwort erhalten, aber Daten scheinen unvollständig oder null.")
        elif error_key == "pvgis_http_error":
            error_msg_pvgis = texts.get("pvgis_http_error", "PVGIS API HTTP-Fehler") + f": Status {result_raw.get('status_code')}"
        elif error_key == "pvgis_timeout_error":
            error_msg_pvgis = texts.get("pvgis_timeout_error", "PVGIS API Zeitüberschreitung (Timeout nach 25s). Bitte Netzwerkverbindung prüfen.")
        elif error_key == "pvgis_connection_error":
            error_msg_pvgis = texts.get("pvgis_connection_error", "PVGIS API Verbindungsfehler. Ist das Internet verfügbar und die API erreichbar?") + f" Details: {result_raw.get('details')}"
        elif error_key == "pvgis_request_error":
            error_msg_pvgis = texts.get("pvgis_request_error", "PVGIS API Allgemeiner Anfragefehler.") + f" Details: {result_raw.get('details')}"
        elif error_key == "pvgis_json_decode_error":
            error_msg_pvgis = texts.get("pvgis_json_decode_error", "PVGIS API: Fehler beim Lesen der JSON-Antwort. Möglicherweise temporäres API-Problem.")
        else:
            error_msg_pvgis = texts.get("pvgis_unknown_error", "PVGIS API: Unbekannter Fehler.") + f" Details: {result_raw.get('details')}"

        effective_errors_list.append(error_msg_pvgis)
        return None

    # Deep copy before returning to prevent caller from mutating cache
    return copy.deepcopy(result_raw)"""

content = content.replace(search_to_delete, replace_new)

with open("calculations.py", "w") as f:
    f.write(content)
