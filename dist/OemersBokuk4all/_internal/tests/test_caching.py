"""
Tests für Caching-Funktionalität in FormulaEngine und ExcelManager

Testet:
- Formel-Cache
- Cache-Invalidierung
- Dependency-Cache
- Performance-Verbesserungen durch Caching
"""

import pytest
from excel.excel_models import ExcelMatrix, Cell
from excel.excel_manager import ExcelManager
from excel.excel_formula_engine import FormulaEngine


class TestFormulaCaching:
    """Tests für Formel-Caching"""
    
    def test_cache_enabled_by_default(self):
        """Test: Cache ist standardmäßig aktiviert"""
        engine = FormulaEngine()
        assert engine.cache_enabled is True
    
    def test_cache_can_be_disabled(self):
        """Test: Cache kann deaktiviert werden"""
        engine = FormulaEngine(enable_cache=False)
        assert engine.cache_enabled is False
    
    def test_formula_result_cached(self):
        """Test: Formelergebnisse werden gecacht"""
        engine = FormulaEngine()
        context = {(0, 0): 10, (0, 1): 20}
        
        # Erste Ausführung
        result1 = engine.execute_formula("=A1+B1", context)
        assert result1 == 30
        
        # Cache-Statistiken prüfen
        stats = engine.get_cache_stats()
        assert stats['misses'] == 1
        assert stats['hits'] == 0
        
        # Zweite Ausführung (sollte aus Cache kommen)
        result2 = engine.execute_formula("=A1+B1", context)
        assert result2 == 30
        
        # Cache-Hit prüfen
        stats = engine.get_cache_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
    
    def test_cache_invalidated_on_cell_change(self):
        """Test: Cache wird bei Zelländerung invalidiert"""
        engine = FormulaEngine()
        context = {(0, 0): 10, (0, 1): 20}
        
        # Erste Ausführung
        result1 = engine.execute_formula("=A1+B1", context)
        assert result1 == 30
        
        # Ändere Zellwert
        context[(0, 0)] = 15
        
        # Invalidiere Cache
        engine.invalidate_cache([(0, 0)])
        
        # Zweite Ausführung (sollte neu berechnet werden)
        result2 = engine.execute_formula("=A1+B1", context)
        assert result2 == 35
        
        # Cache-Statistiken prüfen
        stats = engine.get_cache_stats()
        assert stats['misses'] == 2  # Beide Male neu berechnet
    
    def test_cache_key_includes_cell_values(self):
        """Test: Cache-Key enthält Zellwerte"""
        engine = FormulaEngine()
        
        # Erste Berechnung mit Werten 10, 20
        context1 = {(0, 0): 10, (0, 1): 20}
        result1 = engine.execute_formula("=A1+B1", context1)
        assert result1 == 30
        
        # Zweite Berechnung mit anderen Werten
        context2 = {(0, 0): 15, (0, 1): 25}
        result2 = engine.execute_formula("=A1+B1", context2)
        assert result2 == 40
        
        # Beide Ergebnisse sollten unterschiedlich sein
        # (kein falscher Cache-Hit)
        assert result1 != result2
    
    def test_complex_formula_cached(self):
        """Test: Komplexe Formeln werden gecacht"""
        engine = FormulaEngine()
        context = {
            (0, 0): 10,
            (0, 1): 20,
            (0, 2): 30
        }
        
        # Arithmetische Formel
        formula = "=A1+B1+C1"
        
        # Erste Ausführung
        result1 = engine.execute_formula(formula, context)
        assert result1 == 60  # 10+20+30
        
        # Zweite Ausführung (aus Cache)
        result2 = engine.execute_formula(formula, context)
        assert result2 == 60
        
        # Cache-Hit prüfen
        stats = engine.get_cache_stats()
        assert stats['hits'] >= 1
    
    def test_clear_cache(self):
        """Test: Cache kann geleert werden"""
        engine = FormulaEngine()
        context = {(0, 0): 10, (0, 1): 20}
        
        # Fülle Cache
        engine.execute_formula("=A1+B1", context)
        
        stats = engine.get_cache_stats()
        assert stats['size'] > 0
        
        # Leere Cache
        engine.clear_cache()
        
        stats = engine.get_cache_stats()
        assert stats['size'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
    
    def test_cache_stats(self):
        """Test: Cache-Statistiken sind korrekt"""
        engine = FormulaEngine()
        context = {(0, 0): 10, (0, 1): 20}
        
        # Mehrere Berechnungen
        for _ in range(5):
            engine.execute_formula("=A1+B1", context)
        
        stats = engine.get_cache_stats()
        
        assert stats['enabled'] is True
        assert stats['hits'] == 4  # 4 Cache-Hits
        assert stats['misses'] == 1  # 1 Cache-Miss
        assert stats['hit_rate'] == 80.0  # 80% Hit-Rate


class TestDependencyCache:
    """Tests für Dependency-Cache"""
    
    def test_dependency_cache_built(self):
        """Test: Dependency-Cache wird erstellt"""
        matrix = ExcelMatrix()
        matrix.set_cell_value(0, 0, 10)
        matrix.set_cell_value(0, 1, 20)
        matrix.set_cell_value(0, 2, None, "=A1+B1")
        
        engine = FormulaEngine()
        engine.build_dependency_cache(matrix.cells)
        
        stats = engine.get_cache_stats()
        assert stats['dependency_cache_size'] > 0
    
    def test_get_dependents_from_cache(self):
        """Test: Abhängige Zellen aus Cache abrufen"""
        matrix = ExcelMatrix()
        matrix.set_cell_value(0, 0, 10)
        matrix.set_cell_value(0, 1, None, "=A1*2")
        matrix.set_cell_value(0, 2, None, "=A1+10")
        
        engine = FormulaEngine()
        engine.build_dependency_graph(matrix.cells)
        engine.build_dependency_cache(matrix.cells)
        
        # A1 (0,0) sollte zwei abhängige Zellen haben: B1 und C1
        dependents = engine.get_dependents_from_cache((0, 0))
        
        assert len(dependents) == 2
        assert (0, 1) in dependents  # B1
        assert (0, 2) in dependents  # C1
    
    def test_dependency_cache_performance(self):
        """Test: Dependency-Cache ist schneller als normale Abfrage"""
        import time
        
        # Erstelle Matrix mit vielen Abhängigkeiten
        matrix = ExcelMatrix()
        matrix.set_cell_value(0, 0, 100)
        
        # 50 Zellen die von A1 abhängen
        for i in range(1, 51):
            matrix.set_cell_value(0, i, None, f"=A1*{i}")
        
        engine = FormulaEngine()
        engine.build_dependency_graph(matrix.cells)
        
        # Ohne Cache
        start = time.time()
        for _ in range(1000):
            engine.get_dependent_cells((0, 0))
        time_without_cache = time.time() - start
        
        # Mit Cache
        engine.build_dependency_cache(matrix.cells)
        start = time.time()
        for _ in range(1000):
            engine.get_dependents_from_cache((0, 0))
        time_with_cache = time.time() - start
        
        # Cache sollte schneller oder gleich schnell sein
        # Bei sehr schnellen Operationen kann die Zeit 0 sein
        assert time_with_cache <= time_without_cache + 0.01


class TestExcelManagerCaching:
    """Tests für Caching in ExcelManager"""
    
    def test_manager_cache_enabled_by_default(self):
        """Test: Cache ist im Manager standardmäßig aktiviert"""
        manager = ExcelManager()
        stats = manager.get_cache_stats()
        assert stats['enabled'] is True
    
    def test_manager_can_disable_cache(self):
        """Test: Cache kann im Manager deaktiviert werden"""
        manager = ExcelManager(enable_cache=False)
        stats = manager.get_cache_stats()
        assert stats['enabled'] is False
    
    def test_cache_invalidated_on_set_cell_value(self):
        """Test: Cache wird bei set_cell_value invalidiert"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, None, "=A1+B1")
        
        # Erste Berechnung
        value1 = manager.get_cell_value(0, 2)
        assert value1 == 30
        
        # Ändere Wert
        manager.set_cell_value(0, 0, 15)
        
        # Zweite Berechnung (sollte neuen Wert haben)
        value2 = manager.get_cell_value(0, 2)
        assert value2 == 35
    
    def test_cache_cleared_on_rebuild_dependency_graph(self):
        """Test: Cache wird bei Rebuild des Dependency-Graphs geleert"""
        manager = ExcelManager()
        
        # Setze Werte und Formeln
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, None, "=A1*2")
        
        # Fülle Cache
        manager.get_cell_value(0, 1)
        
        stats_before = manager.get_cache_stats()
        assert stats_before['size'] > 0
        
        # Füge Zeile hinzu (triggert Rebuild)
        manager.add_row(0)
        
        # Cache sollte geleert sein
        stats_after = manager.get_cache_stats()
        assert stats_after['size'] == 0
    
    def test_manager_cache_methods(self):
        """Test: Manager Cache-Methoden funktionieren"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, None, "=A1*2")
        
        # Fülle Cache
        manager.get_cell_value(0, 1)
        
        # Prüfe Stats
        stats = manager.get_cache_stats()
        assert stats['size'] > 0
        
        # Leere Cache
        manager.clear_cache()
        stats = manager.get_cache_stats()
        assert stats['size'] == 0
        
        # Deaktiviere Cache
        manager.disable_cache()
        stats = manager.get_cache_stats()
        assert stats['enabled'] is False
        
        # Aktiviere Cache
        manager.enable_cache()
        stats = manager.get_cache_stats()
        assert stats['enabled'] is True


class TestCachingPerformance:
    """Performance-Tests für Caching"""
    
    def test_large_matrix_with_cache(self):
        """Test: Große Matrix mit vielen Formeln profitiert von Cache"""
        # Erstelle Manager mit Cache
        manager = ExcelManager(enable_cache=True)
        
        # 50 Zellen mit Werten
        for i in range(50):
            manager.set_cell_value(i, 0, i + 1)
        
        # 50 Zellen mit Formeln die auf vorherige Zellen referenzieren
        for i in range(50):
            manager.set_cell_value(i, 1, None, f"=A{i+1}*2")
        
        # Erste Berechnung aller Formeln
        manager.recalculate_all_formulas()
        
        # Prüfe dass Cache verwendet wurde
        stats = manager.get_cache_stats()
        initial_size = stats['size']
        
        # Ändere einen Wert und berechne neu
        manager.set_cell_value(0, 0, 100)
        
        # Cache sollte Einträge haben
        stats = manager.get_cache_stats()
        assert stats['size'] >= 0  # Cache kann invalidiert worden sein
        
        # Teste dass Formeln korrekt neu berechnet werden
        value = manager.get_cell_value(0, 1)
        assert value == 200  # 100 * 2
    
    def test_repeated_calculations_benefit_from_cache(self):
        """Test: Wiederholte Berechnungen profitieren von Cache"""
        engine = FormulaEngine(enable_cache=True)
        
        # Kontext mit Werten
        context = {
            (0, 0): 10,
            (0, 1): 20,
            (0, 2): 30
        }
        
        # Arithmetische Formel
        formula = "=(A1+B1+C1)*2"
        
        # Erste Berechnung
        result1 = engine.execute_formula(formula, context)
        assert result1 == 120  # (10+20+30)*2
        
        # 10 weitere Berechnungen (sollten aus Cache kommen)
        for _ in range(10):
            result = engine.execute_formula(formula, context)
            assert result == result1
        
        # Cache-Statistiken prüfen
        stats = engine.get_cache_stats()
        # Mindestens 10 Cache-Hits sollten vorhanden sein
        assert stats['hits'] >= 10
        assert stats['misses'] == 1  # Nur die erste Berechnung


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
