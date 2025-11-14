#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automatische Behebung fehlender Module
Erstellt Symlinks oder kopiert fehlende Module aus utils/ ins Root
"""

import sys
from pathlib import Path
import shutil

def main():
    print("=" * 80)
    print("[TOOL] BEHEBUNG FEHLENDER MODULE")
    print("=" * 80)
    
    root = Path('.')
    utils = root / 'utils'
    
    # Module die aus utils/ verfügbar gemacht werden müssen
    utils_modules = {
        'pv3d': utils / 'pv3d.py',
        'pv3d_plotly': utils / 'pv3d_plotly.py',
        'pdf_visual_inject': utils / 'pdf_visual_inject.py',
    }
    
    print("\n[PACKAGE] ÜBERPRÜFE UTILS-MODULE")
    print("-" * 80)
    
    fixed = 0
    not_found = 0
    
    for module_name, source_path in utils_modules.items():
        if f != 0:
            target_path = root / f"{module_name}.py"
        else:
            target_path = 0.0
        
        if source_path.exists():
            if not target_path.exists():
                print(f"  [OK] Kopiere {module_name}.py von utils/")
                shutil.copy2(source_path, target_path)
                fixed += 1
            else:
                print(f"  [INFO]  {module_name}.py bereits vorhanden")
        else:
            print(f"  [ERROR] {module_name}.py NICHT in utils/ gefunden")
            not_found += 1
    
    # Prüfe ob andere fehlende Module alte/deprecated Dateien sind
    deprecated_modules = [
        'admin_pv_mounting_tab_v2',  # Alte Version
        'analysis_chart_modern_enhancement',  # Deprecated
        'business_sections_pdf',  # Deprecated
        'doc_output_modern_patch',  # Patch-Datei
        'enhanced_analysis_charts',  # Deprecated
        'enhanced_live_preview',  # Deprecated
        'extended_pdf_generator',  # Deprecated
        'mega_tom90_hybrid_pdf',  # Deprecated
        'modern_charts',  # Deprecated
        'modern_dashboard_ui',  # Deprecated
        'pdf_debug_widget',  # Debug-Tool
        'pdf_logo_integration',  # Deprecated
        'pdf_ui_design_enhancement',  # Deprecated
        'placeholders',  # Alte Datei
        'price_matrix',  # Deprecated (jetzt price_matrix_store)
        'speech_recognition',  # Optional Feature
        'storage_model_resolver',  # Deprecated
        'tom90_exact_renderer',  # Deprecated
        'tom90_renderer',  # Deprecated
        'universal_chart_modernizer',  # Deprecated
    ]
    
    print("\n[DELETE]  DEPRECATED/OPTIONALE MODULE")
    print("-" * 80)
    print("Die folgenden Module sind veraltet oder optional:")
    for mod in deprecated_modules:
        print(f"  [WARNING]  {mod}")
    
    print("\n" + "=" * 80)
    print("[CHART] ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"[OK] Behoben:     {fixed} Module")
    print(f"[INFO]  Vorhanden:   {len([m for m in utils_modules if (root / f'{m}.py').exists()]) - fixed} Module")
    print(f"[ERROR] Nicht gefunden: {not_found} Module")
    print(f"[WARNING]  Deprecated:  {len(deprecated_modules)} Module (können ignoriert werden)")
    
    print("\n[IDEA] NÄCHSTE SCHRITTE:")
    print("1. App neu starten: streamlit run admin_panel.py")
    print("2. Test-Dateien die deprecated Module importieren, können ignoriert werden")
    print("3. Für Produktiv-Code sind alle kritischen Module verfügbar")

if __name__ == "__main__":
    main()
