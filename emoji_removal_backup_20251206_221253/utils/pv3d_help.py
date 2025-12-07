"""
3D PV-Visualisierung Hilfe-System

Dieses Modul stellt Tooltips, Hilfe-Texte und interaktive Anleitungen bereit.
"""

import streamlit as st
from typing import Dict, List, Optional


# Tooltip-Definitionen
TOOLTIPS = {
    # Basis-Einstellungen
    "building_length": "Länge des Gebäudes in Metern. Messen Sie die längste Seite Ihres Gebäudes.",
    "building_width": "Breite des Gebäudes in Metern. Messen Sie die kürzere Seite.",
    "building_height": "Höhe der Außenwände (Traufhöhe) vom Boden bis zur Dachkante, nicht die Firsthöhe!",
    "roof_type": "Wählen Sie die Dachform Ihres Gebäudes. Dies beeinflusst die Modul-Platzierung erheblich.",
    
    # Modul-Belegung
    "layout_mode": "Automatisch: Module werden gleichmäßig verteilt. Manuell: Sie können einzelne Module entfernen.",
    "mounting_type": "Wählen Sie die Ausrichtung der Aufständerung für optimalen Ertrag. Süd = maximaler Ertrag, Ost-West = gleichmäßige Produktion.",
    "azimuth": "Horizontale Ausrichtung in Grad: 0° = Süd, 90° = West, 180° = Nord, 270° = Ost",
    "tilt": "Neigungswinkel zur Horizontalen: 0° = horizontal, 90° = vertikal. Optimal für Deutschland: 30-35°",
    "use_garage": "Fügt automatisch eine Garage (6m x 3m) hinzu, wenn Module nicht auf dem Hauptdach passen.",
    "use_facade": "Platziert Module an der Südfassade als letzte Option bei Platzmangel. Ertrag ca. 70% im Vergleich zu Dach.",
    "removed_indices": "Geben Sie die Indizes der zu entfernenden Module ein (komma-separiert, 0-basiert). Beispiel: 0,1,5,10",
    
    # Erweiterte Kontrolle
    "collision_detection": "Prüft automatisch auf Überschneidungen zwischen Modulen und zeigt Warnungen an. Deaktivieren für experimentelle Layouts.",
    "selection_mode": "Einzeln: Ein Modul auswählen. Gruppe: Vordefinierte Gruppen. Bereich: Start- und End-Index angeben.",
    "module_index": "Index des auszuwählenden Moduls (0-basiert). 0 = erstes Modul, 1 = zweites Modul, usw.",
    
    # Analyse
    "optimization_goal": """Wählen Sie das Optimierungsziel:
    • Maximale Modulanzahl: Platziert so viele Module wie möglich
    • Maximaler Ertrag: Optimiert für höchste Energieausbeute
    • Ausgewogen: Balance zwischen Anzahl und Ertrag""",
    "shading_analysis": "Färbt Module basierend auf Verschattungsgrad ein. Grün = keine Verschattung, Rot = starke Verschattung.",
    "hour_of_day": "Wählen Sie die Tageszeit für die Verschattungs-Analyse. Testen Sie verschiedene Zeiten (Morgen, Mittag, Abend).",
    "season": "Wählen Sie die Jahreszeit für die Sonnenstandsberechnung. Sommer = höchster Sonnenstand, Winter = niedrigster.",
    "latitude": "Breitengrad des Standorts für Sonnenstandsberechnung. Deutschland: ca. 47-55°N",
    "sun_animation": "Zeigt eine Animation des Sonnenverlaufs über den Tag. Hilft Verschattungsmuster zu verstehen.",
    "yield_heatmap": "Färbt Module basierend auf ihrem Ertragspotential. Dunkelgrün = höchster Ertrag, Rot = sehr niedriger Ertrag.",
    "heatmap_metric": "Wählen Sie die Metrik für die Farbcodierung: Jahresertrag, Verschattung oder Effizienz.",
    "yield_forecast": "Berechnet erwarteten Jahresertrag, Ersparnis, CO₂-Einsparung und Amortisationszeit.",
    "electricity_price": "Aktueller Strompreis für Wirtschaftlichkeitsberechnung. Deutschland: ca. 0.30-0.40 €/kWh",
    "module_efficiency": "Wirkungsgrad der PV-Module. Standard: 20%, Premium: 22-25%",
    
    # Export
    "screenshot": "Exportiert die aktuelle 3D-Ansicht als Bild. PNG = verlustfrei, JPEG = komprimiert.",
    "screenshot_format": "PNG: Beste Qualität, größere Dateien. JPEG: Gute Qualität, kleinere Dateien.",
    "screenshot_resolution": "Höhere Auflösung = bessere Qualität, aber größere Dateien. Full HD empfohlen für Standard-Nutzung.",
    "multiview": "Erstellt Screenshots aus 4 Perspektiven (Isometrisch, Top, Süd, Ost) als ZIP-Datei.",
    "animation_360": "Erstellt eine 360° Rotation als GIF-Animation. Mehr Frames = flüssiger, aber größere Datei.",
    "animation_frames": "Anzahl der Frames für die Animation. 36 = guter Kompromiss, 72 = sehr flüssig.",
    "model_3d": "Exportiert das 3D-Modell. STL = 3D-Druck, GLTF = Web, OBJ = Universal.",
    "export_csv": "Exportiert Modul-Details (Position, Ausrichtung, Ertrag) als CSV für Excel-Analyse.",
    "export_json": "Exportiert vollständige Layout-Konfiguration als JSON für Backup oder Import in andere Tools.",
}


# Hilfe-Texte für komplexe Funktionen
HELP_TEXTS = {
    "optimization_assistant": {
        "title": "Optimierungs-Assistent",
        "description": "Der Optimierungs-Assistent findet automatisch die beste Konfiguration für Ihre Anforderungen.",
        "steps": [
            "1. Wählen Sie ein Optimierungs-Ziel (Maximale Modulanzahl, Maximaler Ertrag, oder Ausgewogen)",
            "2. Klicken Sie auf 'Optimierung starten'",
            "3. Das System generiert und bewertet verschiedene Konfigurationen",
            "4. Die beste Konfiguration wird automatisch angewendet",
            "5. Prüfen Sie das Ergebnis und passen Sie bei Bedarf an"
        ],
        "tips": [
            "'Maximaler Ertrag' ist für die meisten Fälle die beste Wahl",
            "'Ausgewogen' bietet einen guten Kompromiss zwischen Anzahl und Ertrag",
            "Die Optimierung berücksichtigt Verschattung und Ausrichtung"
        ]
    },
    
    "shading_analysis": {
        "title": "☀️ Verschattungs-Analyse",
        "description": "Analysiert die Verschattung jedes Moduls zu verschiedenen Tageszeiten und Jahreszeiten.",
        "steps": [
            "1. Aktivieren Sie 'Verschattungs-Analyse aktivieren'",
            "2. Wählen Sie eine Tageszeit (z.B. 12:00 Uhr für Mittag)",
            "3. Wählen Sie eine Jahreszeit (Sommer, Winter, oder Frühling/Herbst)",
            "4. Geben Sie den Breitengrad Ihres Standorts ein (Deutschland: ca. 51°)",
            "5. Module werden entsprechend ihrer Verschattung eingefärbt"
        ],
        "interpretation": [
            "🟢 Grün: Keine Verschattung (0-10%) - Optimal",
            "🟡 Gelb: Leichte Verschattung (10-30%) - Gut",
            "🟠 Orange: Mittlere Verschattung (30-60%) - Akzeptabel",
            "🔴 Rot: Starke Verschattung (60-100%) - Problematisch"
        ],
        "tips": [
            "Testen Sie verschiedene Tageszeiten (Morgen, Mittag, Abend)",
            "Vergleichen Sie Sommer und Winter",
            "Entfernen Sie stark verschattete Module (rot) für besseren Ertrag"
        ]
    },
    
    "yield_heatmap": {
        "title": "🔥 Ertrags-Heatmap",
        "description": "Visualisiert das Ertragspotential jedes Moduls mit Farbcodierung.",
        "steps": [
            "1. Aktivieren Sie 'Ertrags-Heatmap aktivieren'",
            "2. Wählen Sie eine Metrik (Jahresertrag, Verschattung, oder Effizienz)",
            "3. Die Heatmap wird nach dem Rendern angezeigt",
            "4. Identifizieren Sie schwache Module (orange/rot)",
            "5. Optimieren Sie die Konfiguration basierend auf den Ergebnissen"
        ],
        "interpretation": [
            "🟢 Dunkelgrün: Höchster Ertrag (90-100%) - Behalten",
            "🟢 Hellgrün: Guter Ertrag (70-90%) - Behalten",
            "🟡 Gelb: Mittlerer Ertrag (50-70%) - Prüfen",
            "🟠 Orange: Niedriger Ertrag (30-50%) - Überdenken",
            "🔴 Rot: Sehr niedriger Ertrag (<30%) - Entfernen"
        ],
        "tips": [
            "Entfernen Sie Module mit <50% Ertrag für bessere Wirtschaftlichkeit",
            "Priorisieren Sie grüne Bereiche bei der Planung",
            "Kombinieren Sie mit Verschattungs-Analyse für beste Ergebnisse"
        ]
    },
    
    "module_selection": {
        "title": "🎛️ Modul-Auswahl & Bearbeitung",
        "description": "Wählen Sie einzelne Module oder Gruppen aus, um deren Eigenschaften zu bearbeiten.",
        "modes": {
            "Einzeln": [
                "1. Wählen Sie 'Einzeln' als Auswahl-Modus",
                "2. Geben Sie den Index des Moduls ein (0 = erstes Modul)",
                "3. Klicken Sie auf '➕ Auswählen'",
                "4. Das Modul wird in der 3D-Ansicht hervorgehoben"
            ],
            "Gruppe": [
                "1. Wählen Sie 'Gruppe' als Auswahl-Modus",
                "2. Wählen Sie eine vordefinierte Gruppe aus",
                "3. Klicken Sie auf '🔘 Gruppe auswählen'",
                "4. Alle Module der Gruppe werden ausgewählt"
            ],
            "Bereich": [
                "1. Wählen Sie 'Bereich' als Auswahl-Modus",
                "2. Geben Sie Start-Index ein (z.B. 0)",
                "3. Geben Sie End-Index ein (z.B. 9)",
                "4. Klicken Sie auf '🔘 Bereich auswählen'",
                "5. Module 0-9 werden ausgewählt"
            ]
        },
        "tips": [
            "Verwenden Sie 'Gruppe' für schnelle Auswahl vieler Module",
            "Verwenden Sie 'Bereich' für zusammenhängende Module",
            "Verwenden Sie 'Einzeln' für präzise Kontrolle"
        ]
    },
    
    "export_options": {
        "title": "Export-Optionen",
        "description": "Exportieren Sie die 3D-Visualisierung in verschiedenen Formaten.",
        "formats": {
            "Screenshot": {
                "description": "Exportiert die aktuelle Ansicht als Bild",
                "formats": ["PNG (verlustfrei, beste Qualität)", "JPEG (komprimiert, kleinere Dateien)"],
                "resolutions": ["HD (1280x720)", "Full HD (1920x1080)", "2K (2560x1440)", "4K (3840x2160)"],
                "use_cases": ["Präsentationen", "Dokumentation", "E-Mail"]
            },
            "Multi-View": {
                "description": "Erstellt Screenshots aus 4 Perspektiven",
                "views": ["Isometrisch (3D-Ansicht)", "Top (Draufsicht)", "Süd (Südansicht)", "Ost (Ostansicht)"],
                "output": "ZIP-Datei mit 4 Bildern",
                "use_cases": ["Vollständige Dokumentation", "Verschiedene Perspektiven"]
            },
            "360° Animation": {
                "description": "Erstellt eine 360° Rotation als GIF",
                "settings": ["Frames: 12-72 (mehr = flüssiger)", "Auflösung: Klein/Mittel/Groß"],
                "use_cases": ["Web-Präsentationen", "Animierte Vorschau"]
            },
            "3D-Modell": {
                "description": "Exportiert das 3D-Modell",
                "formats": ["STL (3D-Druck, CAD)", "GLTF (Web, AR/VR)", "OBJ (Universal)"],
                "use_cases": ["CAD-Software", "3D-Druck", "Weitere Bearbeitung"]
            },
            "Daten": {
                "description": "Exportiert Konfiguration und Details",
                "formats": ["CSV (Excel-Analyse)", "JSON (Backup, Import)"],
                "use_cases": ["Datenanalyse", "Backup", "Versionskontrolle"]
            }
        }
    }
}


# Beispiel-Konfigurationen
EXAMPLE_CONFIGS = {
    "Einfamilienhaus": {
        "description": "Typisches Einfamilienhaus mit Satteldach",
        "settings": {
            "building_length": 12.0,
            "building_width": 10.0,
            "building_height": 3.0,
            "roof_type": "Satteldach",
            "mounting_type": "Süd",
            "expected_modules": "20-30",
            "expected_power": "8-12 kWp"
        }
    },
    "Mehrfamilienhaus": {
        "description": "Mehrfamilienhaus mit Flachdach",
        "settings": {
            "building_length": 20.0,
            "building_width": 15.0,
            "building_height": 9.0,
            "roof_type": "Flachdach",
            "mounting_type": "Ost-West",
            "expected_modules": "60-80",
            "expected_power": "25-35 kWp"
        }
    },
    "Gewerbe": {
        "description": "Gewerbehalle mit großem Flachdach",
        "settings": {
            "building_length": 30.0,
            "building_width": 20.0,
            "building_height": 4.0,
            "roof_type": "Flachdach",
            "mounting_type": "Süd",
            "expected_modules": "120-150",
            "expected_power": "50-65 kWp"
        }
    }
}


def get_tooltip(key: str) -> str:
    """
    Gibt den Tooltip-Text für einen UI-Element-Key zurück.
    
    Args:
        key: Eindeutiger Key des UI-Elements
        
    Returns:
        Tooltip-Text oder leerer String wenn nicht gefunden
    """
    return TOOLTIPS.get(key, "")


def show_help_dialog(topic: str):
    """
    Zeigt einen Hilfe-Dialog für ein bestimmtes Thema.
    
    Args:
        topic: Thema für das Hilfe angezeigt werden soll
    """
    if topic not in HELP_TEXTS:
        st.warning(f"Keine Hilfe verfügbar für: {topic}")
        return
    
    help_data = HELP_TEXTS[topic]
    
    with st.expander(f"❓ Hilfe: {help_data['title']}", expanded=True):
        st.markdown(f"**{help_data['description']}**")
        
        if "steps" in help_data:
            st.markdown("### 📋 Schritt-für-Schritt-Anleitung")
            for step in help_data["steps"]:
                st.markdown(step)
        
        if "modes" in help_data:
            st.markdown("### Modi")
            for mode, steps in help_data["modes"].items():
                with st.expander(f"**{mode}**"):
                    for step in steps:
                        st.markdown(step)
        
        if "formats" in help_data:
            st.markdown("### Formate")
            for format_name, format_data in help_data["formats"].items():
                with st.expander(f"**{format_name}**"):
                    st.markdown(f"*{format_data['description']}*")
                    if "formats" in format_data:
                        st.markdown("**Formate:**")
                        for fmt in format_data["formats"]:
                            st.markdown(f"- {fmt}")
                    if "views" in format_data:
                        st.markdown("**Ansichten:**")
                        for view in format_data["views"]:
                            st.markdown(f"- {view}")
                    if "settings" in format_data:
                        st.markdown("**Einstellungen:**")
                        for setting in format_data["settings"]:
                            st.markdown(f"- {setting}")
                    if "use_cases" in format_data:
                        st.markdown("**Anwendungsfälle:**")
                        for use_case in format_data["use_cases"]:
                            st.markdown(f"- {use_case}")
        
        if "interpretation" in help_data:
            st.markdown("### Interpretation")
            for interp in help_data["interpretation"]:
                st.markdown(interp)
        
        if "tips" in help_data:
            st.markdown("### Tipps")
            for tip in help_data["tips"]:
                st.markdown(tip)


def show_example_config(config_name: str):
    """
    Zeigt eine Beispiel-Konfiguration.
    
    Args:
        config_name: Name der Beispiel-Konfiguration
    """
    if config_name not in EXAMPLE_CONFIGS:
        st.warning(f"Keine Beispiel-Konfiguration verfügbar für: {config_name}")
        return
    
    config = EXAMPLE_CONFIGS[config_name]
    
    st.info(f"**{config_name}:** {config['description']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Gebäude:**")
        st.markdown(f"- Länge: {config['settings']['building_length']}m")
        st.markdown(f"- Breite: {config['settings']['building_width']}m")
        st.markdown(f"- Höhe: {config['settings']['building_height']}m")
        st.markdown(f"- Dachform: {config['settings']['roof_type']}")
    
    with col2:
        st.markdown("**Erwartete Werte:**")
        st.markdown(f"- Module: {config['settings']['expected_modules']}")
        st.markdown(f"- Leistung: {config['settings']['expected_power']}")
        st.markdown(f"- Aufständerung: {config['settings']['mounting_type']}")


def render_help_sidebar():
    """
    Rendert eine Hilfe-Sidebar mit allen verfügbaren Hilfe-Themen.
    """
    with st.sidebar.expander("❓ Hilfe & Anleitungen", expanded=False):
        st.markdown("### 📚 Verfügbare Hilfe-Themen")
        
        help_topics = {
            "optimization_assistant": "Optimierungs-Assistent",
            "shading_analysis": "☀️ Verschattungs-Analyse",
            "yield_heatmap": "🔥 Ertrags-Heatmap",
            "module_selection": "🎛️ Modul-Auswahl",
            "export_options": "Export-Optionen"
        }
        
        selected_topic = st.selectbox(
            "Wählen Sie ein Thema",
            options=list(help_topics.keys()),
            format_func=lambda x: help_topics[x],
            key="help_topic_select"
        )
        
        if st.button("📖 Hilfe anzeigen", use_container_width=True):
            st.session_state["show_help_for"] = selected_topic
        
        st.divider()
        
        st.markdown("### 📋 Beispiel-Konfigurationen")
        
        example_names = list(EXAMPLE_CONFIGS.keys())
        selected_example = st.selectbox(
            "Wählen Sie ein Beispiel",
            options=example_names,
            key="example_config_select"
        )
        
        if st.button("👁️ Beispiel anzeigen", use_container_width=True):
            show_example_config(selected_example)
        
        st.divider()
        
        st.markdown("### Dokumentation")
        st.markdown("Vollständige Dokumentation:")
        st.markdown("- [Benutzerhandbuch](docs/3D_VISUALIZATION_USER_GUIDE.md)")
        st.markdown("- [Schnellreferenz](docs/3D_VISUALIZATION_QUICK_REFERENCE.md)")


def show_contextual_help(context: str):
    """
    Zeigt kontextbezogene Hilfe basierend auf dem aktuellen UI-Bereich.
    
    Args:
        context: Aktueller Kontext (z.B. "basis_settings", "analysis", etc.)
    """
    context_help = {
        "basis_settings": {
            "title": "🏠 Basis-Einstellungen",
            "tips": [
                "Messen Sie Ihr Gebäude präzise für beste Ergebnisse",
                "Die Traufhöhe ist die Höhe der Außenwände, nicht die Firsthöhe",
                "Wählen Sie die Dachform, die Ihrem Gebäude am nächsten kommt"
            ]
        },
        "module_placement": {
            "title": "Modul-Belegung",
            "tips": [
                "Starten Sie mit 'Automatisch' für eine erste Planung",
                "Süd-Ausrichtung liefert den höchsten Ertrag",
                "Ost-West-Ausrichtung optimiert den Eigenverbrauch"
            ]
        },
        "advanced_controls": {
            "title": "🎛️ Erweiterte Kontrolle",
            "tips": [
                "Kollisionserkennung hilft unrealistische Konfigurationen zu vermeiden",
                "Verwenden Sie Gruppen-Auswahl für schnelle Anpassungen",
                "Bereich-Auswahl ist ideal für zusammenhängende Module"
            ]
        },
        "analysis": {
            "title": "Analyse",
            "tips": [
                "Nutzen Sie den Optimierungs-Assistenten für beste Ergebnisse",
                "Verschattungs-Analyse zeigt problematische Bereiche",
                "Ertrags-Heatmap hilft schwache Module zu identifizieren"
            ]
        },
        "export": {
            "title": "Export",
            "tips": [
                "Multi-View Export liefert vollständige Dokumentation",
                "JSON-Export ermöglicht Backup Ihrer Konfiguration",
                "CSV-Export ist ideal für Excel-Analysen"
            ]
        }
    }
    
    if context in context_help:
        help_data = context_help[context]
        st.info(f"**{help_data['title']}**\n\n" + "\n".join(help_data["tips"]))


def show_success_message(action: str):
    """
    Zeigt eine Erfolgsmeldung nach einer Aktion.
    
    Args:
        action: Durchgeführte Aktion
    """
    messages = {
        "optimization": "Optimierung erfolgreich abgeschlossen! Die beste Konfiguration wurde angewendet.",
        "export_screenshot": "Screenshot erfolgreich exportiert!",
        "export_multiview": "Multi-View Screenshots erfolgreich exportiert! ZIP-Datei wurde heruntergeladen.",
        "export_360": "360° Animation erfolgreich erstellt! GIF wurde heruntergeladen.",
        "export_3d": "3D-Modell erfolgreich exportiert!",
        "export_csv": "CSV-Datei erfolgreich exportiert!",
        "export_json": "JSON-Konfiguration erfolgreich exportiert!",
        "module_selected": "Modul(e) erfolgreich ausgewählt!",
        "module_deselected": "Auswahl erfolgreich aufgehoben!",
    }
    
    if action in messages:
        st.success(messages[action])
    else:
        st.success(f"{action} erfolgreich abgeschlossen!")


def show_warning_message(warning_type: str, details: Optional[str] = None):
    """
    Zeigt eine Warnmeldung.
    
    Args:
        warning_type: Typ der Warnung
        details: Optionale Details zur Warnung
    """
    warnings = {
        "collision": "Kollision erkannt! Module überschneiden sich. Bitte passen Sie die Konfiguration an.",
        "no_modules": "Keine Module platziert! Vergrößern Sie das Gebäude oder aktivieren Sie zusätzliche Flächen.",
        "low_yield": "Einige Module haben sehr niedrigen Ertrag (<30%). Erwägen Sie deren Entfernung.",
        "high_shading": "Starke Verschattung erkannt! Prüfen Sie die Verschattungs-Analyse.",
        "export_failed": "Export fehlgeschlagen! Versuchen Sie eine niedrigere Auflösung oder ein anderes Format.",
    }
    
    message = warnings.get(warning_type, f"Warnung: {warning_type}")
    if details:
        message += f"\n\n{details}"
    
    st.warning(message)
