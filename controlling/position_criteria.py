"""
Position-Specific Criteria and Quota Definitions

Definiert positionsspezifische Kriterien und Berechnungslogiken für:
- Call Agent
- Verkäufer
- Quality Call
- Sonstige
"""

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass


@dataclass
class QuotaDefinition:
    """Definition einer Quote"""
    name: str
    formula_fn: Callable[[Dict[str, float]], float]
    description: str
    ratio_template: str  # Template für "Jeder X. ..."


# ============================================================================
# CALL AGENT KRITERIEN & QUOTEN
# ============================================================================

CALL_AGENT_CRITERIA = [
    "Kunden terminiert",
    "QC bestanden",
    "Storniert / kein Interesse",
    "Nicht erreicht / neu terminieren",
    "Getätigte Anrufe gesamt",
    "Verkauf",
    "Folgetermin gemacht",
    "Zu teuer gewesen",
    "Angebot erhalten",
    "Technisch nicht machbar"
]


def _calc_ca_qc_quote(data: Dict[str, float]) -> float:
    """QC bestanden Quote: (QC bestanden / Kunden terminiert) × 100"""
    kunden_terminiert = data.get("Kunden terminiert", 0)
    qc_bestanden = data.get("QC bestanden", 0)
    if kunden_terminiert == 0:
        return 0.0
    return (qc_bestanden / kunden_terminiert) * 100


def _calc_ca_terminvereinbarung(data: Dict[str, float]) -> float:
    """Terminvereinbarungsquote: (Kunden terminiert / Getätigte Anrufe gesamt) × 100"""
    anrufe = data.get("Getätigte Anrufe gesamt", 0)
    termine = data.get("Kunden terminiert", 0)
    if anrufe == 0:
        return 0.0
    return (termine / anrufe) * 100


def _calc_ca_storniert_quote(data: Dict[str, float]) -> float:
    """Storniert Quote: (Storniert/kein Interesse / Kunden terminiert) × 100"""
    kunden_terminiert = data.get("Kunden terminiert", 0)
    storniert = data.get("Storniert / kein Interesse", 0)
    if kunden_terminiert == 0:
        return 0.0
    return (storniert / kunden_terminiert) * 100


def _calc_ca_nicht_erreicht_quote(data: Dict[str, float]) -> float:
    """Nicht erreicht Quote: (Nicht erreicht / Getätigte Anrufe gesamt) × 100"""
    anrufe = data.get("Getätigte Anrufe gesamt", 0)
    nicht_erreicht = data.get("Nicht erreicht / neu terminieren", 0)
    if anrufe == 0:
        return 0.0
    return (nicht_erreicht / anrufe) * 100


def _calc_ca_verkauf_quote(data: Dict[str, float]) -> float:
    """Verkaufsquote: (Verkauf / Kunden terminiert) × 100"""
    kunden_terminiert = data.get("Kunden terminiert", 0)
    verkauf = data.get("Verkauf", 0)
    if kunden_terminiert == 0:
        return 0.0
    return (verkauf / kunden_terminiert) * 100


def _calc_ca_folgetermin_quote(data: Dict[str, float]) -> float:
    """Folgetermin Quote: (Folgetermin gemacht / Kunden terminiert) × 100"""
    kunden_terminiert = data.get("Kunden terminiert", 0)
    folgetermin = data.get("Folgetermin gemacht", 0)
    if kunden_terminiert == 0:
        return 0.0
    return (folgetermin / kunden_terminiert) * 100


def _calc_ca_zu_teuer_quote(data: Dict[str, float]) -> float:
    """Zu teuer Quote: (Zu teuer gewesen / Kunden terminiert) × 100"""
    kunden_terminiert = data.get("Kunden terminiert", 0)
    zu_teuer = data.get("Zu teuer gewesen", 0)
    if kunden_terminiert == 0:
        return 0.0
    return (zu_teuer / kunden_terminiert) * 100


def _calc_ca_angebot_quote(data: Dict[str, float]) -> float:
    """Angebot Quote: (Angebot erhalten / Kunden terminiert) × 100"""
    kunden_terminiert = data.get("Kunden terminiert", 0)
    angebot = data.get("Angebot erhalten", 0)
    if kunden_terminiert == 0:
        return 0.0
    return (angebot / kunden_terminiert) * 100


def _calc_ca_technisch_nicht_machbar_quote(data: Dict[str, float]) -> float:
    """Technisch nicht machbar Quote: (Technisch nicht machbar / Kunden terminiert) × 100"""
    kunden_terminiert = data.get("Kunden terminiert", 0)
    nicht_machbar = data.get("Technisch nicht machbar", 0)
    if kunden_terminiert == 0:
        return 0.0
    return (nicht_machbar / kunden_terminiert) * 100


CALL_AGENT_QUOTAS = [
    QuotaDefinition(
        name="QC bestanden Quote",
        formula_fn=_calc_ca_qc_quote,
        description="Anteil der Termine mit bestandenem QC",
        ratio_template="Jeder {ratio}. terminierte Kunde hat QC bestanden"
    ),
    QuotaDefinition(
        name="Terminvereinbarungsquote",
        formula_fn=_calc_ca_terminvereinbarung,
        description="Erfolgsrate der Terminvereinbarung pro Anruf",
        ratio_template="Jeder {ratio}. Anruf führt zu einem Termin"
    ),
    QuotaDefinition(
        name="Storniert / kein Interesse Quote",
        formula_fn=_calc_ca_storniert_quote,
        description="Anteil stornierter oder uninteressierter Kunden",
        ratio_template="Jeder {ratio}. terminierte Kunde ist nicht interessiert"
    ),
    QuotaDefinition(
        name="Nicht erreicht Quote",
        formula_fn=_calc_ca_nicht_erreicht_quote,
        description="Anteil nicht erreichter Kunden pro Anruf",
        ratio_template="Jeder {ratio}. Anruf erreicht den Kunden nicht"
    ),
    QuotaDefinition(
        name="Verkaufsquote",
        formula_fn=_calc_ca_verkauf_quote,
        description="Anteil verkaufter Termine",
        ratio_template="Jeder {ratio}. terminierte Kunde wird verkauft"
    ),
    QuotaDefinition(
        name="Folgetermin Quote",
        formula_fn=_calc_ca_folgetermin_quote,
        description="Anteil vereinbarter Folgetermine",
        ratio_template="Jeder {ratio}. terminierte Kunde erhält Folgetermin"
    ),
    QuotaDefinition(
        name="Zu teuer Quote",
        formula_fn=_calc_ca_zu_teuer_quote,
        description="Anteil der Kunden, denen es zu teuer war",
        ratio_template="Jeder {ratio}. terminierte Kunde findet es zu teuer"
    ),
    QuotaDefinition(
        name="Angebot Quote",
        formula_fn=_calc_ca_angebot_quote,
        description="Anteil der Kunden mit Angebot",
        ratio_template="Jeder {ratio}. terminierte Kunde erhält ein Angebot"
    ),
    QuotaDefinition(
        name="Technisch nicht machbar Quote",
        formula_fn=_calc_ca_technisch_nicht_machbar_quote,
        description="Anteil technisch nicht machbarer Projekte",
        ratio_template="Jeder {ratio}. terminierte Kunde ist technisch nicht machbar"
    )
]


# ============================================================================
# VERKÄUFER KRITERIEN & QUOTEN
# ============================================================================

VERKAUFER_CRITERIA = [
    "Angefahrene Termine",
    "Nicht angefahrene Termine",
    "Verkauf",
    "QC bestanden",
    "Storniert / kein Interesse",
    "Technisch nicht machbar",
    "Folgetermin gemacht",
    "Zu teuer gewesen",
    "Angebot erhalten"
]


def _calc_vk_abschlussquote(data: Dict[str, float]) -> float:
    """Abschlussquote: (Verkauf / Angefahrene Termine) × 100"""
    angefahren = data.get("Angefahrene Termine", 0)
    verkauf = data.get("Verkauf", 0)
    if angefahren == 0:
        return 0.0
    return (verkauf / angefahren) * 100


def _calc_vk_qc_quote(data: Dict[str, float]) -> float:
    """QC Quote: (QC bestanden / Verkauf) × 100"""
    verkauf = data.get("Verkauf", 0)
    qc = data.get("QC bestanden", 0)
    if verkauf == 0:
        return 0.0
    return (qc / verkauf) * 100


def _calc_vk_anfahrquote(data: Dict[str, float]) -> float:
    """Anfahrquote: (Angefahrene Termine / (Angefahrene + Nicht angefahrene)) × 100"""
    angefahren = data.get("Angefahrene Termine", 0)
    nicht_angefahren = data.get("Nicht angefahrene Termine", 0)
    gesamt = angefahren + nicht_angefahren
    if gesamt == 0:
        return 0.0
    return (angefahren / gesamt) * 100


def _calc_vk_storniert_quote(data: Dict[str, float]) -> float:
    """Storniert Quote: (Storniert / Angefahrene Termine) × 100"""
    angefahren = data.get("Angefahrene Termine", 0)
    storniert = data.get("Storniert / kein Interesse", 0)
    if angefahren == 0:
        return 0.0
    return (storniert / angefahren) * 100


def _calc_vk_technisch_nicht_machbar_quote(data: Dict[str, float]) -> float:
    """Technisch nicht machbar Quote: (Technisch nicht machbar / Angefahrene Termine) × 100"""
    angefahren = data.get("Angefahrene Termine", 0)
    nicht_machbar = data.get("Technisch nicht machbar", 0)
    if angefahren == 0:
        return 0.0
    return (nicht_machbar / angefahren) * 100


def _calc_vk_folgetermin_quote(data: Dict[str, float]) -> float:
    """Folgetermin Quote: (Folgetermin gemacht / Angefahrene Termine) × 100"""
    angefahren = data.get("Angefahrene Termine", 0)
    folgetermin = data.get("Folgetermin gemacht", 0)
    if angefahren == 0:
        return 0.0
    return (folgetermin / angefahren) * 100


def _calc_vk_zu_teuer_quote(data: Dict[str, float]) -> float:
    """Zu teuer Quote: (Zu teuer / Angefahrene Termine) × 100"""
    angefahren = data.get("Angefahrene Termine", 0)
    zu_teuer = data.get("Zu teuer gewesen", 0)
    if angefahren == 0:
        return 0.0
    return (zu_teuer / angefahren) * 100


def _calc_vk_angebot_quote(data: Dict[str, float]) -> float:
    """Angebot Quote: (Angebot erhalten / Angefahrene Termine) × 100"""
    angefahren = data.get("Angefahrene Termine", 0)
    angebot = data.get("Angebot erhalten", 0)
    if angefahren == 0:
        return 0.0
    return (angebot / angefahren) * 100


VERKAUFER_QUOTAS = [
    QuotaDefinition(
        name="Abschlussquote",
        formula_fn=_calc_vk_abschlussquote,
        description="Erfolgsrate bei angefahrenen Terminen",
        ratio_template="Jeder {ratio}. angefahrene Termin wird verkauft"
    ),
    QuotaDefinition(
        name="QC bestanden Quote",
        formula_fn=_calc_vk_qc_quote,
        description="Anteil bestandener QC bei Verkäufen",
        ratio_template="Jeder {ratio}. Verkauf besteht die QC"
    ),
    QuotaDefinition(
        name="Anfahrquote",
        formula_fn=_calc_vk_anfahrquote,
        description="Anteil tatsächlich angefahrener Termine",
        ratio_template="Jeder {ratio}. Termin wird angefahren"
    ),
    QuotaDefinition(
        name="Storniert / kein Interesse Quote",
        formula_fn=_calc_vk_storniert_quote,
        description="Anteil stornierter oder uninteressierter Kunden",
        ratio_template="Jeder {ratio}. angefahrene Termin ist nicht interessiert"
    ),
    QuotaDefinition(
        name="Technisch nicht machbar Quote",
        formula_fn=_calc_vk_technisch_nicht_machbar_quote,
        description="Anteil technisch nicht machbarer Projekte",
        ratio_template="Jeder {ratio}. angefahrene Termin ist technisch nicht machbar"
    ),
    QuotaDefinition(
        name="Folgetermin Quote",
        formula_fn=_calc_vk_folgetermin_quote,
        description="Anteil vereinbarter Folgetermine",
        ratio_template="Jeder {ratio}. angefahrene Termin erhält Folgetermin"
    ),
    QuotaDefinition(
        name="Zu teuer Quote",
        formula_fn=_calc_vk_zu_teuer_quote,
        description="Anteil der Kunden, denen es zu teuer war",
        ratio_template="Jeder {ratio}. angefahrene Termin findet es zu teuer"
    ),
    QuotaDefinition(
        name="Angebot Quote",
        formula_fn=_calc_vk_angebot_quote,
        description="Anteil der Kunden mit Angebot",
        ratio_template="Jeder {ratio}. angefahrene Termin erhält ein Angebot"
    )
]


# ============================================================================
# QUALITY CALL KRITERIEN & QUOTEN
# ============================================================================

QUALITY_CALL_CRITERIA = [
    "QC durchgeführt",
    "QC bestanden",
    "QC nicht bestanden"
]


def _calc_qc_bestandenquote(data: Dict[str, float]) -> float:
    """QC Bestandenquote: (QC bestanden / QC durchgeführt) × 100"""
    durchgefuehrt = data.get("QC durchgeführt", 0)
    bestanden = data.get("QC bestanden", 0)
    if durchgefuehrt == 0:
        return 0.0
    return (bestanden / durchgefuehrt) * 100


def _calc_qc_durchfallquote(data: Dict[str, float]) -> float:
    """QC Durchfallquote: (QC nicht bestanden / QC durchgeführt) × 100"""
    durchgefuehrt = data.get("QC durchgeführt", 0)
    nicht_bestanden = data.get("QC nicht bestanden", 0)
    if durchgefuehrt == 0:
        return 0.0
    return (nicht_bestanden / durchgefuehrt) * 100


QUALITY_CALL_QUOTAS = [
    QuotaDefinition(
        name="QC Bestandenquote",
        formula_fn=_calc_qc_bestandenquote,
        description="Anteil bestandener QC-Prüfungen",
        ratio_template="Jeder {ratio}. QC wird bestanden"
    ),
    QuotaDefinition(
        name="QC Durchfallquote",
        formula_fn=_calc_qc_durchfallquote,
        description="Anteil nicht bestandener QC-Prüfungen",
        ratio_template="Jeder {ratio}. QC wird nicht bestanden"
    )
]


# ============================================================================
# SONSTIGE KRITERIEN & QUOTEN
# ============================================================================

SONSTIGE_CRITERIA = []  # Wird bei Bedarf erweitert
SONSTIGE_QUOTAS = []


# ============================================================================
# POSITION MAPPING
# ============================================================================

POSITION_CONFIG = {
    "Call Agent": {
        "criteria": CALL_AGENT_CRITERIA,
        "quotas": CALL_AGENT_QUOTAS
    },
    "Verkäufer": {
        "criteria": VERKAUFER_CRITERIA,
        "quotas": VERKAUFER_QUOTAS
    },
    "Quality Call": {
        "criteria": QUALITY_CALL_CRITERIA,
        "quotas": QUALITY_CALL_QUOTAS
    },
    "Sonstiges": {
        "criteria": SONSTIGE_CRITERIA,
        "quotas": SONSTIGE_QUOTAS
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_position_criteria(position_name: str) -> List[str]:
    """
    Hole relevante Kriterien für eine Position.
    
    Args:
        position_name: Name der Position
        
    Returns:
        Liste der Kriteriumnamen
    """
    config = POSITION_CONFIG.get(position_name, {})
    return config.get("criteria", [])


def get_position_quotas(position_name: str) -> List[QuotaDefinition]:
    """
    Hole relevante Quoten für eine Position.
    
    Args:
        position_name: Name der Position
        
    Returns:
        Liste der QuotaDefinition-Objekte
    """
    config = POSITION_CONFIG.get(position_name, {})
    return config.get("quotas", [])


def calculate_quotas_for_position(
    position_name: str,
    raw_data: Dict[str, float]
) -> Dict[str, float]:
    """
    Berechne alle Quoten für eine Position basierend auf Rohdaten.
    
    Args:
        position_name: Name der Position
        raw_data: Dictionary mit Kriterienwerten
        
    Returns:
        Dictionary mit berechneten Quoten
    """
    quotas_defs = get_position_quotas(position_name)
    result = {}
    
    for quota_def in quotas_defs:
        try:
            value = quota_def.formula_fn(raw_data)
            result[quota_def.name] = value
        except Exception as e:
            # Bei Fehler 0.0 zurückgeben
            result[quota_def.name] = 0.0
    
    return result


def calculate_ratio_description(
    quota_percentage: float,
    quota_name: str,
    position_name: str
) -> str:
    """
    Generiere Ratio-Beschreibung (z.B. "Jeder 3. Anruf führt zu einem Termin").
    
    Args:
        quota_percentage: Prozentwert der Quote
        quota_name: Name der Quote
        position_name: Name der Position
        
    Returns:
        Beschreibung als String
    """
    if quota_percentage == 0 or quota_percentage > 100:
        return "keine Daten"
    
    ratio = max(1, round(100 / quota_percentage))
    
    # Finde passende QuotaDefinition
    quotas_defs = get_position_quotas(position_name)
    for quota_def in quotas_defs:
        if quota_def.name == quota_name:
            return quota_def.ratio_template.format(ratio=ratio)
    
    # Fallback
    return f"1 zu {ratio}"
