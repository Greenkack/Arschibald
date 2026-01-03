import os

# Die komplette Ordner- und Dateistruktur aus deiner MD-Datei
structure = {
    "photovoltaik_plattform": {
        "main.py": "",
        "core": {
            "database.py": "",
            "calculations.py": "",
            "pdf_builder.py": "",
            "context_builder.py": "",
        },
        "pages": {
            "0_Admin_Firmen.py": "",
            "1_Bedarfsanalyse.py": "",
            "2_CRM_Pipeline.py": "",
            "3_Produkte_Verwalten.py": "",
            "4_PDF_Konfigurieren.py": "",
            "5_Einstellungen.py": "",
        },
        "assets": {},  # Leerer Ordner für statische Dateien
        "de.json": "",
        "requirements.txt": "",
    }
}


def create_structure(base_path, struct):
    for name, content in struct.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # Ordner
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Datei (leerer Platzhalter)
            with open(path, "w", encoding="utf-8") as f:
                # Optional: Platzhalter-Text oder Kommentar einfügen
                if name.endswith(".py"):
                    f.write(f"# {name} (automatisch erstellt)\n")
                elif name.endswith(".json"):
                    f.write("{\n  // Sprachdatei (automatisch erstellt)\n}\n")
                elif name.endswith(".txt"):
                    f.write("# requirements.txt (automatisch erstellt)\n")
                else:
                    f.write("")


if __name__ == "__main__":
    create_structure(".", structure)
    print("App-Struktur wurde erfolgreich erstellt!")
