"""
Umfassende Analyse aller Module zur Identifikation nicht-implementierter Features
Analysiert: analysis.py, doc_output.py, pdf_generator.py, pdf_ui.py, solarcalculator.py,
           calculations.py, extended_calculations.py, financial_tools.py, admin_panel.py
"""

import ast
import json
import os
from typing import Any


class FeatureAnalyzer(ast.NodeVisitor):
    """AST-basierter Analyzer zur Identifikation von Funktionen und Features"""

    def __init__(self, filename: str):
        self.filename = filename
        self.functions = []
        self.classes = []
        self.calculations = []
        self.charts = []
        self.financial_features = []
        self.current_class = None

    def visit_FunctionDef(self, node):
        """Analyse von Funktionsdefinitionen"""
        func_info = {
            'name': node.name,
            'lineno': node.lineno,
            'docstring': ast.get_docstring(node),
            'args': [arg.arg for arg in node.args.args],
            'returns': self._get_return_type(node),
            'class': self.current_class
        }

        self.functions.append(func_info)

        # Kategorisierung nach Feature-Typ
        name_lower = node.name.lower()

        if any(
            keyword in name_lower for keyword in [
                'calculate',
                'compute',
                'analyze',
                'calc']):
            self.calculations.append(func_info)

        if any(
            keyword in name_lower for keyword in [
                'chart',
                'graph',
                'plot',
                'diagram']):
            self.charts.append(func_info)

        if any(
            keyword in name_lower for keyword in [
                'financ',
                'loan',
                'credit',
                'rate',
                'payment',
                'amortization']):
            self.financial_features.append(func_info)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Analyse von Klassendefinitionen"""
        prev_class = self.current_class
        self.current_class = node.name

        class_info = {
            'name': node.name,
            'lineno': node.lineno,
            'docstring': ast.get_docstring(node),
            'methods': []
        }
        self.classes.append(class_info)

        self.generic_visit(node)
        self.current_class = prev_class

    def _get_return_type(self, node):
        """Extrahiert Return-Type Annotation falls vorhanden"""
        if node.returns:
            try:
                return ast.unparse(node.returns)
            except BaseException:
                return "unknown"
        return None


def analyze_file(filepath: str) -> dict[str, Any]:
    """Analysiert eine einzelne Python-Datei"""
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=filepath)
        analyzer = FeatureAnalyzer(filepath)
        analyzer.visit(tree)

        return {
            'file': os.path.basename(filepath),
            'total_functions': len(analyzer.functions),
            'total_classes': len(analyzer.classes),
            'calculations': analyzer.calculations,
            'charts': analyzer.charts,
            'financial_features': analyzer.financial_features,
            'all_functions': analyzer.functions[:20],  # Limit für Übersicht
        }
    except Exception as e:
        return {
            'file': os.path.basename(filepath),
            'error': str(e)
        }


def find_ui_references(filepath: str, function_names: set[str]) -> list[str]:
    """Findet Referenzen zu Funktionen in UI-Dateien"""
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()

        found = []
        for func_name in function_names:
            if func_name in content:
                found.append(func_name)
        return found
    except BaseException:
        return []


def main():
    """Hauptanalyse"""

    files_to_analyze = [
        'analysis.py',
        'doc_output.py',
        'pdf_generator.py',
        'pdf_ui.py',
        'solarcalculator.py',
        'calculations.py',
        'extended_calculations.py',
        'financial_tools.py',
        'admin_panel.py'
    ]

    ui_files = ['pdf_ui.py', 'admin_panel.py', 'app.py']

    print("=" * 100)
    print("🔍 UMFASSENDE FEATURE-ANALYSE")
    print("=" * 100)
    print()

    all_results = {}
    all_calculation_funcs = set()
    all_chart_funcs = set()
    all_financial_funcs = set()

    # Analyse aller Dateien
    for filename in files_to_analyze:
        if os.path.exists(filename):
            print(f"📄 Analysiere {filename}...")
            result = analyze_file(filename)
            all_results[filename] = result

            # Sammle Funktionsnamen
            for calc in result.get('calculations', []):
                all_calculation_funcs.add(calc['name'])
            for chart in result.get('charts', []):
                all_chart_funcs.add(chart['name'])
            for fin in result.get('financial_features', []):
                all_financial_funcs.add(fin['name'])

    print()
    print("=" * 100)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 100)
    print()

    # Berechnungs-Features
    print(f"🧮 BERECHNUNGS-FEATURES ({len(all_calculation_funcs)} gefunden):")
    print("-" * 100)
    for filename, result in all_results.items():
        calcs = result.get('calculations', [])
        if calcs:
            print(f"\n  📁 {filename} ({len(calcs)} Berechnungen):")
            for calc in calcs[:10]:  # Top 10
                doc = calc.get('docstring', '')[:60] if calc.get(
                    'docstring') else 'Keine Beschreibung'
                print(f"    • {calc['name']}() - Zeile {calc['lineno']}")
                print(f"      └─ {doc}...")

    print()
    print("=" * 100)

    # Chart-Features
    print(f"📈 CHART/DIAGRAMM-FEATURES ({len(all_chart_funcs)} gefunden):")
    print("-" * 100)
    for filename, result in all_results.items():
        charts = result.get('charts', [])
        if charts:
            print(f"\n  📁 {filename} ({len(charts)} Charts):")
            for chart in charts:
                doc = chart.get('docstring', '')[:60] if chart.get(
                    'docstring') else 'Keine Beschreibung'
                print(f"    • {chart['name']}() - Zeile {chart['lineno']}")
                print(f"      └─ {doc}...")

    print()
    print("=" * 100)

    # Finanzierungs-Features
    print(f"💰 FINANZIERUNGS-FEATURES ({len(all_financial_funcs)} gefunden):")
    print("-" * 100)
    for filename, result in all_results.items():
        fin_features = result.get('financial_features', [])
        if fin_features:
            print(f"\n  📁 {filename} ({len(fin_features)} Features):")
            for feat in fin_features:
                doc = feat.get('docstring', '')[:60] if feat.get(
                    'docstring') else 'Keine Beschreibung'
                print(f"    • {feat['name']}() - Zeile {feat['lineno']}")
                print(f"      └─ {doc}...")

    print()
    print("=" * 100)
    print("🔍 UI-INTEGRATION-CHECK")
    print("=" * 100)

    # Prüfe UI-Integration
    for ui_file in ui_files:
        if os.path.exists(ui_file):
            print(f"\n📄 Prüfe {ui_file}...")

            calc_refs = find_ui_references(ui_file, all_calculation_funcs)
            chart_refs = find_ui_references(ui_file, all_chart_funcs)
            fin_refs = find_ui_references(ui_file, all_financial_funcs)

            print(
                f"  ✅ Berechnungen gefunden: {len(calc_refs)}/{len(all_calculation_funcs)}")
            print(
                f"  ✅ Charts gefunden: {len(chart_refs)}/{len(all_chart_funcs)}")
            print(
                f"  ✅ Finanzierung gefunden: {len(fin_refs)}/{len(all_financial_funcs)}")

            # Fehlende Features
            missing_calcs = all_calculation_funcs - set(calc_refs)
            missing_charts = all_chart_funcs - set(chart_refs)
            missing_fin = all_financial_funcs - set(fin_refs)

            if missing_calcs:
                print(f"\n  ⚠️  FEHLENDE BERECHNUNGEN ({len(missing_calcs)}):")
                for func in list(missing_calcs)[:10]:
                    print(f"      • {func}()")

            if missing_charts:
                print(f"\n  ⚠️  FEHLENDE CHARTS ({len(missing_charts)}):")
                for func in list(missing_charts)[:10]:
                    print(f"      • {func}()")

            if missing_fin:
                print(
                    f"\n  ⚠️  FEHLENDE FINANZIERUNGS-FEATURES ({len(missing_fin)}):")
                for func in list(missing_fin)[:10]:
                    print(f"      • {func}()")

    print()
    print("=" * 100)
    print("✅ ANALYSE ABGESCHLOSSEN")
    print("=" * 100)

    # Exportiere Ergebnisse als JSON
    with open('feature_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'calculation_functions': list(all_calculation_funcs),
            'chart_functions': list(all_chart_funcs),
            'financial_functions': list(all_financial_funcs),
            'detailed_results': all_results
        }, f, indent=2, ensure_ascii=False)

    print("\n📝 Detaillierte Ergebnisse gespeichert in: feature_analysis_results.json")


if __name__ == '__main__':
    main()
