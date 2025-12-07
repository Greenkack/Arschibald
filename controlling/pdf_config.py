"""
PDF Farb-Konfiguration für Controlling Reports

Ermöglicht individuelle Anpassung der PDF-Farben für Berichte.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class PDFColorScheme:
    """
    Farbschema für PDF-Generierung.
    
    Alle Farben im HEX-Format (#RRGGBB).
    """
    # Hauptfarben
    primary_color: str = "#366092"  # Dunkelblau (Tabellen-Header)
    secondary_color: str = "#5B9BD5"  # Hellblau (Akzente)
    
    # Textfarben
    title_color: str = "#366092"  # Titel-Farbe
    text_color: str = "#000000"  # Standard-Text
    header_text_color: str = "#FFFFFF"  # Text auf farbigem Hintergrund
    
    # Hintergrundfarben
    table_header_bg: str = "#366092"  # Tabellen-Kopfzeile
    table_row_bg: str = "#F5F5DC"  # Tabellenzeilen (beige)
    table_alt_row_bg: str = "#FFFFFF"  # Alternative Zeilen (weiß)
    
    # Akzentfarben
    success_color: str = "#28A745"  # Grün für Erfolg
    warning_color: str = "#FFC107"  # Gelb für Warnung
    error_color: str = "#DC3545"  # Rot für Fehler
    info_color: str = "#17A2B8"  # Cyan für Info
    
    # Rahmen & Linien
    border_color: str = "#000000"  # Rahmenfarbe
    grid_color: str = "#CCCCCC"  # Rasterlinien


class PDFConfigManager:
    """
    Manager für PDF-Farbkonfiguration.
    
    Speichert und lädt benutzerdefinierte Farbschemata.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialisiere Config Manager.
        
        Args:
            config_path: Pfad zur Konfigurationsdatei
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "data" / "pdf_colors.json"
        
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lade oder erstelle Standard-Schema
        self.color_scheme = self.load_color_scheme()
    
    def load_color_scheme(self) -> PDFColorScheme:
        """
        Lade Farbschema aus Datei oder verwende Standard.
        
        Returns:
            PDFColorScheme Objekt
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return PDFColorScheme(**data)
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Farbkonfiguration: {e}")
                logger.info("Verwende Standard-Farbschema")
        
        # Standard-Schema verwenden
        return PDFColorScheme()
    
    def save_color_scheme(self, color_scheme: PDFColorScheme) -> bool:
        """
        Speichere Farbschema in Datei.
        
        Args:
            color_scheme: Zu speicherndes Farbschema
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(color_scheme), f, indent=2, ensure_ascii=False)
            
            self.color_scheme = color_scheme
            logger.info(f"Farbschema gespeichert: {self.config_path}")
            return True
        
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Farbkonfiguration: {e}")
            return False
    
    def update_color(self, color_name: str, hex_color: str) -> bool:
        """
        Aktualisiere einzelne Farbe.
        
        Args:
            color_name: Name der Farbe (z.B. 'primary_color')
            hex_color: Neue Farbe im HEX-Format (#RRGGBB)
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not self._is_valid_hex_color(hex_color):
            logger.error(f"Ungültige HEX-Farbe: {hex_color}")
            return False
        
        if not hasattr(self.color_scheme, color_name):
            logger.error(f"Unbekannter Farbname: {color_name}")
            return False
        
        setattr(self.color_scheme, color_name, hex_color)
        return self.save_color_scheme(self.color_scheme)
    
    def reset_to_default(self) -> bool:
        """
        Setze Farbschema auf Standard zurück.
        
        Returns:
            True bei Erfolg
        """
        self.color_scheme = PDFColorScheme()
        return self.save_color_scheme(self.color_scheme)
    
    def get_predefined_schemes(self) -> Dict[str, PDFColorScheme]:
        """
        Hole vordefinierte Farbschemata.
        
        Returns:
            Dictionary mit vordefinierten Schemata
        """
        return {
            "Standard (Blau)": PDFColorScheme(),
            
            "Grün": PDFColorScheme(
                primary_color="#2E7D32",
                secondary_color="#66BB6A",
                title_color="#2E7D32",
                table_header_bg="#2E7D32",
                table_row_bg="#E8F5E9",
                success_color="#1B5E20",
                warning_color="#F57C00",
                error_color="#C62828",
                info_color="#0277BD"
            ),
            
            "Rot": PDFColorScheme(
                primary_color="#C62828",
                secondary_color="#E57373",
                title_color="#C62828",
                table_header_bg="#C62828",
                table_row_bg="#FFEBEE",
                success_color="#2E7D32",
                warning_color="#F57C00",
                error_color="#B71C1C",
                info_color="#0277BD"
            ),
            
            "Orange": PDFColorScheme(
                primary_color="#E65100",
                secondary_color="#FF9800",
                title_color="#E65100",
                table_header_bg="#E65100",
                table_row_bg="#FFF3E0",
                success_color="#2E7D32",
                warning_color="#F57C00",
                error_color="#C62828",
                info_color="#0277BD"
            ),
            
            "Lila": PDFColorScheme(
                primary_color="#6A1B9A",
                secondary_color="#AB47BC",
                title_color="#6A1B9A",
                table_header_bg="#6A1B9A",
                table_row_bg="#F3E5F5",
                success_color="#2E7D32",
                warning_color="#F57C00",
                error_color="#C62828",
                info_color="#0277BD"
            ),
            
            "Grau (Monochrom)": PDFColorScheme(
                primary_color="#424242",
                secondary_color="#757575",
                title_color="#212121",
                table_header_bg="#424242",
                table_row_bg="#F5F5F5",
                success_color="#2E7D32",
                warning_color="#F57C00",
                error_color="#C62828",
                info_color="#0277BD"
            ),
            
            "Dunkel": PDFColorScheme(
                primary_color="#1A1A1A",
                secondary_color="#333333",
                title_color="#000000",
                table_header_bg="#1A1A1A",
                table_row_bg="#F0F0F0",
                border_color="#333333",
                grid_color="#666666",
                success_color="#2E7D32",
                warning_color="#F57C00",
                error_color="#C62828",
                info_color="#0277BD"
            ),
        }
    
    def apply_predefined_scheme(self, scheme_name: str) -> bool:
        """
        Wende vordefiniertes Farbschema an.
        
        Args:
            scheme_name: Name des vordefinierten Schemas
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        schemes = self.get_predefined_schemes()
        
        if scheme_name not in schemes:
            logger.error(f"Unbekanntes Schema: {scheme_name}")
            return False
        
        return self.save_color_scheme(schemes[scheme_name])
    
    @staticmethod
    def _is_valid_hex_color(hex_color: str) -> bool:
        """
        Validiere HEX-Farbe.
        
        Args:
            hex_color: Zu validierende Farbe
            
        Returns:
            True wenn gültig
        """
        if not hex_color.startswith('#'):
            return False
        
        if len(hex_color) != 7:
            return False
        
        try:
            int(hex_color[1:], 16)
            return True
        except ValueError:
            return False


# Singleton-Instanz
_config_manager = None


def get_pdf_config_manager() -> PDFConfigManager:
    """
    Hole globale PDF Config Manager Instanz.
    
    Returns:
        PDFConfigManager Singleton
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = PDFConfigManager()
    return _config_manager


def get_color_scheme() -> PDFColorScheme:
    """
    Hole aktuelles Farbschema.
    
    Returns:
        Aktuelles PDFColorScheme
    """
    return get_pdf_config_manager().color_scheme
