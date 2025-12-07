#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST: SHADCN UI CHART DESIGN
Verifiziert vollständige Shadcn UI Implementation in allen Charts
"""

import re
from pathlib import Path


def test_shadcn_implementation():
    """Prüft Shadcn UI Features in Chart-Modulen"""
    
    print("=" * 80)
    print("SHADCN UI CHART DESIGN - VERIFICATION")
    print("=" * 80)
    
    files_to_check = [
        "heatpump_ui.py",
        "heatpump_dynamic_tariff_charts.py",
        "heatpump_advanced_charts.py"
    ]
    
    results = {}
    
    for filename in files_to_check:
        filepath = Path(filename)
        if not filepath.exists():
            results[filename] = {"exists": False}
            continue
        
        content = filepath.read_text(encoding='utf-8')
        
        # Prüfe Shadcn UI Features
        features = {
            "SHADCN_COLORS definiert": bool(re.search(r'SHADCN_COLORS\s*=\s*{', content)),
            "Gradient-Fills verwendet": bool(re.search(r'fillcolor.*rgba.*0\.1[0-9]', content)),
            "Spline-Shape (glatte Kurven)": bool(re.search(r"shape\s*[=:]\s*['\"]spline['\"]", content)),
            "Moderne Linienbreite (3px)": bool(re.search(r'width\s*[=:]\s*3', content)),
            "Shadcn Primary Color": bool(re.search(r'#38bdf8', content)),
            "Shadcn Success Color": bool(re.search(r'#34d399', content)),
            "Shadcn Danger Color": bool(re.search(r'#f87171', content)),
            "Inter Font Family": bool(re.search(r'Inter.*apple-system', content)),
            "Modern Margins (70+)": bool(re.search(r'"l":\s*7[0-9]', content)),
            "Hover Mode Unified": bool(re.search(r'hovermode.*unified', content))
        }
        
        results[filename] = {
            "exists": True,
            "features": features,
            "score": sum(features.values()) / len(features) * 100
        }
    
    # Ausgabe
    print("\nERGEBNISSE PRO DATEI:")
    print("-" * 80)
    
    for filename, data in results.items():
        if not data.get("exists"):
            print(f"\n{filename}: NICHT GEFUNDEN")
            continue
        
        score = data.get("score", 0)
        icon = "" if score >= 70 else "" if score >= 40 else ""
        
        print(f"\n{icon} {filename}: {score:.0f}% Shadcn UI Features")
        
        for feature, implemented in data["features"].items():
            status = "" if implemented else ""
            print(f"   {status} {feature}")
    
    # Gesamt-Score
    total_score = sum(d.get("score", 0) for d in results.values() if d.get("exists")) / \
                  sum(1 for d in results.values() if d.get("exists"))
    
    print("\n" + "=" * 80)
    print(f"GESAMT-SCORE: {total_score:.0f}%")
    
    if total_score >= 80:
        print("HERVORRAGEND - Vollständiges Shadcn UI Design implementiert!")
    elif total_score >= 60:
        print("GUT - Die meisten Shadcn UI Features sind implementiert")
    else:
        print("VERBESSERUNGSBEDARF - Mehr Shadcn UI Features erforderlich")
    
    print("=" * 80)
    
    # Details zu fehlenden Features
    print("\nFEATURE-ANALYSE:")
    print("-" * 80)
    
    all_features = {}
    for filename, data in results.items():
        if data.get("exists") and data.get("features"):
            for feature, implemented in data["features"].items():
                if feature not in all_features:
                    all_features[feature] = []
                all_features[feature].append((filename, implemented))
    
    for feature, implementations in all_features.items():
        total = len(implementations)
        implemented = sum(1 for _, impl in implementations if impl)
        percentage = implemented / total * 100
        
        status = "" if percentage == 100 else "" if percentage >= 50 else ""
        print(f"{status} {feature}: {implemented}/{total} Dateien ({percentage:.0f}%)")
        
        # Zeige fehlende Implementierungen
        if percentage < 100:
            missing = [f for f, impl in implementations if not impl]
            print(f"   Fehlt in: {', '.join(missing)}")
    
    print("\n" + "=" * 80)


def check_apply_chart_theme_calls():
    """Zählt apply_chart_theme() Aufrufe"""
    
    print("\nCHART THEME APPLICATION:")
    print("-" * 80)
    
    filepath = Path("heatpump_ui.py")
    if not filepath.exists():
        print("heatpump_ui.py nicht gefunden")
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # Zähle apply_chart_theme Aufrufe
    theme_calls = len(re.findall(r'apply_chart_theme\s*\(', content))
    
    # Zähle st.plotly_chart Aufrufe
    plotly_calls = len(re.findall(r'st\.plotly_chart\s*\(', content))
    
    coverage = theme_calls / plotly_calls * 100 if plotly_calls > 0 else 0
    
    print(f"apply_chart_theme Aufrufe: {theme_calls}")
    print(f"st.plotly_chart Aufrufe: {plotly_calls}")
    print(f"Theme Coverage: {coverage:.0f}%")
    
    if coverage >= 80:
        print("AUSGEZEICHNET - Fast alle Charts verwenden Shadcn UI Theme")
    elif coverage >= 60:
        print("GUT - Die meisten Charts verwenden Theme")
    else:
        print("VERBESSERUNGSBEDARF - Viele Charts ohne Theme")


if __name__ == "__main__":
    test_shadcn_implementation()
    check_apply_chart_theme_calls()
    
    print("\n SHADCN UI FEATURES:")
    print("-" * 80)
    print("Moderne Farbpalette (Shadcn UI Farben)")
    print("Gradient-Fills für Scatter/Area Charts")
    print("Glatte Spline-Kurven")
    print("Moderne Linienbreite (3px)")
    print("Inter Font Family")
    print("Großzügige Margins")
    print("Unified Hover Mode")
    print("Responsive Layout")
    print("Dark/Light Mode Support")
    print("=" * 80)
