"""
Tests für Lazy Loading Funktionalität

Testet:
- ViewportRange
- LazyLoadCache mit LRU
- LazyGridLoader
- Virtuelles Scrolling
- Performance mit großen Datensätzen
"""

import pytest
from excel.excel_lazy_loader import (
    ViewportRange,
    LazyLoadCache,
    LazyGridLoader,
    create_lazy_loader
)
from excel.excel_models import Cell, ExcelMatrix


def create_test_matrix(rows: int = 1000, cols: int = 50) -> ExcelMatrix:
    """Erstellt eine Test-Matrix mit vielen Zellen"""
    matrix = ExcelMatrix(
        id=1,
        name="Test Matrix",
        description="Large test matrix",
        rows=rows,
        columns=cols,
        cells={},
        metadata={}
    )
    
    # Fülle mit Test-Daten
    for row in range(rows):
        for col in range(cols):
            value = f"R{row+1}C{col+1}"
            matrix.cells[(row, col)] = Cell(
                row=row,
                col=col,
                value=value,
                data_type="text"
            )
    
    return matrix


class TestViewportRange:
    """Tests für ViewportRange"""
    
    def test_contains(self):
        """Test: Prüft ob Zelle im Viewport liegt"""
        viewport = ViewportRange(0, 100, 0, 26)
        
        assert viewport.contains(0, 0) is True
        assert viewport.contains(50, 10) is True
        assert viewport.contains(99, 25) is True
        assert viewport.contains(100, 0) is False
        assert viewport.contains(0, 26) is False
    
    def test_get_cell_count(self):
        """Test: Berechnet Anzahl Zellen im Viewport"""
        viewport = ViewportRange(0, 100, 0, 26)
        assert viewport.get_cell_count() == 2600
        
        viewport = ViewportRange(10, 20, 5, 10)
        assert viewport.get_cell_count() == 50
    
    def test_expand(self):
        """Test: Erweitert Viewport um Buffer"""
        viewport = ViewportRange(10, 20, 5, 10)
        expanded = viewport.expand(buffer_rows=5, buffer_cols=2)
        
        assert expanded.start_row == 5
        assert expanded.end_row == 25
        assert expanded.start_col == 3
        assert expanded.end_col == 12
    
    def test_expand_with_boundary(self):
        """Test: Expansion respektiert Grenzen"""
        viewport = ViewportRange(0, 10, 0, 5)
        expanded = viewport.expand(buffer_rows=5, buffer_cols=2)
        
        # Start sollte nicht negativ werden
        assert expanded.start_row == 0
        assert expanded.start_col == 0


class TestLazyLoadCache:
    """Tests für LazyLoadCache mit LRU"""
    
    def test_put_and_get(self):
        """Test: Speichern und Abrufen von Zellen"""
        cache = LazyLoadCache(max_size=100)
        cell = Cell(row=0, col=0, value="Test")
        
        cache.put(0, 0, cell)
        retrieved = cache.get(0, 0)
        
        assert retrieved is not None
        assert retrieved.value == "Test"
    
    def test_lru_eviction(self):
        """Test: LRU-Strategie entfernt älteste Einträge"""
        cache = LazyLoadCache(max_size=3)
        
        # Füge 3 Zellen hinzu
        cache.put(0, 0, Cell(row=0, col=0, value="A"))
        cache.put(0, 1, Cell(row=0, col=1, value="B"))
        cache.put(0, 2, Cell(row=0, col=2, value="C"))
        
        # Greife auf erste Zelle zu (macht sie "recent")
        cache.get(0, 0)
        
        # Füge neue Zelle hinzu (sollte B entfernen, da älteste)
        cache.put(0, 3, Cell(row=0, col=3, value="D"))
        
        assert cache.get(0, 0) is not None  # A noch da
        assert cache.get(0, 1) is None      # B entfernt
        assert cache.get(0, 2) is not None  # C noch da
        assert cache.get(0, 3) is not None  # D neu
    
    def test_put_batch(self):
        """Test: Batch-Insert von Zellen"""
        cache = LazyLoadCache(max_size=100)
        cells = {
            (0, 0): Cell(row=0, col=0, value="A"),
            (0, 1): Cell(row=0, col=1, value="B"),
            (0, 2): Cell(row=0, col=2, value="C")
        }
        
        cache.put_batch(cells)
        
        assert cache.get(0, 0).value == "A"
        assert cache.get(0, 1).value == "B"
        assert cache.get(0, 2).value == "C"
    
    def test_clear(self):
        """Test: Cache leeren"""
        cache = LazyLoadCache(max_size=100)
        cache.put(0, 0, Cell(row=0, col=0, value="Test"))
        
        cache.clear()
        
        assert cache.get(0, 0) is None
        assert len(cache.cells) == 0
    
    def test_cache_stats(self):
        """Test: Cache-Statistiken"""
        cache = LazyLoadCache(max_size=100)
        cache.put(0, 0, Cell(row=0, col=0, value="A"))
        cache.put(0, 1, Cell(row=0, col=1, value="B"))
        
        stats = cache.get_cache_stats()
        
        assert stats['size'] == 2
        assert stats['max_size'] == 100
        assert stats['utilization'] == 0.02


class TestLazyGridLoader:
    """Tests für LazyGridLoader"""
    
    def test_initialization(self):
        """Test: Initialisierung lädt initiale Zellen"""
        matrix = create_test_matrix(rows=200, cols=30)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        # Prüfe dass Viewport gesetzt ist
        assert loader.viewport.start_row == 0
        assert loader.viewport.end_row == 50
        assert loader.viewport.start_col == 0
        assert loader.viewport.end_col == 10
        
        # Prüfe dass Zellen geladen wurden (mit Buffer)
        stats = loader.get_cache_stats()
        assert stats['size'] > 0
    
    def test_get_cell(self):
        """Test: Zelle abrufen"""
        matrix = create_test_matrix(rows=100, cols=20)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        cell = loader.get_cell(0, 0)
        
        assert cell is not None
        assert cell.value == "R1C1"
    
    def test_scroll_down(self):
        """Test: Nach unten scrollen"""
        matrix = create_test_matrix(rows=200, cols=30)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        initial_start = loader.viewport.start_row
        loader.scroll_down(rows=10)
        
        assert loader.viewport.start_row == initial_start + 10
        assert loader.viewport.end_row == initial_start + 60
    
    def test_scroll_up(self):
        """Test: Nach oben scrollen"""
        matrix = create_test_matrix(rows=200, cols=30)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        # Scrolle erst runter, dann hoch
        loader.scroll_down(rows=20)
        loader.scroll_up(rows=10)
        
        assert loader.viewport.start_row == 10
    
    def test_scroll_boundary(self):
        """Test: Scrolling respektiert Grenzen"""
        matrix = create_test_matrix(rows=100, cols=20)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        # Versuche über Ende hinaus zu scrollen
        loader.scroll_down(rows=100)
        
        assert loader.viewport.end_row <= 100
        
        # Versuche über Anfang hinaus zu scrollen
        loader.scroll_up(rows=200)
        
        assert loader.viewport.start_row == 0
    
    def test_scroll_right(self):
        """Test: Nach rechts scrollen"""
        matrix = create_test_matrix(rows=100, cols=50)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        initial_start = loader.viewport.start_col
        loader.scroll_right(cols=5)
        
        assert loader.viewport.start_col == initial_start + 5
    
    def test_scroll_left(self):
        """Test: Nach links scrollen"""
        matrix = create_test_matrix(rows=100, cols=50)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        loader.scroll_right(cols=10)
        loader.scroll_left(cols=5)
        
        assert loader.viewport.start_col == 5
    
    def test_jump_to_cell(self):
        """Test: Zu Zelle springen"""
        matrix = create_test_matrix(rows=1000, cols=50)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        loader.jump_to_cell(row=500, col=25)
        
        # Zelle sollte ungefähr in der Mitte des Viewports sein
        assert loader.viewport.start_row <= 500 < loader.viewport.end_row
        assert loader.viewport.start_col <= 25 < loader.viewport.end_col
    
    def test_get_visible_dataframe(self):
        """Test: DataFrame mit sichtbaren Zellen"""
        matrix = create_test_matrix(rows=100, cols=20)
        loader = LazyGridLoader(matrix, viewport_rows=10, viewport_cols=5)
        
        df = loader.get_visible_dataframe()
        
        assert df.shape == (10, 5)
        assert df.iloc[0, 0] == "R1C1"
        assert df.columns[0] == "A"
        assert df.index[0] == "1"
    
    def test_refresh_viewport(self):
        """Test: Viewport neu laden"""
        matrix = create_test_matrix(rows=100, cols=20)
        loader = LazyGridLoader(matrix, viewport_rows=50, viewport_cols=10)
        
        # Ändere Zelle in Matrix
        matrix.cells[(0, 0)].value = "CHANGED"
        
        # Refresh sollte neue Werte laden
        loader.refresh_viewport()
        cell = loader.get_cell(0, 0)
        
        assert cell.value == "CHANGED"
    
    def test_col_num_to_label(self):
        """Test: Spaltennummer zu Label konvertieren"""
        assert LazyGridLoader._col_num_to_label(0) == "A"
        assert LazyGridLoader._col_num_to_label(25) == "Z"
        assert LazyGridLoader._col_num_to_label(26) == "AA"
        assert LazyGridLoader._col_num_to_label(27) == "AB"
        assert LazyGridLoader._col_num_to_label(51) == "AZ"
        assert LazyGridLoader._col_num_to_label(52) == "BA"


class TestPerformance:
    """Performance-Tests für große Datensätze"""
    
    def test_large_matrix_loading(self):
        """Test: Laden einer großen Matrix (1000x50)"""
        import time
        
        matrix = create_test_matrix(rows=1000, cols=50)
        
        start = time.time()
        loader = LazyGridLoader(matrix, viewport_rows=100, viewport_cols=26)
        end = time.time()
        
        # Initialisierung sollte schnell sein (< 1 Sekunde)
        assert end - start < 1.0
        
        # Cache sollte nur Viewport + Buffer enthalten, nicht alle Zellen
        stats = loader.get_cache_stats()
        assert stats['size'] < 1000 * 50  # Nicht alle Zellen geladen
    
    def test_scrolling_performance(self):
        """Test: Scrolling-Performance"""
        import time
        
        matrix = create_test_matrix(rows=1000, cols=50)
        loader = LazyGridLoader(matrix, viewport_rows=100, viewport_cols=26)
        
        start = time.time()
        for _ in range(10):
            loader.scroll_down(rows=10)
        end = time.time()
        
        # 10 Scroll-Operationen sollten schnell sein (< 0.5 Sekunden)
        assert end - start < 0.5
    
    def test_cache_efficiency(self):
        """Test: Cache-Effizienz bei wiederholtem Zugriff"""
        matrix = create_test_matrix(rows=1000, cols=50)
        loader = LazyGridLoader(matrix, viewport_rows=100, viewport_cols=26, cache_size=5000)
        
        # Erster Zugriff
        loader.get_cell(0, 0)
        
        # Zweiter Zugriff sollte aus Cache kommen
        import time
        start = time.time()
        for _ in range(100):
            loader.get_cell(0, 0)
        end = time.time()
        
        # 100 Cache-Zugriffe sollten sehr schnell sein (< 0.1 Sekunden)
        assert end - start < 0.1


def test_create_lazy_loader():
    """Test: Factory-Funktion"""
    matrix = create_test_matrix(rows=100, cols=20)
    loader = create_lazy_loader(matrix, viewport_rows=50, viewport_cols=10)
    
    assert isinstance(loader, LazyGridLoader)
    assert loader.viewport.end_row == 50
    assert loader.viewport.end_col == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
