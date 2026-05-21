"""
Contrast Utilities - Automatische Textfarben-Anpassung

Diese Utilities stellen sicher, dass Text immer gut lesbar ist,
indem die Textfarbe automatisch basierend auf dem Hintergrund angepasst wird.

WCAG 2.1 AA konform (Kontrastverhältnis mindestens 4.5:1)
"""

import re
from typing import Tuple, Optional


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Konvertiert Hex-Farbe zu RGB
    
    Args:
        hex_color: Hex-Farbe (z.B. '#FF0000' oder 'FF0000')
    
    Returns:
        Tuple mit (R, G, B) Werten (0-255)
    """
    # Entferne '#' falls vorhanden
    hex_color = hex_color.lstrip('#')
    
    # Unterstütze auch 3-stellige Hex-Codes (#FFF -> #FFFFFF)
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    # Konvertiere zu RGB
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except (ValueError, IndexError):
        # Fallback: Weiß
        return (255, 255, 255)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Konvertiert RGB zu Hex-Farbe
    
    Args:
        r: Rot (0-255)
        g: Grün (0-255)
        b: Blau (0-255)
    
    Returns:
        Hex-Farbe mit '#' (z.B. '#FF0000')
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Berechnet die relative Luminanz einer Farbe nach WCAG 2.1
    
    Args:
        rgb: Tuple mit (R, G, B) Werten (0-255)
    
    Returns:
        Relative Luminanz (0.0 - 1.0)
    """
    r, g, b = rgb
    
    # Normalisiere auf 0-1
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0
    
    # Linearisiere RGB-Werte
    def linearize(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4
    
    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)
    
    # Berechne Luminanz
    luminance = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    
    return luminance


def get_contrast_ratio(color1: str, color2: str) -> float:
    """
    Berechnet das Kontrastverhältnis zwischen zwei Farben nach WCAG 2.1
    
    Args:
        color1: Erste Farbe (Hex)
        color2: Zweite Farbe (Hex)
    
    Returns:
        Kontrastverhältnis (1.0 - 21.0)
    """
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    lum1 = get_relative_luminance(rgb1)
    lum2 = get_relative_luminance(rgb2)
    
    # Hellere Farbe zuerst
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    # Kontrastverhältnis
    ratio = (lighter + 0.05) / (darker + 0.05)
    
    return ratio


def is_light_color(hex_color: str) -> bool:
    """
    Prüft ob eine Farbe hell ist
    
    Args:
        hex_color: Hex-Farbe (z.B. '#FFFFFF')
    
    Returns:
        True wenn hell, False wenn dunkel
    """
    rgb = hex_to_rgb(hex_color)
    luminance = get_relative_luminance(rgb)
    
    # Schwellwert: 0.5 (kann angepasst werden)
    return luminance > 0.5


def get_contrast_color(background_color: str, 
                       light_color: str = "#FFFFFF", 
                       dark_color: str = "#000000") -> str:
    """
    Gibt die optimale Textfarbe für einen Hintergrund zurück
    
    Args:
        background_color: Hintergrundfarbe (Hex)
        light_color: Helle Textfarbe (Standard: Weiß)
        dark_color: Dunkle Textfarbe (Standard: Schwarz)
    
    Returns:
        Optimale Textfarbe (Hex)
    
    Example:
        >>> get_contrast_color("#000000")  # Schwarzer Hintergrund
        '#FFFFFF'  # Weißer Text
        
        >>> get_contrast_color("#FFFFFF")  # Weißer Hintergrund
        '#000000'  # Schwarzer Text
    """
    if is_light_color(background_color):
        return dark_color
    else:
        return light_color


def get_best_contrast_color(background_color: str, 
                            color_options: list = None) -> str:
    """
    Wählt die Farbe mit dem besten Kontrast aus einer Liste von Optionen
    
    Args:
        background_color: Hintergrundfarbe (Hex)
        color_options: Liste von möglichen Textfarben (Hex)
                      Standard: [Schwarz, Weiß]
    
    Returns:
        Farbe mit dem besten Kontrast (Hex)
    """
    if color_options is None:
        color_options = ["#000000", "#FFFFFF"]
    
    best_color = color_options[0]
    best_ratio = 0
    
    for color in color_options:
        ratio = get_contrast_ratio(background_color, color)
        if ratio > best_ratio:
            best_ratio = ratio
            best_color = color
    
    return best_color


def meets_wcag_aa(background_color: str, 
                  text_color: str, 
                  large_text: bool = False) -> bool:
    """
    Prüft ob Farbkombination WCAG 2.1 AA Standard erfüllt
    
    Args:
        background_color: Hintergrundfarbe (Hex)
        text_color: Textfarbe (Hex)
        large_text: True wenn Text >= 18pt oder >= 14pt bold
    
    Returns:
        True wenn WCAG AA konform, False sonst
    """
    ratio = get_contrast_ratio(background_color, text_color)
    
    # WCAG AA Anforderungen:
    # - Normaler Text: mindestens 4.5:1
    # - Großer Text: mindestens 3:1
    min_ratio = 3.0 if large_text else 4.5
    
    return ratio >= min_ratio


def meets_wcag_aaa(background_color: str, 
                   text_color: str, 
                   large_text: bool = False) -> bool:
    """
    Prüft ob Farbkombination WCAG 2.1 AAA Standard erfüllt
    
    Args:
        background_color: Hintergrundfarbe (Hex)
        text_color: Textfarbe (Hex)
        large_text: True wenn Text >= 18pt oder >= 14pt bold
    
    Returns:
        True wenn WCAG AAA konform, False sonst
    """
    ratio = get_contrast_ratio(background_color, text_color)
    
    # WCAG AAA Anforderungen:
    # - Normaler Text: mindestens 7:1
    # - Großer Text: mindestens 4.5:1
    min_ratio = 4.5 if large_text else 7.0
    
    return ratio >= min_ratio


def adjust_color_brightness(hex_color: str, factor: float) -> str:
    """
    Passt die Helligkeit einer Farbe an
    
    Args:
        hex_color: Farbe (Hex)
        factor: Faktor (< 1.0 dunkler, > 1.0 heller)
    
    Returns:
        Angepasste Farbe (Hex)
    """
    r, g, b = hex_to_rgb(hex_color)
    
    # Anpassen und auf 0-255 begrenzen
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    
    return rgb_to_hex(r, g, b)


def get_accessible_text_color(background_color: str,
                              preferred_color: Optional[str] = None,
                              fallback_light: str = "#FFFFFF",
                              fallback_dark: str = "#0A0A0A") -> str:
    """
    Gibt eine WCAG-konforme Textfarbe für einen Hintergrund zurück
    
    Diese Funktion prüft ob die bevorzugte Farbe ausreichend Kontrast hat.
    Falls nicht, wird eine helle oder dunkle Fallback-Farbe verwendet.
    
    Args:
        background_color: Hintergrundfarbe (Hex)
        preferred_color: Bevorzugte Textfarbe (Hex), optional
        fallback_light: Helle Fallback-Farbe (Standard: Weiß)
        fallback_dark: Dunkle Fallback-Farbe (Standard: Fast-Schwarz)
    
    Returns:
        WCAG AA konforme Textfarbe (Hex)
    
    Example:
        >>> get_accessible_text_color("#1E1E1E")  # Dunkler Hintergrund
        '#FFFFFF'  # Weißer Text
        
        >>> get_accessible_text_color("#F5F5F5")  # Heller Hintergrund
        '#0A0A0A'  # Dunkler Text
    """
    # Falls bevorzugte Farbe gegeben und konform ist, verwende sie
    if preferred_color:
        if meets_wcag_aa(background_color, preferred_color):
            return preferred_color
    
    # Wähle zwischen heller und dunkler Farbe
    if is_light_color(background_color):
        # Heller Hintergrund -> dunkle Schrift
        return fallback_dark
    else:
        # Dunkler Hintergrund -> helle Schrift
        return fallback_light


def parse_css_color(color: str) -> Optional[str]:
    """
    Parst verschiedene CSS-Farbformate und gibt Hex zurück
    
    Args:
        color: CSS-Farbe (hex, rgb(), rgba(), hsl(), hsla(), oder named)
    
    Returns:
        Hex-Farbe oder None bei Fehler
    """
    color = color.strip()
    
    # Bereits Hex-Farbe
    if color.startswith('#'):
        return color
    
    # RGB/RGBA
    rgb_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', color)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        return rgb_to_hex(r, g, b)
    
    # Named colors (Basis-Set)
    named_colors = {
        'white': '#FFFFFF',
        'black': '#000000',
        'red': '#FF0000',
        'green': '#008000',
        'blue': '#0000FF',
        'yellow': '#FFFF00',
        'cyan': '#00FFFF',
        'magenta': '#FF00FF',
        'gray': '#808080',
        'grey': '#808080',
    }
    
    if color.lower() in named_colors:
        return named_colors[color.lower()]
    
    return None


# Vordefinierte Farbpaare (Hintergrund -> Text)
PRESET_CONTRAST_PAIRS = {
    # Dunkle Hintergründe
    "#000000": "#FFFFFF",  # Schwarz -> Weiß
    "#0A0A0A": "#FFFFFF",  # Fast-Schwarz -> Weiß
    "#1A1A1A": "#FFFFFF",  # Dunkelgrau -> Weiß
    "#1E1E1E": "#FFFFFF",  # VSCode Dark -> Weiß
    "#2D2D2D": "#FFFFFF",  # Grau -> Weiß
    
    # Helle Hintergründe
    "#FFFFFF": "#0A0A0A",  # Weiß -> Fast-Schwarz
    "#F5F5F5": "#0A0A0A",  # Hellgrau -> Fast-Schwarz
    "#FAFAFA": "#0A0A0A",  # Fast-Weiß -> Fast-Schwarz
    "#E5E5E5": "#0A0A0A",  # Grau -> Fast-Schwarz
    
    # Farbige Hintergründe (Beispiele)
    "#3B82F6": "#FFFFFF",  # Blau -> Weiß
    "#EF4444": "#FFFFFF",  # Rot -> Weiß
    "#10B981": "#FFFFFF",  # Grün -> Weiß
    "#F59E0B": "#000000",  # Gelb -> Schwarz
}


def get_preset_contrast_color(background_color: str) -> Optional[str]:
    """
    Gibt eine vordefinierte Textfarbe für bekannte Hintergrundfarben zurück
    
    Args:
        background_color: Hintergrundfarbe (Hex)
    
    Returns:
        Vordefinierte Textfarbe oder None wenn nicht gefunden
    """
    return PRESET_CONTRAST_PAIRS.get(background_color.upper())
