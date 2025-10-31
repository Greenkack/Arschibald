function Step8-CreateReadme {
    Log-Header "SCHRITT 8: DOKUMENTATION ERSTELLEN"
    
    # Einfaches README ohne Sonderzeichen die Probleme machen
    $readmeLine1 = "# Oemers Calculator All in One - Installation"
    $readmeLine2 = ""
    $readmeLine3 = "## Setup-Inhalt"
    $readmeLine4 = ""
    $readmeLine5 = "Diese Setup.exe enthaelt alle notwendigen Komponenten:"
    $readmeLine6 = "- Python 3.11.9 (Embedded)"
    $readmeLine7 = "- Alle Python-Pakete (194 Pakete)"
    $readmeLine8 = "- Vollstaendige App mit allen Dateien"
    $readmeLine9 = "- Core-Module (Phase 1-12, 31 Module)"
    $readmeLine10 = "- Agent-System, PDF-System, Chart-System, CRM"
    $readmeLine11 = ""
    $readmeLine12 = "## Installation"
    $readmeLine13 = ""
    $readmeLine14 = "1. Doppelklick auf OemersCalculator_Complete_Setup_v$APP_VERSION.exe"
    $readmeLine15 = "2. Installationsordner waehlen (Standard: C:\Program Files\OemersCalculatorAllInOne)"
    $readmeLine16 = "3. Administrator-Rechte bestaetigen"
    $readmeLine17 = "4. Warten bis Python-Pakete installiert sind (ca. 5 Minuten)"
    $readmeLine18 = ""
    $readmeLine19 = "## App starten"
    $readmeLine20 = ""
    $readmeLine21 = "Desktop-Verknuepfung: Oemers Calculator All in One"
    $readmeLine22 = "Browser oeffnet automatisch: http://localhost:8501"
    $readmeLine23 = ""
    $readmeLine24 = "## Systemanforderungen"
    $readmeLine25 = ""
    $readmeLine26 = "- Windows 10/11 (64-bit)"
    $readmeLine27 = "- RAM: 4 GB minimum (8 GB empfohlen)"
    $readmeLine28 = "- Festplatte: 3 GB frei"
    $readmeLine29 = "- Browser: Chrome, Firefox oder Edge"
    $readmeLine30 = ""
    $readmeLine31 = "## Support"
    $readmeLine32 = ""
    $readmeLine33 = "GitHub: https://github.com/Greenkack/Arschibald/issues"
    $readmeLine34 = ""
    $readmeLine35 = "Version: $APP_VERSION"
    $readmeLine36 = "Build: $(Get-Date -Format 'yyyy-MM-dd')"
    
    $readmeContent = $readmeLine1,$readmeLine2,$readmeLine3,$readmeLine4,$readmeLine5,$readmeLine6,$readmeLine7,$readmeLine8,$readmeLine9,$readmeLine10,$readmeLine11,$readmeLine12,$readmeLine13,$readmeLine14,$readmeLine15,$readmeLine16,$readmeLine17,$readmeLine18,$readmeLine19,$readmeLine20,$readmeLine21,$readmeLine22,$readmeLine23,$readmeLine24,$readmeLine25,$readmeLine26,$readmeLine27,$readmeLine28,$readmeLine29,$readmeLine30,$readmeLine31,$readmeLine32,$readmeLine33,$readmeLine34,$readmeLine35,$readmeLine36 -join "`n"
    
    $readmePath = Join-Path $OUTPUT_DIR "README_INSTALLATION.md"
    Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
    Log "README erstellt: $readmePath" "SUCCESS"
    
    # Kurze Anleitung
    $quickLine1 = "SCHNELLSTART - Oemers Calculator"
    $quickLine2 = ""
    $quickLine3 = "1. Setup ausfuehren: OemersCalculator_Complete_Setup_v$APP_VERSION.exe"
    $quickLine4 = "2. Installation durchfuehren"
    $quickLine5 = "3. Desktop-Icon starten"
    $quickLine6 = "4. Browser oeffnet automatisch"
    $quickLine7 = ""
    $quickLine8 = "Fertig!"
    
    $quickGuide = $quickLine1,$quickLine2,$quickLine3,$quickLine4,$quickLine5,$quickLine6,$quickLine7,$quickLine8 -join "`n"
    
    $quickGuidePath = Join-Path $OUTPUT_DIR "SCHNELLSTART.txt"
    Set-Content -Path $quickGuidePath -Value $quickGuide -Encoding UTF8
    Log "Schnellstart-Anleitung erstellt" "SUCCESS"
}
