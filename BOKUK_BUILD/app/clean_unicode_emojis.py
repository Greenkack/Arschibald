#!/usr/bin/env python3
"""
UNICODE-EMOJI BEREINIGER
========================

Entfernt ALLE problematischen Unicode-Emojis aus PDF-relevanten Dateien.
"""

import os
import re


def clean_unicode_emojis():
    """Entfernt alle problematischen Unicode-Emojis aus PDF-Dateien."""

    print("🧹 Unicode-Emoji Bereinigung gestartet...")

    # PDF-relevante Dateien
    pdf_files = [
        "pdf_generator.py",
        "tom90_renderer.py",
        "central_pdf_system.py",
        "doc_output.py",
        "mega_tom90_hybrid_pdf.py",
    ]

    # Problematische Unicode-Emojis (als Unicode-Codes)
    emoji_patterns = [
        # Häufige Emojis
        (r"\s*", ""),  # \U0001f527
        (r"\s*", ""),  # \u2699\ufe0f
        (r"\s*", ""),  # \U0001f4de
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        (r"\s*", ""),
        # Unicode-Codes aus Fehlermeldung
        (r"\\U0001f527\s*", ""),  #
        (r"\\u2699\\ufe0f\s*", ""),  #
        (r"\\U0001f4de\s*", ""),  #
        # Als raw Unicode in Strings
        (r"\U0001f527\s*", ""),  #
        (r"\u2699\ufe0f\s*", ""),  #
        (r"\U0001f4de\s*", ""),  #
    ]

    # Ampersand-Fixes
    xml_fixes = [
        (r"Garantie & Gewährleistung", "Garantie &amp; Gewährleistung"),
        (r"Montage & Installation", "Montage &amp; Installation"),
        (r"Wartung & Service", "Wartung &amp; Service"),
    ]

    total_fixes = 0

    for file_path in pdf_files:
        if not os.path.exists(file_path):
            print(f" Datei nicht gefunden: {file_path}")
            continue

        print(f" Bereinige: {file_path}")

        try:
            # Datei lesen
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            file_fixes = 0

            # Emoji-Patterns entfernen
            for pattern, replacement in emoji_patterns:
                old_content = content
                content = re.sub(pattern, replacement, content)
                if content != old_content:
                    matches = len(re.findall(pattern, old_content))
                    file_fixes += matches
                    print(f"   {matches}x Emoji entfernt: '{pattern[:20]}...'")

            # XML-Fixes anwenden
            for pattern, replacement in xml_fixes:
                count = content.count(pattern)
                if count > 0:
                    content = content.replace(pattern, replacement)
                    file_fixes += count
                    print(
                        f"   {count}x XML-Fix: '{pattern}' → '{replacement}'")

            # Datei zurückschreiben wenn geändert
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                total_fixes += file_fixes
                print(f"   {file_fixes} Fixes gespeichert")
            else:
                print("  ℹ Bereits sauber")

        except Exception as e:
            print(f"   Fehler bei {file_path}: {e}")

    print(
        f"\n Unicode-Emoji Bereinigung abgeschlossen! {total_fixes} Fixes insgesamt")
    return total_fixes


def verify_xml_cleanliness():
    """Überprüft ob alle problematischen Unicode-Zeichen entfernt wurden."""

    print("\n Überprüfe XML-Sauberkeit...")

    problematic_patterns = [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "\\U0001f527",
        "\\u2699\\ufe0f",
        "\\U0001f4de",
        " & ",
        " &amp;",  # Check both patterns
    ]

    pdf_files = [
        "pdf_generator.py",
        "tom90_renderer.py",
        "central_pdf_system.py"]

    issues_found = 0

    for file_path in pdf_files:
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            file_issues = 0

            # Check for problematic patterns
            for pattern in problematic_patterns:
                if pattern in content:
                    count = content.count(pattern)
                    if pattern == " &amp;":
                        print(
                            f"   {file_path}: {count}x '{pattern}' (korrekt escaped)")
                    elif pattern == " & ":
                        print(
                            f"   {file_path}: {count}x '{pattern}' (sollte escaped werden)")
                        file_issues += count
                    else:
                        print(
                            f"   {file_path}: {count}x '{pattern}' (problematisch)")
                        file_issues += count

            if file_issues == 0:
                print(f"   {file_path}: Sauber")

            issues_found += file_issues

        except Exception as e:
            print(f"   Fehler bei {file_path}: {e}")

    print(f"\n Verifikation: {issues_found} problematische Muster gefunden")
    return issues_found == 0


if __name__ == "__main__":
    # 1. Bereinigung durchführen
    fixes_applied = clean_unicode_emojis()

    # 2. Sauberkeit überprüfen
    is_clean = verify_xml_cleanliness()

    print("\n ZUSAMMENFASSUNG:")
    print(f"  • {fixes_applied} Unicode-Emojis entfernt")
    print(f"  • XML-Sauberkeit: {' OK' if is_clean else ' Probleme gefunden'}")

    if fixes_applied > 0 and is_clean:
        print("\n EMPFEHLUNG: PDF-Generierung sollte jetzt funktionieren!")
        print("   Alle problematischen Unicode-Emojis wurden entfernt.")
