"""
Test: Excel Integration - Benutzerfreundlichkeit (Task 22)

Testet alle Benutzerfreundlichkeits-Features:
- Tastatur-Shortcuts
- Funktions-Tooltips
- Fehler-Tooltips
- Beispiel-Matrizen
- Tutorial-System
"""

import pytest
from excel.excel_help import (
    get_keyboard_shortcuts,
    get_function_tooltip,
    get_error_tooltip,
    get_ui_tooltip,
    get_all_functions_by_category,
    format_function_help,
    format_error_help
)
from excel.excel_examples import (
    get_example_matrix,
    get_all_examples,
    get_example_list
)
from excel.excel_tutorial import (
    get_tutorial_steps,
    get_tutorial_step,
    get_total_steps,
    format_tutorial_step,
    TutorialProgress
)


class TestKeyboardShortcuts:
    """Tests für Tastatur-Shortcuts Dokumentation"""
    
    def test_get_keyboard_shortcuts(self):
        """Test: Alle Shortcuts abrufen"""
        shortcuts = get_keyboard_shortcuts()
        
        assert isinstance(shortcuts, dict)
        assert len(shortcuts) > 0
        
        # Prüfe Kategorien
        assert "Navigation" in shortcuts
        assert "Bearbeitung" in shortcuts
        assert "Formeln" in shortcuts
        assert "Speichern" in shortcuts
    
    def test_shortcuts_have_descriptions(self):
        """Test: Alle Shortcuts haben Beschreibungen"""
        shortcuts = get_keyboard_shortcuts()
        
        for category, shortcuts_dict in shortcuts.items():
            assert len(shortcuts_dict) > 0
            for shortcut, description in shortcuts_dict.items():
                assert isinstance(shortcut, str)
                assert isinstance(description, str)
                assert len(description) > 0


class TestFunctionTooltips:
    """Tests für Funktions-Tooltips"""
    
    def test_get_function_tooltip(self):
        """Test: Tooltip für eine Funktion abrufen"""
        tooltip = get_function_tooltip("SUM")
        
        assert tooltip is not None
        assert "description" in tooltip
        assert "syntax" in tooltip
        assert "example" in tooltip
        assert "category" in tooltip
    
    def test_all_functions_have_tooltips(self):
        """Test: Alle Funktionen haben Tooltips"""
        functions = get_all_functions_by_category()
        
        assert len(functions) > 0
        
        for category, func_list in functions.items():
            assert len(func_list) > 0
            for func in func_list:
                assert "name" in func
                assert "description" in func
                assert "syntax" in func
                assert "example" in func
    
    def test_format_function_help(self):
        """Test: Formatierte Funktions-Hilfe"""
        help_text = format_function_help("VLOOKUP")
        
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "VLOOKUP" in help_text
        assert "Syntax" in help_text
        assert "Beispiel" in help_text
    
    def test_function_categories(self):
        """Test: Funktionen sind korrekt kategorisiert"""
        functions = get_all_functions_by_category()
        
        # Prüfe erwartete Kategorien
        assert "Mathematik" in functions
        assert "Logik" in functions
        assert "Lookup" in functions
        assert "Datum" in functions
        assert "Text" in functions


class TestErrorTooltips:
    """Tests für Fehler-Tooltips"""
    
    def test_get_error_tooltip(self):
        """Test: Tooltip für einen Fehler abrufen"""
        tooltip = get_error_tooltip("#DIV/0!")
        
        assert tooltip is not None
        assert "title" in tooltip
        assert "description" in tooltip
        assert "solutions" in tooltip
        assert len(tooltip["solutions"]) > 0
    
    def test_all_error_codes_have_tooltips(self):
        """Test: Alle Fehler-Codes haben Tooltips"""
        error_codes = ["#ERROR!", "#REF!", "#DIV/0!", "#CIRCULAR!", "#NAME?", "#VALUE!"]
        
        for error_code in error_codes:
            tooltip = get_error_tooltip(error_code)
            assert tooltip is not None
            assert len(tooltip["solutions"]) >= 3
    
    def test_format_error_help(self):
        """Test: Formatierte Fehler-Hilfe"""
        help_text = format_error_help("#DIV/0!")
        
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "#DIV/0!" in help_text
        assert "Lösungsvorschläge" in help_text


class TestUITooltips:
    """Tests für UI-Element Tooltips"""
    
    def test_get_ui_tooltip(self):
        """Test: Tooltip für UI-Element abrufen"""
        tooltip = get_ui_tooltip("neue_matrix")
        
        assert isinstance(tooltip, str)
        assert len(tooltip) > 0
    
    def test_ui_tooltips_exist(self):
        """Test: Tooltips für wichtige UI-Elemente existieren"""
        elements = [
            "neue_matrix",
            "speichern",
            "laden",
            "undo",
            "redo",
            "auto_save",
            "formeln_anzeigen",
            "kopieren",
            "einfuegen"
        ]
        
        for element in elements:
            tooltip = get_ui_tooltip(element)
            assert len(tooltip) > 0


class TestExampleMatrices:
    """Tests für Beispiel-Matrizen"""
    
    def test_get_example_matrix(self):
        """Test: Beispiel-Matrix abrufen"""
        example = get_example_matrix("einfache_preisliste")
        
        assert example is not None
        assert "name" in example
        assert "description" in example
        assert "rows" in example
        assert "columns" in example
        assert "data" in example
    
    def test_all_examples_exist(self):
        """Test: Alle Beispiele existieren"""
        examples = get_all_examples()
        
        assert len(examples) >= 4
        assert "einfache_preisliste" in examples
        assert "staffelpreise" in examples
        assert "kalkulation_mit_formeln" in examples
        assert "lookup_beispiel" in examples
    
    def test_get_example_list(self):
        """Test: Beispiel-Liste abrufen"""
        examples = get_example_list()
        
        assert len(examples) >= 4
        for example in examples:
            assert "key" in example
            assert "name" in example
            assert "description" in example
    
    def test_example_has_formulas(self):
        """Test: Beispiele enthalten Formeln"""
        example = get_example_matrix("einfache_preisliste")
        
        # Prüfe ob Formeln vorhanden sind
        has_formulas = False
        for cell_data in example["data"].values():
            if "formula" in cell_data:
                has_formulas = True
                break
        
        assert has_formulas


class TestTutorial:
    """Tests für Tutorial-System"""
    
    def test_get_tutorial_steps(self):
        """Test: Alle Tutorial-Schritte abrufen"""
        steps = get_tutorial_steps()
        
        assert len(steps) > 0
        assert len(steps) == get_total_steps()
    
    def test_get_tutorial_step(self):
        """Test: Einzelnen Tutorial-Schritt abrufen"""
        step = get_tutorial_step(1)
        
        assert step is not None
        assert "step" in step
        assert "title" in step
        assert "content" in step
    
    def test_tutorial_step_structure(self):
        """Test: Tutorial-Schritte haben korrekte Struktur"""
        steps = get_tutorial_steps()
        
        for step in steps:
            assert "step" in step
            assert "title" in step
            assert "content" in step
            assert "action" in step
            assert "highlight" in step
    
    def test_format_tutorial_step(self):
        """Test: Tutorial-Schritt formatieren"""
        step = get_tutorial_step(1)
        formatted = format_tutorial_step(step)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert step["title"] in formatted
    
    def test_tutorial_progress(self):
        """Test: Tutorial-Fortschritt"""
        progress = TutorialProgress()
        
        assert progress.current_step == 1
        assert not progress.is_completed()
        assert progress.get_progress_percentage() == 0.0
        
        # Nächster Schritt
        progress.next_step()
        assert progress.current_step == 2
        assert progress.get_progress_percentage() > 0.0
        
        # Vorheriger Schritt
        progress.previous_step()
        assert progress.current_step == 1
    
    def test_tutorial_skip(self):
        """Test: Tutorial überspringen"""
        progress = TutorialProgress()
        
        progress.skip_tutorial()
        assert progress.is_completed()
    
    def test_tutorial_complete(self):
        """Test: Tutorial abschließen"""
        progress = TutorialProgress()
        
        progress.complete_tutorial()
        assert progress.is_completed()
        assert progress.get_progress_percentage() > 0.0


class TestIntegration:
    """Integrationstests für alle Features"""
    
    def test_help_system_complete(self):
        """Test: Hilfe-System ist vollständig"""
        # Shortcuts
        shortcuts = get_keyboard_shortcuts()
        assert len(shortcuts) >= 4
        
        # Funktionen
        functions = get_all_functions_by_category()
        assert len(functions) >= 5
        
        # Fehler
        error_codes = ["#ERROR!", "#REF!", "#DIV/0!", "#CIRCULAR!", "#NAME?", "#VALUE!"]
        for code in error_codes:
            assert get_error_tooltip(code) is not None
    
    def test_examples_complete(self):
        """Test: Beispiele sind vollständig"""
        examples = get_all_examples()
        
        # Mindestens 4 Beispiele
        assert len(examples) >= 4
        
        # Jedes Beispiel hat Daten
        for example in examples.values():
            assert len(example["data"]) > 0
    
    def test_tutorial_complete(self):
        """Test: Tutorial ist vollständig"""
        steps = get_tutorial_steps()
        
        # Mindestens 10 Schritte
        assert len(steps) >= 10
        
        # Erster und letzter Schritt
        assert steps[0]["step"] == 1
        assert steps[-1]["step"] == len(steps)


def run_tests():
    """Führt alle Tests aus"""
    print("=" * 80)
    print("EXCEL INTEGRATION - BENUTZERFREUNDLICHKEIT TESTS")
    print("=" * 80)
    
    # Führe Tests aus
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
