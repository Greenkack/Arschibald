"""
Automatisches Hinzufügen von Pickle-Serialisierungsmethoden zu allen Klassen.
Dieses Script durchsucht alle .py-Dateien und fügt __getstate__ und __setstate__ hinzu.
"""

import os
import re
from pathlib import Path
from typing import List, Set

# Serialisierungsmethoden als String
SERIALIZATION_CODE = '''    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)

'''

# Verzeichnisse, die ignoriert werden sollen
IGNORE_DIRS = {
    '__pycache__', '.git', 'venv', 'env', '.venv', 
    'node_modules', '.pytest_cache', '.mypy_cache',
    'python_embed', 'site-packages', '_sdist_build',
    'agent_workspace', '.streamlit'
}

# Dateien, die ignoriert werden sollen
IGNORE_FILES = {
    'make_all_classes_serializable.py',
    '__init__.py',
    'setup.py',
    'conftest.py'
}

# Klassen-Basisnamen, die nicht serialisiert werden sollen
SKIP_BASE_CLASSES = {
    'Exception', 'Error', 'Enum', 'IntEnum', 'Protocol',
    'TypedDict', 'NamedTuple', 'ABC', 'Base', 'Canvas',
    'Flowable', 'NodeVisitor', 'ast.NodeVisitor',
    'collections.namedtuple', 'tuple', 'dict', 'list',
    'type', 'object', 'TestCase'
}


def should_skip_directory(dirpath: str) -> bool:
    """Prüft, ob ein Verzeichnis übersprungen werden soll."""
    parts = Path(dirpath).parts
    return any(ignore in parts for ignore in IGNORE_DIRS)


def should_skip_file(filepath: str) -> bool:
    """Prüft, ob eine Datei übersprungen werden soll."""
    filename = os.path.basename(filepath)
    return filename in IGNORE_FILES


def has_serialization_methods(class_content: str) -> bool:
    """Prüft, ob eine Klasse bereits Serialisierungsmethoden hat."""
    return '__getstate__' in class_content or '__setstate__' in class_content


def should_skip_class(class_def: str) -> bool:
    """Prüft, ob eine Klasse übersprungen werden soll."""
    # Skip Exception-Klassen
    if 'Exception' in class_def or 'Error' in class_def:
        return True
    
    # Skip Enum-Klassen
    if 'Enum' in class_def:
        return True
    
    # Skip Protocol, TypedDict, etc.
    for skip_base in SKIP_BASE_CLASSES:
        if skip_base in class_def:
            return True
    
    # Skip Test-Klassen
    if 'Test' in class_def and 'TestCase' in class_def:
        return True
    
    return False


def find_class_definitions(content: str) -> List[tuple]:
    """
    Findet alle Klassendefinitionen im Code.
    Gibt Liste von (line_number, class_line, indentation) zurück.
    """
    lines = content.split('\n')
    classes = []
    
    for i, line in enumerate(lines):
        # Suche nach Klassendefinitionen
        match = re.match(r'^(\s*)class\s+([A-Z][a-zA-Z0-9_]*)\s*[\(:]', line)
        if match:
            indent = match.group(1)
            class_name = match.group(2)
            
            # Überspringe spezielle Klassen
            if should_skip_class(line):
                continue
            
            # Finde das Ende der Klasse (nächste Methode oder __init__)
            class_start = i
            class_end = i + 1
            
            # Suche nach __init__ oder erster Methode
            for j in range(i + 1, min(i + 50, len(lines))):
                next_line = lines[j]
                
                # Gefunden: __init__ oder def
                if re.match(rf'^{indent}    def\s+', next_line):
                    class_end = j
                    break
                
                # Gefunden: Docstring oder Pass
                if re.match(rf'^{indent}    """', next_line) or \
                   re.match(rf'^{indent}    pass', next_line):
                    class_end = j + 1
                    break
            
            # Prüfe, ob bereits Serialisierung vorhanden
            class_content = '\n'.join(lines[class_start:min(class_start + 100, len(lines))])
            if has_serialization_methods(class_content):
                continue
            
            classes.append((class_start, class_end, indent, class_name))
    
    return classes


def add_serialization_to_file(filepath: str) -> bool:
    """
    Fügt Serialisierungsmethoden zu allen Klassen in einer Datei hinzu.
    Gibt True zurück, wenn Änderungen vorgenommen wurden.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Fehler beim Lesen: {e}")
        return False
    
    # Finde alle Klassen
    classes = find_class_definitions(content)
    
    if not classes:
        return False
    
    print(f"\n{filepath}")
    print(f"  Gefundene Klassen: {len(classes)}")
    
    # Sortiere Klassen von hinten nach vorne (um Zeilennummern nicht zu verschieben)
    classes.sort(reverse=True)
    
    lines = content.split('\n')
    modified = False
    
    for class_start, insert_pos, indent, class_name in classes:
        # Erstelle Serialisierungscode mit korrekter Einrückung
        serialization_lines = [
            f"{indent}    def __getstate__(self):",
            f'{indent}        """Ermöglicht Pickle-Serialisierung für Session State"""',
            f"{indent}        return self.__dict__.copy()",
            f"{indent}    ",
            f"{indent}    def __setstate__(self, state):",
            f'{indent}        """Ermöglicht Pickle-Deserialisierung für Session State"""',
            f"{indent}        self.__dict__.update(state)",
            f"{indent}    "
        ]
        
        # Füge Methoden nach Klassendefinition ein
        lines[insert_pos:insert_pos] = serialization_lines
        modified = True
        print(f"  Serialisierung hinzugefügt: {class_name}")
    
    if modified:
        # Schreibe modifizierte Datei
        new_content = '\n'.join(lines)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"  Fehler beim Schreiben: {e}")
            return False
    
    return False


def process_directory(root_dir: str) -> tuple:
    """
    Verarbeitet alle Python-Dateien in einem Verzeichnis.
    Gibt (modified_count, total_count) zurück.
    """
    modified_files = 0
    total_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignoriere spezielle Verzeichnisse
        if should_skip_directory(dirpath):
            dirnames.clear()  # Verhindert Traversierung in Unterverzeichnisse
            continue
        
        # Entferne ignorierte Verzeichnisse aus der Traversierung
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            if not filename.endswith('.py'):
                continue
            
            filepath = os.path.join(dirpath, filename)
            
            if should_skip_file(filepath):
                continue
            
            total_files += 1
            
            if add_serialization_to_file(filepath):
                modified_files += 1
    
    return modified_files, total_files


def main():
    """Hauptfunktion."""
    print("=" * 80)
    print("Automatische Serialisierung aller Klassen")
    print("=" * 80)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nArbeitsverzeichnis: {root_dir}")
    print(f"\n⏳ Verarbeite alle Python-Dateien...\n")
    
    modified, total = process_directory(root_dir)
    
    print("\n" + "=" * 80)
    print(f"Fertig!")
    print(f"Statistik:")
    print(f"   - Verarbeitete Dateien: {total}")
    print(f"   - Modifizierte Dateien: {modified}")
    print("=" * 80)
    
    if modified > 0:
        print("\nBitte App neu starten, damit Änderungen wirksam werden!")


if __name__ == "__main__":
    main()
