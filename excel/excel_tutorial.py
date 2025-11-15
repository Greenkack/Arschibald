"""
Excel Integration - Interactive Tutorial

Dieses Modul stellt ein interaktives Onboarding-Tutorial bereit
das neue Benutzer durch die wichtigsten Features führt.
"""

from typing import Dict, List, Any


# Tutorial-Schritte
TUTORIAL_STEPS = [
    {
        "step": 1,
        "title": "Willkommen zur Excel-Integration! 👋",
        "content": """
Herzlich willkommen! Dieses Tutorial führt Sie durch die wichtigsten Features 
der Excel-Integration.

Sie lernen:
- Wie Sie Matrizen erstellen und verwalten
- Wie Sie Formeln eingeben und verwenden
- Wie Sie Daten importieren und exportieren
- Nützliche Tastatur-Shortcuts

**Klicken Sie auf 'Weiter' um zu beginnen!**
        """,
        "action": None,
        "highlight": None
    },
    {
        "step": 2,
        "title": "Matrix erstellen ",
        "content": """
Eine Matrix ist eine Tabelle mit Zeilen und Spalten, ähnlich wie in Excel.

**So erstellen Sie eine neue Matrix:**

1. Klicken Sie auf den Button **"➕ Neue Matrix"**
2. Geben Sie einen Namen ein (z.B. "Meine erste Matrix")
3. Wählen Sie die Anzahl der Zeilen und Spalten
4. Klicken Sie auf "Erstellen"

**Probieren Sie es jetzt aus!**
        """,
        "action": "create_matrix",
        "highlight": "neue_matrix_button"
    },
    {
        "step": 3,
        "title": "Zellen bearbeiten ✏️",
        "content": """
Jetzt können Sie Werte in die Zellen eingeben.

**So bearbeiten Sie eine Zelle:**

1. Klicken Sie auf eine Zelle im Grid
2. Die Zelle wird in der **Formelleiste** angezeigt
3. Geben Sie einen Wert ein (z.B. "100")
4. Klicken Sie auf **"Übernehmen"** oder drücken Sie Enter

**Tipp:** Sie können auch direkt in der Zelle tippen!

**Probieren Sie es aus:** Geben Sie in Zelle A1 den Wert "100" ein.
        """,
        "action": "edit_cell",
        "highlight": "formelleiste"
    },
    {
        "step": 4,
        "title": "Formeln verwenden 🔢",
        "content": """
Formeln ermöglichen automatische Berechnungen.

**So erstellen Sie eine Formel:**

1. Wählen Sie eine Zelle (z.B. B1)
2. Beginnen Sie mit **"="**
3. Geben Sie die Formel ein (z.B. "=A1*2")
4. Drücken Sie Enter

**Häufige Formeln:**
- `=SUM(A1:A10)` - Summiert A1 bis A10
- `=AVERAGE(A1:A10)` - Durchschnitt
- `=IF(A1>10, "Groß", "Klein")` - Bedingung

**Probieren Sie es aus:** Erstellen Sie in B1 die Formel "=A1*2"
        """,
        "action": "create_formula",
        "highlight": "formelleiste"
    },
    {
        "step": 5,
        "title": "Zeilen und Spalten verwalten ➕",
        "content": """
Sie können jederzeit Zeilen und Spalten hinzufügen oder löschen.

**Zeile hinzufügen:**
1. Wählen Sie die Position
2. Klicken Sie auf **"➕ Zeile hinzufügen"**

**Spalte hinzufügen:**
1. Wählen Sie die Position
2. Klicken Sie auf **"➕ Spalte hinzufügen"**

**Wichtig:** Formeln werden automatisch angepasst!

**Probieren Sie es aus:** Fügen Sie eine neue Zeile hinzu.
        """,
        "action": "add_row",
        "highlight": "zeilen_spalten_buttons"
    },
    {
        "step": 6,
        "title": "Speichern und Laden 💾",
        "content": """
Vergessen Sie nicht, Ihre Arbeit zu speichern!

**Speichern:**
- Klicken Sie auf **"💾 Speichern"**
- Oder drücken Sie **Strg+S**

**Auto-Save:**
- Aktivieren Sie **"🔄 Auto-Save"** für automatisches Speichern

**Laden:**
- Klicken Sie auf **"📂 Laden"**
- Wählen Sie eine gespeicherte Matrix aus

**Probieren Sie es aus:** Speichern Sie Ihre Matrix.
        """,
        "action": "save_matrix",
        "highlight": "speichern_button"
    },
    {
        "step": 7,
        "title": "Undo/Redo ↶↷",
        "content": """
Fehler passieren - kein Problem!

**Rückgängig machen (Undo):**
- Klicken Sie auf **"↶ Undo"**
- Oder drücken Sie **Strg+Z**

**Wiederholen (Redo):**
- Klicken Sie auf **"↷ Redo"**
- Oder drücken Sie **Strg+Y**

**Tipp:** Sie können bis zu 50 Schritte rückgängig machen!

**Probieren Sie es aus:** Ändern Sie eine Zelle und machen Sie es rückgängig.
        """,
        "action": "undo",
        "highlight": "undo_redo_buttons"
    },
    {
        "step": 8,
        "title": "Kopieren und Einfügen 📋",
        "content": """
Kopieren Sie Zellwerte schnell und einfach.

**Kopieren:**
1. Wählen Sie eine Zelle
2. Klicken Sie auf **"📋 Kopieren"** oder drücken Sie **Strg+C**

**Einfügen:**
1. Wählen Sie die Zielzelle
2. Klicken Sie auf **"Einfügen"** oder drücken Sie **Strg+V**

**Tipp:** Formeln werden beim Einfügen automatisch angepasst!

**Probieren Sie es aus:** Kopieren Sie eine Zelle.
        """,
        "action": "copy_paste",
        "highlight": "copy_paste_buttons"
    },
    {
        "step": 9,
        "title": "Import und Export 📥📤",
        "content": """
Arbeiten Sie mit externen Dateien.

**CSV Import:**
- Klicken Sie auf **"📥 CSV Import"**
- Wählen Sie eine CSV-Datei
- Die Daten werden automatisch importiert

**Excel Export:**
- Klicken Sie auf **"📤 Excel Export"**
- Ihre Matrix wird als XLSX-Datei exportiert
- **Formeln bleiben erhalten!**

**Tipp:** Sie können auch Excel-Dateien importieren!
        """,
        "action": "import_export",
        "highlight": "import_export_buttons"
    },
    {
        "step": 10,
        "title": "Tastatur-Shortcuts ⌨️",
        "content": """
Arbeiten Sie schneller mit Tastatur-Shortcuts!

**Navigation:**
- **Pfeiltasten** - Zwischen Zellen navigieren
- **Tab** - Zur nächsten Zelle
- **Enter** - Zur Zelle darunter

**Bearbeitung:**
- **Strg+Z** - Rückgängig
- **Strg+Y** - Wiederholen
- **Strg+C** - Kopieren
- **Strg+V** - Einfügen
- **Delete** - Zelle löschen

**Speichern:**
- **Strg+S** - Speichern

**Tipp:** Aktivieren Sie "⌨️ Tastaturnavigation" für volle Unterstützung!
        """,
        "action": None,
        "highlight": "keyboard_nav_checkbox"
    },
    {
        "step": 11,
        "title": "Beispiel-Matrizen 📚",
        "content": """
Lernen Sie von Beispielen!

Wir haben mehrere Beispiel-Matrizen vorbereitet:

- **Einfache Preisliste** - Grundlegende Berechnungen
- **Staffelpreise** - Preismatrix mit Lookup
- **Kalkulation mit Formeln** - Komplexe Berechnungen
- **VLOOKUP Beispiel** - Preissuche

**So laden Sie ein Beispiel:**
1. Klicken Sie auf "Beispiel laden" (im Tutorial-Dialog)
2. Wählen Sie ein Beispiel aus
3. Erkunden Sie die Formeln und Berechnungen

**Tipp:** Ändern Sie die Werte und sehen Sie wie sich die Berechnungen anpassen!
        """,
        "action": "load_example",
        "highlight": None
    },
    {
        "step": 12,
        "title": "Hilfe und Support ",
        "content": """
Brauchen Sie Hilfe?

**Funktion-Hilfe:**
- Bewegen Sie die Maus über Funktionsnamen
- Tooltips zeigen Syntax und Beispiele

**Fehler-Hilfe:**
- Fehler werden in Zellen angezeigt (z.B. #DIV/0!)
- Klicken Sie auf den Fehler für Lösungsvorschläge

**Dokumentation:**
- Vollständige Dokumentation in der Hilfe-Sektion
- Liste aller unterstützten Funktionen

**Tipp:** Bei Problemen schauen Sie in die Fehlerdetails!
        """,
        "action": None,
        "highlight": None
    },
    {
        "step": 13,
        "title": "Fertig! 🎉",
        "content": """
Herzlichen Glückwunsch! Sie haben das Tutorial abgeschlossen.

**Sie haben gelernt:**
Matrizen erstellen und verwalten
Zellen bearbeiten und Formeln verwenden
Zeilen und Spalten hinzufügen
Speichern, Laden, Undo/Redo
Kopieren und Einfügen
Import und Export
Tastatur-Shortcuts
Beispiel-Matrizen nutzen
Hilfe finden

**Nächste Schritte:**
- Erstellen Sie Ihre erste eigene Matrix
- Probieren Sie die Beispiel-Matrizen aus
- Erkunden Sie alle verfügbaren Funktionen

**Viel Erfolg! **
        """,
        "action": "complete",
        "highlight": None
    }
]


def get_tutorial_steps() -> List[Dict[str, Any]]:
    """
    Gibt alle Tutorial-Schritte zurück
    
    Returns:
        Liste von Tutorial-Schritten
    """
    return TUTORIAL_STEPS


def get_tutorial_step(step_number: int) -> Dict[str, Any]:
    """
    Gibt einen bestimmten Tutorial-Schritt zurück
    
    Args:
        step_number: Nummer des Schritts (1-basiert)
        
    Returns:
        Tutorial-Schritt oder None
    """
    if 1 <= step_number <= len(TUTORIAL_STEPS):
        return TUTORIAL_STEPS[step_number - 1]
    return None


def get_total_steps() -> int:
    """
    Gibt die Gesamtanzahl der Tutorial-Schritte zurück
    
    Returns:
        Anzahl der Schritte
    """
    return len(TUTORIAL_STEPS)


def format_tutorial_step(step: Dict[str, Any]) -> str:
    """
    Formatiert einen Tutorial-Schritt als Markdown
    
    Args:
        step: Tutorial-Schritt
        
    Returns:
        Formatierter Text
    """
    progress = f"Schritt {step['step']} von {get_total_steps()}"
    
    formatted = f"""
### {step['title']}

{progress}

{step['content']}
"""
    
    return formatted.strip()


# Tutorial-Fortschritt-Tracking
class TutorialProgress:
    """Verwaltet den Fortschritt eines Benutzers im Tutorial"""
    
    def __init__(self):
        self.current_step = 1
        self.completed_steps = set()
        self.skipped = False
    
    def next_step(self):
        """Geht zum nächsten Schritt"""
        if self.current_step < get_total_steps():
            self.completed_steps.add(self.current_step)
            self.current_step += 1
    
    def previous_step(self):
        """Geht zum vorherigen Schritt"""
        if self.current_step > 1:
            self.current_step -= 1
    
    def skip_tutorial(self):
        """Überspringt das Tutorial"""
        self.skipped = True
    
    def complete_tutorial(self):
        """Markiert das Tutorial als abgeschlossen"""
        self.completed_steps.add(self.current_step)
        self.current_step = get_total_steps()
    
    def is_completed(self) -> bool:
        """Prüft ob das Tutorial abgeschlossen ist"""
        return self.current_step >= get_total_steps() or self.skipped
    
    def get_progress_percentage(self) -> float:
        """
        Gibt den Fortschritt in Prozent zurück
        
        Returns:
            Fortschritt (0-100)
        """
        return (len(self.completed_steps) / get_total_steps()) * 100
    
    def get_current_step(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Tutorial-Schritt zurück
        
        Returns:
            Aktueller Schritt
        """
        return get_tutorial_step(self.current_step)
