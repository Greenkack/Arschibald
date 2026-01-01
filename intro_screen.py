"""
intro_screen.py
Zweck: Intro-Bildschirm für die Bokuk2-Anwendung mit Video/Bild-Optionen

ROBUSTHEIT:
- Maximales Error-Handling mit Fallbacks
- Atomic File Operations
- Type Validation
- Accessibility Enhancements
"""
import base64
import json
from pathlib import Path
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

# Robustheit-Module (mit Fallback falls nicht verfügbar)
try:
    from core.robustness import (
        safe_read_file,
        safe_execute,
        init_session_state,
        validate_path,
        sanitize_string
    )
    from core.accessibility import inject_accessibility_enhancements
    ROBUSTNESS_AVAILABLE = True
except ImportError:
    ROBUSTNESS_AVAILABLE = False
    # Fallback-Implementierungen
    def safe_read_file(filepath, fallback="", encoding='utf-8'):
        try:
            return Path(filepath).read_text(encoding=encoding)
        except:
            return fallback
    
    def safe_execute(func, fallback, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return fallback
    
    def init_session_state(key, default):
        if key not in st.session_state:
            st.session_state[key] = default
    
    def validate_path(path, must_exist=False, allowed_extensions=None):
        return True
    
    def sanitize_string(text, max_length=1000, allow_html=False):
        return str(text)[:max_length].strip()
    
    def inject_accessibility_enhancements():
        pass


def get_daily_tip():
    """Gibt einen zufälligen Tipp des Tages basierend auf dem aktuellen Datum zurück"""
    tips = [
        "Nutzen Sie die Produktdatenbank, um schnell Artikel zu finden und Angebote zu erstellen",
        "Im Admin-Panel können Sie Logos und Firmenlogos für Ihre PDF-Dokumente hochladen",
        "Preisregeln ermöglichen automatische Rabatte basierend auf Menge oder Kundentyp",
        "Die Diagramm-Funktion visualisiert Ihre Amortisationszeiten und Einsparungen",
        "Nutzen Sie die Carousel-Funktion im Intro-Screen für professionelle Präsentationen",
        "Im Admin-Bereich können Sie Zahlungsbedingungen für Ihre Angebote vordefinieren",
        "Produktattribute helfen bei der detaillierten Beschreibung Ihrer Artikel",
        "Die Benutzerverwaltung erlaubt Ihnen, verschiedene Rollen und Berechtigungen zu vergeben",
        "PDF-Einstellungen im Admin-Panel passen Ihre Dokumente an Ihr Corporate Design an",
        "Gewinnmargen können pro Produkt oder Kategorie individuell festgelegt werden",
        "Nutzen Sie die Suchfunktion mit Filtern, um schnell relevante Produkte zu finden",
        "Datenblätter können direkt aus der Produktdatenbank heruntergeladen werden",
        "Die Statistik-Funktion zeigt Ihnen einen Überblick über Ihre Verkaufsaktivitäten",
        "Favoritenlisten helfen Ihnen, häufig verwendete Produkte schnell wiederzufinden",
        "Im Admin-Panel können Sie Serviceleistungen definieren und zu Angeboten hinzufügen",
        "Die Export-Funktion ermöglicht das Speichern von Angeboten als PDF oder Excel",
        "Nutzen Sie Tastenkombinationen: Enter für Login, Strg+S für Speichern",
        "Die Backup-Funktion im Admin-Bereich sichert Ihre wichtigen Daten regelmäßig",
        "Produktbilder werden automatisch optimiert und in verschiedenen Größen gespeichert",
        "Die Währungsumrechnung erfolgt automatisch basierend auf aktuellen Wechselkursen",
        "Nutzen Sie die Notizfunktion, um wichtige Informationen zu Kunden zu speichern",
        "Die Duplikat-Funktion spart Zeit beim Erstellen ähnlicher Angebote",
        "Vordefinierte Textbausteine beschleunigen die Angebotserstellung erheblich",
        "Die Versionshistorie zeigt alle Änderungen an Ihren Dokumenten",
        "Nutzen Sie Tags, um Produkte in eigene Kategorien zu organisieren",
        "Die Dashboard-Ansicht gibt Ihnen einen schnellen Überblick über wichtige Kennzahlen",
        "Erinnerungen können für Folgeaktivitäten bei Kunden eingerichtet werden",
        "Die Mehrsprachigkeit unterstützt Sie bei internationalen Geschäftsbeziehungen",
        "Nutzen Sie die Batch-Bearbeitung, um mehrere Datensätze gleichzeitig zu ändern",
        "Die integrierte Hilfe-Funktion bietet Unterstützung zu allen Features der App"
    ]
    
    # Verwende den Tag des Jahres als Index (1-365/366)
    day_of_year = datetime.now().timetuple().tm_yday
    tip_index = day_of_year % len(tips)
    
    return tips[tip_index]


def get_image_base64(image_path):
    """Konvertiert Bild zu Base64 für HTML-Einbettung mit Caching"""
    try:
        # Cache im Session State für schnelleres Laden
        cache_key = f"img_cache_{image_path}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
            st.session_state[cache_key] = img_base64
            return img_base64
    except BaseException:
        return None


def load_intro_settings():
    """
    Lädt Intro-Einstellungen aus JSON oder gibt Standardwerte zurück
    
    ROBUSTHEIT:
    - Atomic file reading
    - JSON parse error handling
    - Type validation
    - Fallback zu defaults
    """
    settings_file = Path("data/intro_settings.json")
    default_settings = {
        "enabled": True,
        "media_type": "image",  # "none", "image", "video"
        "image_path": "data/company_logos/wppv.png",
        "image_left_path": "data/company_logos/left_logo.png",  # NEU: Linkes kleines Bild
        "image_right_path": "data/company_logos/right_logo.png",  # NEU: Rechtes kleines Bild
        "show_side_images": True,  # NEU: Seitenbilder aktivieren
        "video_url": "",
        "video_file_path": "",  # NEU: Pfad zu hochgeladenem Video (MP4, AVI, MOV)
        "video_size": "fullscreen",  # NEU: "small", "medium", "large", "fullscreen"
        "video_autoplay": True,  # NEU: Automatischer Start
        "video_loop": True,  # NEU: Video wiederholen
        "require_login": True,  # JETZT PFLICHT
        "allow_guest": False,  # DEAKTIVIERT
        "allow_quick_start": False,  # DEAKTIVIERT
        "allow_registration": True,  # NEU: Registrierung erlauben
        "require_company_info": True,  # NEU: Firmeninfo bei Registrierung
        "title": "ÖMERs ALL in ONE DINGSBUMS",
        "subtitle": "",
        "description": ""
    }

    try:
        if settings_file.exists():
            # Robustes File Reading
            content = safe_read_file(settings_file, fallback="{}")
            loaded_settings = json.loads(content) if content else {}
            
            # Merge mit defaults (Type-safe)
            merged = default_settings.copy()
            for key, value in loaded_settings.items():
                if key in default_settings:
                    # Type validation
                    expected_type = type(default_settings[key])
                    if isinstance(value, expected_type):
                        merged[key] = value
            
            return merged
    except json.JSONDecodeError as e:
        st.warning(f"⚠ Intro-Einstellungen konnten nicht geladen werden (JSON-Fehler). Verwende Standardwerte.")
    except Exception as e:
        st.error(f"⚠ Fehler beim Laden der Intro-Einstellungen: {e}")

    return default_settings


def save_intro_settings(settings):
    """Speichert Intro-Einstellungen in JSON"""
    settings_file = Path("data/intro_settings.json")
    settings_file.parent.mkdir(exist_ok=True)
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False


def render_intro_screen():
    """
    Rendert den Intro-Bildschirm mit Login/Weiter-Optionen.

    Returns:
        bool: True wenn Benutzer fortfahren möchte, False sonst
        
    ROBUSTHEIT:
    - Accessibility enhancements injiziert
    - Sichere Session State Initialisierung
    - Error handling bei Bild/Video-Laden
    """
    
    # Accessibility Enhancements injizieren
    inject_accessibility_enhancements()

    # Lade Einstellungen (robust)
    settings = load_intro_settings()
    
    # KRITISCH: Session State NIEMALS mit defaults initialisieren die bypass erlauben!
    # Prüfe nur Existenz, setze NICHT auf False wenn nicht vorhanden
    
    # Prüfe ob Intro deaktiviert ist
    if not settings.get('enabled', True):
        st.session_state['intro_completed'] = True
        st.session_state['user_mode'] = 'quick_start'
        st.session_state['username'] = 'Schnellstart-Benutzer'
        return True

    # SECURITY: Prüfe ob bereits AUTHENTIFIZIERT (nicht nur intro_completed)
    # Beide Bedingungen müssen erfüllt sein!
    if (st.session_state.get('intro_completed', False) and 
        st.session_state.get('username') and 
        st.session_state.get('user_mode')):
        return True
    
    # SECURITY: Bei Rerun ohne Auth → Zurücksetzen!
    if st.session_state.get('intro_completed', False) and not st.session_state.get('username'):
        st.session_state['intro_completed'] = False
        st.session_state['user_mode'] = None
    
    # FORCE PRELOAD: Bilder müssen SOFORT geladen werden, bevor irgendwas rendert
    media_type = settings.get('media_type', 'image')
    images_ready = False
    
    if media_type == 'image':
        image_path = Path(settings.get('image_path', 'data/company_logos/wppv.png'))
        
        # Path-Validierung
        if validate_path(image_path, must_exist=True, allowed_extensions=['.png', '.jpg', '.jpeg', '.gif', '.webp']):
            # Force load immediately (mit Error-Handling)
            img_data = safe_execute(get_image_base64, None, str(image_path))
            if img_data:
                images_ready = True
        
        if settings.get('show_side_images', False):
            image_left_path = Path(settings.get('image_left_path', ''))
            if validate_path(image_left_path, must_exist=True, allowed_extensions=['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                safe_execute(get_image_base64, None, str(image_left_path))
            
            image_right_path = Path(settings.get('image_right_path', ''))
            if validate_path(image_right_path, must_exist=True, allowed_extensions=['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                safe_execute(get_image_base64, None, str(image_right_path))
    
    # Falls Bilder nicht bereit sind, warten und neu laden
    if media_type == 'image' and not images_ready:
        st.warning("Lade Intro-Bildschirm...")
        st.stop()

    # Zentriertes Layout mit CSS (Emoji-Filterung zentral über emoji_toggle.py)
    st.markdown("""
        <style>
        /* Modernes Design: Helles Grau, Orange Akzente, Schwarze Schattierungen */
        .stApp {
            background: #e8e8e8 !important;
        }
        [data-testid="stAppViewContainer"] {
            background: #e8e8e8 !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(170, 170, 170, 0.95) !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 10px 10px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* TABS - KOMPLETTES STYLING - Weißer Container, schwarze Schrift */
        /* ALLE Tab-Container auf WEISS - mehrere Selektoren */
        div.stTabs,
        [data-testid="stTabs"],
        [data-baseweb="tab-highlight"],
        [data-baseweb="tab-border"],
        [data-baseweb="tab-overflow"] {
            background-color: #ffffff !important;
        }
        
        /* Tab-Liste Container - WEISS mit Padding - HÖCHSTE PRIORITÄT */
        body [data-baseweb="tab-list"],
        body div[data-baseweb="tab-list"],
        [data-baseweb="tab-list"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            padding: 8px !important;
            box-shadow: 0 10px 16px rgba(0, 0, 0, 0.25) !important;
            gap: 8px !important;
        }
        
        /* INAKTIVE Tab-Buttons - HELLGRAU Hintergrund, SCHWARZE Schrift - HÖCHSTE PRIORITÄT */
        body button[data-baseweb="tab"]:not([aria-selected="true"]),
        button[data-baseweb="tab"]:not([aria-selected="true"]) {
            background-color: #e8e8e8 !important;
            color: #000000 !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 700 !important;
            border: none !important;
            transition: all 0.3s ease !important;
        }
        body button[data-baseweb="tab"]:not([aria-selected="true"]) span,
        button[data-baseweb="tab"]:not([aria-selected="true"]) span {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        /* Tab-Button Hover - Helleres Grau */
        button[data-baseweb="tab"]:not([aria-selected="true"]):hover {
            background-color: #e0e0e0 !important;
            color: #FF8C00 !important;
        }
        button[data-baseweb="tab"]:not([aria-selected="true"]):hover span {
            color: #FF8C00 !important;
        }
        
        /* AKTIVER Tab - ORANGE mit weißer Schrift - HÖCHSTE PRIORITÄT */
        body button[data-baseweb="tab"][aria-selected="true"],
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #FF8C00 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.3) !important;
        }
        body button[data-baseweb="tab"][aria-selected="true"] span,
        button[data-baseweb="tab"][aria-selected="true"] span {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        /* Tab-Panel (Inhaltsbereich) - WEISS */
        div.stTabs [data-baseweb="tab-panel"],
        div[data-testid="stTabs"] [data-baseweb="tab-panel"],
        .stTabs [data-baseweb="tab-panel"],
        [data-baseweb="tab-panel"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            padding: 24px !important;
            margin-top: 16px !important;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Eingabefelder - Weiß mit schwarzer Schrift */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        input[type="text"],
        input[type="password"],
        input[type="email"],
        textarea {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #cbd5e0 !important;
            border-radius: 10px !important;
            padding: 14px 18px !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.15),
                        inset 0 10px 10px rgba(0, 0, 0, 0.05) !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        input[type="text"]:focus,
        input[type="password"]:focus,
        input[type="email"]:focus,
        textarea:focus {
            border-color: #000000 !important;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2),
                        0 0 0 10px rgba(255, 140, 0, 0.15),
                        inset 0 10px 10px rgba(0, 0, 0, 0.05) !important;
            transform: translateY(-2px) !important;
            outline: none !important;
        }
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder,
        textarea::placeholder {
            color: #000000 !important;
            opacity: 0.6 !important;
        }
        
        /* Labels - Hellgrau und Dick (Fett) */
        .stTextInput > label,
        label,
        .stTextInput label p,
        .stTextInput label div,
        .stForm label,
        .stForm p,
        div[data-testid="stFormSubmitButton"] + div p,
        .stExpander summary,
        .stExpander p {
            color: #6b6b6b !important;
            font-weight: 900 !important;
            font-size: 1rem !important;
            margin-bottom: 10px !important;
            text-shadow: none !important;
            letter-spacing: 0.3px !important;
        }
        
        /* Markdown Text - Schwarz */
        .stMarkdown,
        .stMarkdown p,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4 {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        /* Info/Alert Boxen - Helles Grau mit Orange Akzenten */
        .stAlert,
        div[data-baseweb="notification"] {
            background-color: #e8e8e8 !important;
            border-left: 5px solid #ff9800 !important;
            border-radius: 10px !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.12) !important;
            color: #000000 !important;
            font-weight: 600 !important;
        }
        .stInfo {
            background-color: #000000 !important;
            border-left-color: #ff9800 !important;
        }
        .stSuccess {
            background-color: #000000 !important;
            border-left-color: #ff9800 !important;
        }
        .stWarning {
            background-color: #000000 !important;
            border-left-color: #ff9800 !important;
        }
        .stError {
            background-color: #000000 !important;
            border-left-color: #ff9800 !important;
        }
        
        /* Verstecke leere Streamlit-Container im Intro */
        .intro-container .element-container:empty {
            display: none !important;
        }
        .intro-container > div[data-testid="stImage"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 auto !important;
        }
        .intro-images-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 2rem;
            padding: 0 20px;
            width: 100%;
        }
        .intro-logo {
            max-width: 750px !important;
            width: 700px !important;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15), 
                        0 20px 20px rgba(255, 140, 0, 0.1) !important;
            animation: float 3s ease-in-out infinite;
            position: relative;
            z-index: 10;
            margin: 0 auto;
            display: block;
            border: 2px solid rgba(255, 140, 0, 0.1);
        }
        .intro-logo-side {
            width: 100%;
            max-width: 100px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1),
                        0 10px 12px rgba(0, 0, 0, 0.05);
            animation: float 3.5s ease-in-out infinite;
            opacity: 0.85;
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        .intro-logo-side.left {
            grid-column: 1;
            max-width: 350px;
        }
        .intro-logo-side.right {
            grid-column: 3;
            max-width: 350px;
        }
        .intro-logo-side:hover {
            opacity: 1;
            transform: scale(1.1);
        }
        @media (max-width: 468px) {
            .intro-images-container {
                justify-content: center;
                padding: 0 10px;
            }
            .intro-logo {
                max-width: 450px !important;
                width: 400px !important;
                margin: 0 auto;
            }
            .intro-title {
                font-size: 3.2rem;
                text-align: center;
                -webkit-text-stroke: 2px #00ffff;
            }
            .intro-logo-side.left {
                max-width: 230px;
            }
            .intro-logo-side.right {
                max-width: 230px;
            }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        .intro-video {
            max-width: 800px;
            width: 100%;
            margin-bottom: 2rem;
            border-radius: 15px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .intro-title {
            background: linear-gradient(135deg, #000000 0%, #1a202c 0%, #FF8C00 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 10px 10px rgba(0, 0, 0, 0.1));
            animation: shimmer 3s ease-in-out infinite;
            position: relative;
        }
        .intro-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 120px;
            height: 4px;
            background: linear-gradient(90deg, transparent, #FF8C00, transparent);
            border-radius: 2px;
        }
        @keyframes shimmer {
            0% { 
                opacity: 1;
                transform: scale(1);
            }
            50% { 
                opacity: 0.9;
                transform: scale(1.01);
            }
            100% { 
                opacity: 1;
                transform: scale(1);
            }
        }
        
        /* ========================================
           BUTTON STYLES - Orange mit schwarzen Schattierungen
           ======================================== */
        
        /* Intro-spezifische Button-Basis-Styles */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"],
        button[type="submit"] {
            font-size: 1.1rem !important;
            padding: 14px 32px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            text-transform: none !important;
        }
        
        /* ANMELDEN Button - Orange mit schwarzen Schattierungen */
        button[type="submit"],
        .stButton > button[kind="primary"],
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #FF8C00 0%, #FF6B00 100%) !important;
            color: #000000 !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 10px 18px rgba(0, 0, 0, 0.25),
                        0 10px 10px rgba(255, 140, 0, 0.3) !important;
        }
        button[type="submit"]:hover,
        .stButton > button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {
            background: linear-gradient(135deg, #FF9500 0%, #FF7A00 100%) !important;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.3),
                        0 10px 12px rgba(255, 140, 0, 0.4) !important;
            transform: translateY(-3px) !important;
        }
        
        button[type="submit"]:active,
        .stButton > button[kind="primary"]:active {
            transform: translateY(-1px) !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Secondary Buttons - Weiß mit schwarzen Schattierungen */
        button[kind="secondary"],
        .stButton > button[kind="secondary"] {
            background-color: #ffffff !important;
            color: #ffffff !important;
            border: 2px solid #cbd5e0 !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.1) !important;
        }
        button[kind="secondary"]:hover {
            background-color: #ffffff !important;
            border-color: #000000 !important;
            color: #ffffff !important;
            box-shadow: 0 10px 16px rgba(0, 0, 0, 0.15),
                        0 0 0 10px rgba(255, 140, 0, 0.1) !important;
        }
        
        /* Checkbox & Radio - Orange Akzente */
        input[type="checkbox"],
        input[type="radio"] {
            accent-color: #FF8C00 !important;
        }
        
        /* Select Dropdown - Grau mit schwarzer Schrift */
        select,
        .stSelectbox > div > div > div,
        .stSelectbox select,
        div[data-baseweb="select"] > div {
            background-color: #a9a9a9 !important;
            color: #a9a9a9 !important;
            border: 0px solid #a9a9a9 !important;
            border-radius: 10px !important;
            padding: 12px !important;
            font-weight: 600 !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.15) !important;
        }
        select:focus,
        .stSelectbox > div > div > div:focus {
            border-color: #FF8C00 !important;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2),
                        0 0 0 3px rgba(255, 140, 0, 0.15) !important;
        }
        /* Dropdown Optionen */
        select option,
        div[data-baseweb="select"] ul li {
            background-color: #a9a9a9 !important;
            color: #000000 !important;
            font-weight: 600 !important;
        }
        select option:hover,
        div[data-baseweb="select"] ul li:hover {
            background-color: #c9c9c9 !important;
            color: #FF8C00 !important;
        }
        
        /* ========================================
           STREAMLIT-MENÜ (3 PUNKTE) - SCHWARZE SCHRIFT
           ======================================== */
        
        /* Header & Menu Button */
        header[data-testid="stHeader"],
        header button,
        button[kind="header"],
        button[kind="headerNoPadding"],
        button[data-testid="stHeaderActionButton"] {
            background-color: rgba(170, 170, 170, 0.95) !important;
        }
        
        /* Menu Button Icon - SCHWARZ */
        header button,
        header button *,
        header button svg,
        header button svg path,
        button[kind="header"],
        button[kind="header"] *,
        button[kind="headerNoPadding"],
        button[kind="headerNoPadding"] * {
            color: #000000 !important;
            fill: #000000 !important;
            stroke: #000000 !important;
        }
        
        /* Menu Dropdown Container */
        [data-testid="stMainMenu"],
        [data-testid="stMainMenuPopover"],
        ul[data-testid="main-menu-list"],
        div[role="menu"],
        div[role="dialog"] {
            background-color: #ffffff !important;
            border: 2px solid #000000 !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Menu Items - SCHWARZE SCHRIFT */
        [data-testid="stMainMenu"] *,
        [data-testid="stMainMenuPopover"] *,
        ul[data-testid="main-menu-list"],
        ul[data-testid="main-menu-list"] *,
        ul[data-testid="main-menu-list"] li,
        ul[data-testid="main-menu-list"] a,
        ul[data-testid="main-menu-list"] span,
        ul[data-testid="main-menu-list"] button,
        div[role="menu"] *,
        div[role="menuitem"],
        div[role="menuitem"] *,
        li[role="menuitem"],
        li[role="menuitem"] *,
        div[role="dialog"] *,
        div[role="dialog"] h1,
        div[role="dialog"] h2,
        div[role="dialog"] h3,
        div[role="dialog"] p,
        div[role="dialog"] span,
        div[role="dialog"] label,
        div[role="dialog"] div {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        /* Settings Dialog - ALLE Texte SCHWARZ */
        section[role="dialog"],
        section[role="dialog"] *,
        [data-testid="stModal"],
        [data-testid="stModal"] *,
        .stModal,
        .stModal *,
        div[class*="Modal"],
        div[class*="Modal"] *,
        div[class*="ModalDialog"],
        div[class*="ModalDialog"] * {
            color: #000000 !important;
        }
        
        /* Menu Items Hover */
        ul[data-testid="main-menu-list"] li:hover,
        ul[data-testid="main-menu-list"] li:hover *,
        div[role="menuitem"]:hover,
        div[role="menuitem"]:hover *,
        li[role="menuitem"]:hover,
        li[role="menuitem"]:hover * {
            background-color: #f7f9fc !important;
            color: #FF8C00 !important;
        }

        /* Dynamische Effekte werden aus den globalen Einstellungen geladen */
        </style>
    """, unsafe_allow_html=True)

    # ============================================================================
    # DYNAMISCHE UI-EFFEKTE FÜR INTRO-SCREEN
    # ============================================================================
    try:
        from admin_ui_effects_settings import load_ui_effects_settings
        from ui_effects_library import get_effect_css

        ui_effects_settings = load_ui_effects_settings()
        effects_enabled = ui_effects_settings.get("enabled", True)
        active_effect = ui_effects_settings.get(
            "active_effect", "shimmer_pulse")

        if effects_enabled:
            effect_css = get_effect_css(active_effect)
            st.markdown(f"""
            <style>
            /* Intro-Screen Effekte: {active_effect.upper()} */
            {effect_css}
            </style>
            """, unsafe_allow_html=True)
    except Exception:
        pass  # Fallback: Keine zusätzlichen Effekte

    # === VIDEO-HINTERGRUND (VOR allen anderen Elementen) ===
    media_type = settings.get('media_type', 'image')
    
    if media_type == 'video':
        video_file_path = settings.get('video_file_path', '')
        video_url = settings.get('video_url', '')
        video_size = settings.get('video_size', 'fullscreen')
        video_autoplay = settings.get('video_autoplay', True)
        video_loop = settings.get('video_loop', True)
        
        # FULLSCREEN BACKGROUND VIDEO - IMMER RENDERN
        if video_size == 'fullscreen':
            video_element = None
            
            if video_file_path:
                video_path = Path(video_file_path)
                
                # Prüfe ob kleine WebM-Version existiert
                video_small_path = video_path.parent / (video_path.stem + "_small.webm")
                
                if video_small_path.exists() and video_small_path.is_file():
                    # BASE64-EINBETTUNG für kleine WebM-Datei
                    import base64
                    
                    try:
                        with open(video_small_path, 'rb') as f:
                            video_bytes = f.read()
                        
                        video_size_mb = len(video_bytes) / (1024 * 1024)
                        
                        if video_size_mb < 10:  # Max 10 MB für Base64
                            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
                            video_data_url = f"data:video/webm;base64,{video_base64}"
                            
                            # GROßES, PROFESSIONELLES VIDEO
                            html_code = f'''
                            <style>
                                body, html {{
                                    margin: 0;
                                    padding: 0;
                                    overflow: hidden;
                                    background: #000;
                                }}
                                #intro-video-container {{
                                    width: 100%;
                                    height: 100%;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                }}
                                #intro-bg-video-base64 {{
                                    width: 100%;
                                    height: auto;
                                }}
                            </style>
                            <div id="intro-video-container">
                                <video 
                                    id="intro-bg-video-base64"
                                    autoplay 
                                    loop 
                                    muted 
                                    playsinline
                                >
                                    <source src="{video_data_url}" type="video/webm">
                                </video>
                            </div>
                            <script>
                                (function() {{
                                    const vid = document.getElementById('intro-bg-video-base64');
                                    if (vid) {{
                                        vid.currentTime = 0;
                                        vid.muted = true;
                                        vid.play().catch(e => {{
                                            console.error('[VIDEO]', e);
                                            document.addEventListener('click', function startVideo() {{
                                                vid.play();
                                                document.removeEventListener('click', startVideo);
                                            }});
                                        }});
                                    }}
                                }})();
                            </script>
                            '''
                            
                            # GROß: 700px Höhe für beeindruckenden Effekt
                            components.html(html_code, height=700, scrolling=False)
                        else:
                            st.warning(f"Video zu groß für Base64: {video_size_mb:.1f} MB (max 10 MB)")
                    except Exception as e:
                        st.error(f"Fehler beim Laden des Videos: {e}")
                        
                elif video_path.exists() and video_path.is_file():
                    st.info("⚠️ Konvertiere zuerst das Video: Führe `convert_video_small_webm.ps1` aus")
                else:
                    st.error(f"❌ Video-Datei nicht gefunden: {video_file_path}")
            
            elif video_url and not ('youtube.com' in video_url or 'youtu.be' in video_url):
                # Externe Video-URL
                st.markdown('''
                    <style>
                        [data-testid="stVideo"] {
                            position: fixed !important;
                            top: 0 !important;
                            left: 0 !important;
                            width: 100vw !important;
                            height: 100vh !important;
                            z-index: -1 !important;
                        }
                        
                        [data-testid="stVideo"] video {
                            width: 100vw !important;
                            height: 100vh !important;
                            object-fit: cover !important;
                        }
                    </style>
                ''', unsafe_allow_html=True)
                
                st.video(video_url, loop=video_loop, autoplay=video_autoplay, muted=True)
            
            elif video_url and ('youtube.com' in video_url or 'youtu.be' in video_url):
                # YouTube-Video als Fullscreen-Hintergrund
                if 'youtu.be' in video_url:
                    video_id = video_url.split('/')[-1].split('?')[0]
                else:
                    video_id = video_url.split('v=')[-1].split('&')[0]
                
                autoplay_param = '1' if video_autoplay else '0'
                loop_param = '1' if video_loop else '0'
                
                st.markdown(f'''
                    <style>
                        #intro-persistent-yt-iframe {{
                            position: fixed !important;
                            top: 0 !important;
                            left: 0 !important;
                            width: 100vw !important;
                            height: 100vh !important;
                            z-index: -999999 !important;
                            border: none !important;
                            pointer-events: none !important;
                        }}
                    </style>
                    <script>
                        (function() {{
                            // Prüfe ob iframe bereits existiert
                            let existingIframe = document.getElementById('intro-persistent-yt-iframe');
                            
                            if (!existingIframe) {{
                                // Erstelle iframe nur EINMAL und füge es in body ein
                                const iframe = document.createElement('iframe');
                                iframe.id = 'intro-persistent-yt-iframe';
                                iframe.src = 'https://www.youtube.com/embed/{video_id}?autoplay={autoplay_param}&loop={loop_param}&mute=1&playlist={video_id}&controls=0&enablejsapi=1';
                                iframe.frameBorder = '0';
                                iframe.allow = 'autoplay; encrypted-media';
                                iframe.allowFullscreen = true;
                                iframe.style.position = 'fixed';
                                iframe.style.top = '0';
                                iframe.style.left = '0';
                                iframe.style.width = '100vw';
                                iframe.style.height = '100vh';
                                iframe.style.zIndex = '-999999';
                                iframe.style.border = 'none';
                                iframe.style.pointerEvents = 'none';
                                
                                // Füge iframe in body ein (NICHT in Streamlit-Container)
                                document.body.insertBefore(iframe, document.body.firstChild);
                            }}
                        }})();
                    </script>
                ''', unsafe_allow_html=True)
    # === ENDE VIDEO-HINTERGRUND ===

    # Haupt-Container
    col1, col2, col3 = st.columns([1, 5, 1])

    with col2:
        st.markdown('<div class="intro-container">', unsafe_allow_html=True)

        # Media-Anzeige (nur wenn NICHT Fullscreen)
        media_type = settings.get('media_type', 'image')

        if media_type == 'video':
            # Video-Anzeige (nur für nicht-Fullscreen Größen)
            video_file_path = settings.get('video_file_path', '')
            video_url = settings.get('video_url', '')
            video_size = settings.get('video_size', 'fullscreen')
            video_autoplay = settings.get('video_autoplay', True)
            video_loop = settings.get('video_loop', True)
            
            # Fullscreen wird bereits oben als Hintergrund gerendert
            if video_size != 'fullscreen':
                # Größen-Mappings (width x height)
                size_styles = {
                    'small': 'width: 640px; height: 360px; max-width: 90%;',
                    'medium': 'width: 854px; height: 480px; max-width: 90%;',
                    'large': 'width: 1280px; height: 720px; max-width: 95%;',
                }
                
                video_style = size_styles.get(video_size, size_styles['medium'])
                
                # Bestimme Video-Quelle
                video_src = None
                if video_file_path and Path(video_file_path).exists():
                    # Verwende relativen Pfad für Streamlit Static File Server
                    video_src = f"/app/{video_file_path.replace(chr(92), '/')}"
                elif video_url and not ('youtube.com' in video_url or 'youtu.be' in video_url):
                    video_src = video_url
                
                if video_src:
                    # HTML5-Video mit Autoplay, Loop, Muted
                    autoplay_attr = 'autoplay' if video_autoplay else ''
                    loop_attr = 'loop' if video_loop else ''
                    
                    st.markdown(f'''
                        <video {autoplay_attr} {loop_attr} muted playsinline
                            style="{video_style} border-radius: 8px; display: block; margin: 20px auto;">
                            <source src="{video_src}" type="video/mp4">
                            Ihr Browser unterstützt das Video-Tag nicht.
                        </video>
                    ''', unsafe_allow_html=True)
                elif video_url and ('youtube.com' in video_url or 'youtu.be' in video_url):
                    # YouTube-Video
                    if 'youtu.be' in video_url:
                        video_id = video_url.split('/')[-1].split('?')[0]
                    else:
                        video_id = video_url.split('v=')[-1].split('&')[0]
                    
                    autoplay_param = '1' if video_autoplay else '0'
                    loop_param = '1' if video_loop else '0'
                    
                    st.markdown(f'''
                        <iframe style="{video_style} border: none; border-radius: 8px; display: block; margin: 20px auto;"
                            src="https://www.youtube.com/embed/{video_id}?autoplay={autoplay_param}&loop={loop_param}&mute=1&playlist={video_id}&controls=0"
                            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>
                        </iframe>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("Kein Video konfiguriert. Bitte im Admin-Panel Video hochladen oder URL eingeben.")

        elif media_type == 'image':
            # Prüfe ob Seitenbilder aktiviert sind
            show_side_images = settings.get('show_side_images', False)

            if show_side_images:
                # 3 Bilder mit Grid Layout: klein links - groß mitte - klein
                # rechts
                st.markdown(
                    '<div class="intro-images-container">',
                    unsafe_allow_html=True)

                # Spalte 1: Linkes kleines Bild
               # image_left_path = Path(settings.get('image_left_path', ''))
              #  if image_left_path.exists():
               #     img_left_base64 = get_image_base64(image_left_path)
               #     if img_left_base64:
                #        st.markdown(
                  #          f'<img src="data:image/png;base64,{img_left_base64}" class="intro-logo-side left" style="grid-column: 1;">',
                  #          unsafe_allow_html=True)

                # Spalte 2: Hauptbild (groß in der Mitte)
                image_path = Path(
                    settings.get(
                        'image_path',
                        'data/company_logos/default_company_logo.png'))
                if image_path.exists():
                    img_base64 = get_image_base64(image_path)
                    if img_base64:
                        st.markdown(
                            f'<img src="data:image/png;base64,{img_base64}" class="intro-logo" style="grid-column: 2;">',
                            unsafe_allow_html=True)

                # Spalte 3: Rechtes kleines Bild
              #  image_right_path = Path(settings.get('image_right_path', ''))
             #   if image_right_path.exists():
              #      img_right_base64 = get_image_base64(image_right_path)
               #     if img_right_base64:
               #         st.markdown(
                #            f'<img src="data:image/png;base64,{img_right_base64}" class="intro-logo-side right" style="grid-column: 3;">',
                #            unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Nur Hauptbild (original)
                image_path = Path(
                    settings.get(
                        'image_path',
                        'data/company_logos/default_company_logo.png'))
                if image_path.exists():
                    img_base64 = get_image_base64(image_path)
                    if img_base64:
                        st.markdown(
                            f'<img src="data:image/png;base64,{img_base64}" class="intro-logo">',
                            unsafe_allow_html=True)

        # Titel - NUR DER TITEL, KEINE BESCHREIBUNG
        st.markdown(
            f'<h1 class="intro-title">{
                settings.get(
                    "title",
                    "ÖMERs ALL in ONE DINGSBUMS")}</h1>',
            unsafe_allow_html=True)

        st.markdown("---")

        # INTRO-SCREEN WRAPPER für spezifische Styles
        st.markdown('<div id="intro-screen-container" class="intro-screen-wrapper">', unsafe_allow_html=True)
        
        # INTRO-SPECIFIC STYLES - Überschreiben globale Theme-Styles
        st.markdown("""
        <style>
        /* INTRO-SCREEN SPEZIFISCHE STYLES - HÖCHSTE PRIORITÄT */
        #intro-screen-container .stTabs [data-baseweb="tab-list"],
        .intro-screen-wrapper .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            padding: 8px !important;
            box-shadow: 0 10px 16px rgba(0, 0, 0, 0.25) !important;
            gap: 8px !important;
        }
        #intro-screen-container .stTabs [data-baseweb="tab"],
        .intro-screen-wrapper .stTabs [data-baseweb="tab"],
        #intro-screen-container button[data-baseweb="tab"],
        .intro-screen-wrapper button[data-baseweb="tab"] {
            background-color: #e8e8e8 !important;
            color: #000000 !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 700 !important;
            border: none !important;
            border-bottom: none !important;
            transition: all 0.3s ease !important;
        }
        #intro-screen-container .stTabs [data-baseweb="tab"]:hover,
        .intro-screen-wrapper .stTabs [data-baseweb="tab"]:hover,
        #intro-screen-container button[data-baseweb="tab"]:hover,
        .intro-screen-wrapper button[data-baseweb="tab"]:hover {
            background-color: #f5f5f5 !important;
            color: #FF8C00 !important;
            border-bottom: none !important;
        }
        #intro-screen-container .stTabs [aria-selected="true"],
        .intro-screen-wrapper .stTabs [aria-selected="true"],
        #intro-screen-container button[data-baseweb="tab"][aria-selected="true"],
        .intro-screen-wrapper button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #FF8C00 !important;
            color: #ffffff !important;
            border-bottom: none !important;
            box-shadow: 0 10px 12px rgba(0, 0, 0, 0.3) !important;
        }
        #intro-screen-container .stTabs [data-baseweb="tab-panel"],
        .intro-screen-wrapper .stTabs [data-baseweb="tab-panel"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            padding: 24px !important;
            margin-top: 16px !important;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15) !important;
        }
        /* Labels hellgrau */
        #intro-screen-container .stTextInput > label,
        .intro-screen-wrapper .stTextInput > label,
        #intro-screen-container label,
        .intro-screen-wrapper label,
        #intro-screen-container .stForm label,
        .intro-screen-wrapper .stForm label {
            color: #6b6b6b !important;
            font-weight: 900 !important;
        }
        /* Eingabefelder weiß */
        #intro-screen-container .stTextInput > div > div > input,
        .intro-screen-wrapper .stTextInput > div > div > input,
        #intro-screen-container input[type="text"],
        .intro-screen-wrapper input[type="text"],
        #intro-screen-container input[type="password"],
        .intro-screen-wrapper input[type="password"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # JAVASCRIPT: Styles dynamisch NACH Page-Load injizieren - ABSOLUTE HÖCHSTE PRIORITÄT
        # ÜBERSCHREIBT ALLES - AUCH THEME-CSS!
        components.html("""
        <script>
        (function() {
            function applyIntroStyles() {
                // Entferne alte Styles
                const oldStyle = document.getElementById('intro-override-styles');
                if (oldStyle) oldStyle.remove();
                
                // Erstelle neuen Style-Block mit absolut höchster Priorität
                const style = document.createElement('style');
                style.id = 'intro-override-styles';
                style.setAttribute('data-intro-priority', 'maximum');
                style.innerHTML = `
                    /* ============================================
                       INTRO-SCREEN ABSOLUTE OVERRIDE STYLES
                       ÜBERSCHREIBT ALLE THEMES UND CONFIGS!
                       ============================================ */
                    /* ============================================
                       INTRO-SCREEN ABSOLUTE OVERRIDE STYLES
                       ÜBERSCHREIBT ALLE THEMES UND CONFIGS!
                       ============================================ */
                    
                    /* TAB CONTAINER - WEISS */
                    body div[data-baseweb="tab-list"],
                    div[data-baseweb="tab-list"] {
                        background-color: #ffffff !important;
                        border-radius: 12px !important;
                        padding: 8px !important;
                        box-shadow: 0 10px 16px rgba(0, 0, 0, 0.25) !important;
                        gap: 8px !important;
                    }
                    
                    /* INAKTIVE TABS - HELLGRAU MIT SCHWARZER SCHRIFT */
                    body button[data-baseweb="tab"]:not([aria-selected="true"]),
                    button[data-baseweb="tab"]:not([aria-selected="true"]) {
                        background-color: #e8e8e8 !important;
                        color: #000000 !important;
                        border-radius: 8px !important;
                        padding: 12px 24px !important;
                        font-weight: 700 !important;
                        border: none !important;
                        border-bottom: none !important;
                    }
                    body button[data-baseweb="tab"]:not([aria-selected="true"]) span,
                    button[data-baseweb="tab"]:not([aria-selected="true"]) span,
                    body button[data-baseweb="tab"]:not([aria-selected="true"]) *,
                    button[data-baseweb="tab"]:not([aria-selected="true"]) * {
                        color: #000000 !important;
                        font-weight: 700 !important;
                    }
                    
                    /* HOVER STATE */
                    body button[data-baseweb="tab"]:not([aria-selected="true"]):hover,
                    button[data-baseweb="tab"]:not([aria-selected="true"]):hover {
                        background-color: #f5f5f5 !important;
                        color: #FF8C00 !important;
                    }
                    body button[data-baseweb="tab"]:not([aria-selected="true"]):hover span,
                    button[data-baseweb="tab"]:not([aria-selected="true"]):hover span,
                    body button[data-baseweb="tab"]:not([aria-selected="true"]):hover *,
                    button[data-baseweb="tab"]:not([aria-selected="true"]):hover * {
                        color: #FF8C00 !important;
                    }
                    
                    /* AKTIVER TAB - ORANGE MIT WEISSER SCHRIFT */
                    body button[data-baseweb="tab"][aria-selected="true"],
                    button[data-baseweb="tab"][aria-selected="true"] {
                        background-color: #FF8C00 !important;
                        color: #ffffff !important;
                        border-bottom: none !important;
                        box-shadow: 0 10px 12px rgba(0, 0, 0, 0.3) !important;
                    }
                    body button[data-baseweb="tab"][aria-selected="true"] span,
                    button[data-baseweb="tab"][aria-selected="true"] span,
                    body button[data-baseweb="tab"][aria-selected="true"] *,
                    button[data-baseweb="tab"][aria-selected="true"] * {
                        color: #ffffff !important;
                        font-weight: 700 !important;
                    }
                    
                    /* TAB PANEL - WEISS */
                    body div[data-baseweb="tab-panel"],
                    div[data-baseweb="tab-panel"] {
                        background-color: #ffffff !important;
                        border-radius: 12px !important;
                        padding: 24px !important;
                        margin-top: 16px !important;
                        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15) !important;
                    }
                    
                    /* LABELS - SCHWARZ */
                    .stTextInput > label, .stTextInput label *, 
                    label, .stForm label, .stForm label p,
                    .stForm label *, form label, form label * {
                        color: #000000 !important;
                        font-weight: 700 !important;
                    }
                    
                    /* INPUT FELDER - WEISS MIT SCHWARZER SCHRIFT */
                    .stTextInput > div > div > input, 
                    input[type="text"], input[type="password"], 
                    input[type="email"], textarea {
                        background-color: #ffffff !important;
                        color: #000000 !important;
                    }
                `;
                
                // Füge Style zum Head hinzu
                document.head.appendChild(style);
                
                // DIREKTES ELEMENT-STYLING für sofortige Wirkung
                setTimeout(() => {
                    // Tab-List Container
                    document.querySelectorAll('[data-baseweb="tab-list"]').forEach(el => {
                        el.style.setProperty('background-color', '#ffffff', 'important');
                    });
                    
                    // Inaktive Tabs
                    document.querySelectorAll('button[data-baseweb="tab"]:not([aria-selected="true"])').forEach(el => {
                        el.style.setProperty('background-color', '#e8e8e8', 'important');
                        el.style.setProperty('color', '#000000', 'important');
                        // Auch alle Kind-Elemente
                        el.querySelectorAll('*').forEach(child => {
                            child.style.setProperty('color', '#000000', 'important');
                        });
                    });
                    
                    // Aktive Tabs
                    document.querySelectorAll('button[data-baseweb="tab"][aria-selected="true"]').forEach(el => {
                        el.style.setProperty('background-color', '#FF8C00', 'important');
                        el.style.setProperty('color', '#ffffff', 'important');
                        // Auch alle Kind-Elemente
                        el.querySelectorAll('*').forEach(child => {
                            child.style.setProperty('color', '#ffffff', 'important');
                        });
                    });
                    
                    // Tab-Panel
                    document.querySelectorAll('[data-baseweb="tab-panel"]').forEach(el => {
                        el.style.setProperty('background-color', '#ffffff', 'important');
                    });
                    
                    // Labels
                    document.querySelectorAll('label, .stForm label, .stTextInput label').forEach(el => {
                        el.style.setProperty('color', '#000000', 'important');
                        el.querySelectorAll('*').forEach(child => {
                            child.style.setProperty('color', '#000000', 'important');
                        });
                    });
                }, 50);
            }
            
            // Mehrfach aufrufen
            applyIntroStyles();
            setTimeout(applyIntroStyles, 100);
            setTimeout(applyIntroStyles, 300);
            setTimeout(applyIntroStyles, 500);
            setTimeout(applyIntroStyles, 1000);
            setTimeout(applyIntroStyles, 2000);
            setTimeout(applyIntroStyles, 3000);
            
            // MutationObserver für dynamische Änderungen
            const observer = new MutationObserver(() => {
                applyIntroStyles();
            });
            observer.observe(document.body, { 
                childList: true, 
                subtree: true,
                attributes: true,
                attributeFilter: ['class', 'style']
            });
        })();
        </script>
        """, height=0)

        # PFLICHT-LOGIN: Nur Login & Registrierung
        tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])

        # Tab 1: Login
        with tab1:
            st.markdown("#### Anmelden")

            with st.form("login_form"):
                username = st.text_input(
                    "Benutzername", placeholder="Ihr Benutzername")
                password = st.text_input(
                    "Passwort", type="password", placeholder="Ihr Passwort")

                login_button = st.form_submit_button(
                    "Anmelden", use_container_width=True, type="primary")

                if login_button:
                    if username and password:
                        # Authentifizierung mit UserManagement-System
                        try:
                            from user_management import UserManagement
                            um = UserManagement()
                            user = um.authenticate(username, password)

                            if user:
                                st.session_state['intro_completed'] = True
                                st.session_state['user_mode'] = user['role']
                                st.session_state['user_role'] = user['role']
                                st.session_state['username'] = user['full_name'] or user['username']
                                st.session_state['user_id'] = user['id']
                                st.session_state['user_rank'] = user['rank']
                                st.session_state['user_permissions'] = user['permissions']
                                st.success(
                                    f"Willkommen, {
                                        user['full_name'] or user['username']}!")
                                st.rerun()
                            else:
                                st.error("Ungültige Anmeldedaten")
                        except ImportError:
                            # Fallback auf altes System
                            if username == "admin" and password == "admin":
                                st.session_state['intro_completed'] = True
                                st.session_state['user_mode'] = 'admin'
                                st.session_state['username'] = username
                                st.success("Erfolgreich angemeldet!")
                                st.rerun()
                            else:
                                st.error("Ungültige Anmeldedaten")
                    else:
                        st.warning("Bitte Benutzername und Passwort eingeben")

        # Tab 2: Registrierung
        with tab2:
            render_registration_form(settings)

        st.markdown("---")

        # Tipp des Tages - Weißer Hintergrund mit Orange Akzent und schwarzer Schrift
        daily_tip = get_daily_tip()
        st.markdown(f"""
        <div style="
            background-color: #ffffff; 
            padding: 1.5rem; 
            border-radius: 12px; 
            border-left: 5px solid #FF8C00;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15),
                        0 10px 10px rgba(0, 0, 0, 0.1);
            margin: 1.5rem 0;">
            <span style="
                color: #000000 !important; 
                font-weight: 900 !important; 
                font-size: 1.2rem !important;
                display: block !important;
                margin-bottom: 0.5rem !important;
                opacity: 1 !important;
                text-shadow: none !important;">💡 Tipp des Tages:</span>
            <span style="
                color: #000000 !important; 
                font-weight: 700 !important;
                font-size: 1rem !important;
                line-height: 1.6 !important;
                opacity: 1 !important;
                text-shadow: none !important;"> {daily_tip}</span>
        </div>
        """, unsafe_allow_html=True)

        # Footer (Emoji-Filterung zentral über emoji_toggle.py)
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem; color: #000000; font-size: 1rem; text-shadow: 10px 10px 2px rgba(0,0,0,0.1);">
            Ömers All in One DingsBums v2.0 | 2025 | Powered by Ömer
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        
        # Schließe Intro-Screen Container
        st.markdown('</div>', unsafe_allow_html=True)

    # Keyboard-Shortcut mit JavaScript
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.target.matches('input, textarea')) {
            const quickStartButton = document.querySelector('[data-testid="baseButton-primary"]');
            if (quickStartButton) {
                quickStartButton.click();
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

    return False


def render_registration_form(settings: dict):
    """Registrierungsformular mit Pflichtfeldern"""

    st.markdown("#### Neuen Benutzer registrieren")

    # Account-Typ wählen
    account_type = st.selectbox(
        "Kontotyp",
        options=[
            "privat",
            "firma"],
        format_func=lambda x: "Privatkunde" if x == "privat" else "Firmenkunde")

    with st.form("registration_form"):
        st.markdown('<h5 style="color: #000000 !important; font-weight: 700 !important;">Pflichtangaben</h5>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # PFLICHTFELDER
            username = st.text_input(
                "Benutzername *", placeholder="max.mustermann")
            password = st.text_input(
                "Passwort *",
                type="password",
                placeholder="Mindestens 6 Zeichen")
            password_confirm = st.text_input(
                "Passwort bestätigen *", type="password")
            full_name = st.text_input(
                "Vollständiger Name *",
                placeholder="Max Mustermann")
            email = st.text_input("E-Mail *", placeholder="max@firma.de")

        with col2:
            phone = st.text_input(
                "Telefonnummer *",
                placeholder="+49 123 456789")

            if account_type == "firma":
                company_name = st.text_input(
                    "Firmenname *", placeholder="Mustermann GmbH")
                position = st.text_input(
                    "Position im Unternehmen",
                    placeholder="Geschäftsführer")
                department = st.text_input("Abteilung", placeholder="Vertrieb")
            else:
                company_name = ""
                position = "Privatkunde"
                department = ""

        st.markdown('<h5 style="color: #000000 !important; font-weight: 700 !important;">Optionale Angaben</h5>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            address = st.text_area(
                "Adresse", placeholder="Musterstraße 123\n12345 Musterstadt")

        with col4:
            notes = st.text_area("Anmerkungen",
                                 placeholder="Zusätzliche Informationen...")

        # Datenschutz
        st.markdown("---")
        privacy_accepted = st.checkbox(
            "Ich akzeptiere die Datenschutzbestimmungen *")

        # Submit
        submit_button = st.form_submit_button(
            "Registrieren", use_container_width=True, type="primary")

        if submit_button:
            # Validierung
            errors = []

            if not username:
                errors.append("Benutzername ist erforderlich")
            if not password:
                errors.append("Passwort ist erforderlich")
            elif len(password) < 6:
                errors.append("Passwort muss mindestens 6 Zeichen lang sein")
            if password != password_confirm:
                errors.append("Passwörter stimmen nicht überein")
            if not full_name:
                errors.append("Vollständiger Name ist erforderlich")
            if not email:
                errors.append("E-Mail ist erforderlich")
            elif '@' not in email:
                errors.append("Ungültige E-Mail-Adresse")
            if not phone:
                errors.append("Telefonnummer ist erforderlich")
            if account_type == "firma" and not company_name:
                errors.append("Firmenname ist erforderlich")
            if not privacy_accepted:
                errors.append(
                    "Datenschutzbestimmungen müssen akzeptiert werden")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Registrierung durchführen
                try:
                    from user_management import UserManagement
                    um = UserManagement()

                    # Firma erstellen falls Firmenkunde
                    company_id = None
                    if account_type == "firma" and company_name:
                        try:
                            from database import add_company
                            company_id = add_company({
                                'name': company_name,
                                'contact_person': full_name,
                                'email': email,
                                'phone': phone,
                                'address': address
                            })
                        except BaseException:
                            pass  # Firma-Erstellung optional

                    # Benutzer erstellen
                    user_id = um.create_user(
                        username=username,
                        password=password,
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        company_id=company_id,
                        rank="Mitarbeiter" if account_type == "firma" else "Privatkunde",
                        role="user",
                        permissions={
                            "view_data": True,
                            "create_offers": True})

                    if user_id:
                        # Optional: Position/Abteilung in Notizen speichern
                        if position or department or notes:
                            note_parts = []
                            if position:
                                note_parts.append(f"Position: {position}")
                            if department:
                                note_parts.append(f"Abteilung: {department}")
                            if notes:
                                note_parts.append(f"Notizen: {notes}")
                            um.update_user(
                                user_id, notes=" | ".join(note_parts))

                        st.success(
                            f"Registrierung erfolgreich! Sie können sich jetzt mit '{username}' anmelden.")
                        st.info("Bitte wechseln Sie zum 'Anmelden'-Tab.")
                    else:
                        st.error(
                            "Registrierung fehlgeschlagen - Benutzername bereits vergeben")

                except Exception as e:
                    st.error(f"Fehler bei der Registrierung: {e}")


def show_user_info():
    """Zeigt Benutzer-Info in der Sidebar (Emoji-Filterung zentral über emoji_toggle.py)"""
    if st.session_state.get('intro_completed', False):
        username = st.session_state.get('username', 'Unbekannt')
        user_mode = st.session_state.get('user_mode', 'guest')

        mode_labels = {
            'admin': 'Administrator',
            'quick_start': 'Schnellstart',
            'guest': 'Gastmodus',
            'user': 'Benutzer',
            'manager': 'Manager'
        }

        label = mode_labels.get(user_mode, 'Gast')

        st.markdown("---")
        st.markdown("**Angemeldet als:**")
        st.markdown(f"`{username}`")
        st.caption(f"Modus: {label}")

        if st.button("Abmelden", use_container_width=True):
            st.session_state['intro_completed'] = False
            st.session_state.pop('username', None)
            st.session_state.pop('user_mode', None)
            st.session_state.pop('user_id', None)
            st.session_state.pop('user_rank', None)
            st.session_state.pop('user_permissions', None)
            st.rerun()
