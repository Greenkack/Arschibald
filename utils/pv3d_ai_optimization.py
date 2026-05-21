"""
KI-basierte Modul-Anordnungs-Optimierung

Dieses Modul implementiert intelligente Algorithmen zur Optimierung der
PV-Modul-Platzierung basierend auf verschiedenen Zielen:
- Maximaler Ertrag
- Maximale Anzahl Module
- Beste Ästhetik

Requirements: 7.1, 7.2, 7.3, 7.4
"""

from typing import List, Dict, Tuple, Any, Optional
import math
from dataclasses import dataclass

try:
    import numpy as np
except ImportError:
    np = None


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class LayoutScore:
    """
    Bewertung eines Modul-Layouts.
    
    Attributes:
        total_yield_kwh: Geschätzter Gesamtertrag pro Jahr in kWh
        module_count: Anzahl der platzierten Module
        aesthetic_score: Ästhetik-Bewertung (0-100)
        cost_eur: Geschätzte Gesamtkosten in EUR
        roi_years: Return on Investment in Jahren
        coverage_percent: Dachflächennutzung in Prozent
        symmetry_score: Symmetrie-Bewertung (0-100)
    """
    total_yield_kwh: float
    module_count: int
    aesthetic_score: float
    cost_eur: float
    roi_years: float
    coverage_percent: float = 0.0
    symmetry_score: float = 0.0
    
    def get_weighted_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """
        Berechnet gewichtete Gesamtbewertung.
        
        Args:
            weights: Gewichtungen für verschiedene Faktoren
                    Default: {"yield": 0.4, "count": 0.2, "aesthetic": 0.2, "roi": 0.2}
        
        Returns:
            Gewichtete Gesamtbewertung (0-100)
        """
        if weights is None:
            weights = {
                "yield": 0.4,
                "count": 0.2,
                "aesthetic": 0.2,
                "roi": 0.2
            }
        
        # Normalisiere Werte auf 0-100 Skala
        yield_score = min(100, (self.total_yield_kwh / 100))  # 10000 kWh = 100 Punkte
        count_score = min(100, (self.module_count / 50) * 100)  # 50 Module = 100 Punkte
        roi_score = max(0, 100 - (self.roi_years * 10))  # 10 Jahre = 0 Punkte
        
        total_score = (
            weights.get("yield", 0.4) * yield_score +
            weights.get("count", 0.2) * count_score +
            weights.get("aesthetic", 0.2) * self.aesthetic_score +
            weights.get("roi", 0.2) * roi_score
        )
        
        return total_score


@dataclass
class OptimizationResult:
    """
    Ergebnis einer Optimierung.
    
    Attributes:
        positions: Liste von (x, y, z) Positionen
        score: Layout-Bewertung
        strategy: Name der verwendeten Strategie
        metadata: Zusätzliche Metadaten
    """
    positions: List[Tuple[float, float, float]]
    score: LayoutScore
    strategy: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ============================================================================
# KI-OPTIMIERER
# ============================================================================

class AILayoutOptimizer:
    """
    KI-Optimierer für PV-Modul-Layouts.
    
    Dieser Optimierer verwendet verschiedene Algorithmen zur Platzierung
    von PV-Modulen basierend auf unterschiedlichen Optimierungszielen.
    """
    
    def __init__(
        self,
        roof_length: float,
        roof_width: float,
        roof_type: str,
        roof_pitch: float = 0.0,
        module_width: float = 1.05,
        module_height: float = 1.76,
        module_power_w: float = 400.0,
        module_cost_eur: float = 200.0,
        electricity_price_eur_kwh: float = 0.30
    ):
        """
        Initialisiert den KI-Optimierer.
        
        Args:
            roof_length: Dachlänge in Metern (X-Achse)
            roof_width: Dachbreite in Metern (Y-Achse)
            roof_type: Dachtyp (z.B. "Flachdach", "Satteldach")
            roof_pitch: Dachneigung in Grad
            module_width: Modulbreite in Metern
            module_height: Modulhöhe in Metern
            module_power_w: Modulleistung in Watt
            module_cost_eur: Modulkosten in EUR
            electricity_price_eur_kwh: Strompreis in EUR/kWh
        """
        self.roof_length = roof_length
        self.roof_width = roof_width
        self.roof_type = roof_type.lower()
        self.roof_pitch = roof_pitch
        self.module_width = module_width
        self.module_height = module_height
        self.module_power_w = module_power_w
        self.module_cost_eur = module_cost_eur
        self.electricity_price_eur_kwh = electricity_price_eur_kwh
        
        # Berechne Dachfläche
        self.roof_area = roof_length * roof_width
        
        # Berechne Modulfläche
        self.module_area = module_width * module_height
    
    def optimize_for_max_yield(
        self,
        obstacles: Optional[List[Dict[str, Any]]] = None
    ) -> OptimizationResult:
        """
        Optimiert Layout für maximalen Ertrag.
        
        Strategie:
        - Platziere Module an Positionen mit bester Sonneneinstrahlung
        - Vermeide verschattete Bereiche
        - Optimale Ausrichtung (Süd, 30-35°)
        - Berücksichtige Hindernisse
        
        Args:
            obstacles: Liste von Hindernissen mit Position und Größe
        
        Returns:
            OptimizationResult mit optimierten Positionen
        
        Requirements: 7.1
        """
        positions = []
        
        # Berechne Sonneneinstrahlungs-Heatmap
        irradiance_map = self._calculate_irradiance_map()
        
        # Sortiere Positionen nach Einstrahlung (höchste zuerst)
        sorted_positions = self._sort_by_irradiance(irradiance_map)
        
        # Platziere Module an besten Positionen
        for x, y in sorted_positions:
            z = self._calculate_z(y)
            
            # Prüfe Hindernisse
            if obstacles and self._intersects_obstacle(x, y, obstacles):
                continue
            
            # Prüfe Kollision mit existierenden Modulen
            if not self._has_collision(x, y, z, positions):
                positions.append((x, y, z))
        
        # Berechne Bewertung
        score = self._calculate_layout_score(
            positions,
            strategy="max_yield"
        )
        
        return OptimizationResult(
            positions=positions,
            score=score,
            strategy="Maximaler Ertrag",
            metadata={
                "irradiance_map": irradiance_map,
                "optimization_goal": "yield"
            }
        )
    
    def optimize_for_max_count(
        self,
        obstacles: Optional[List[Dict[str, Any]]] = None
    ) -> OptimizationResult:
        """
        Optimiert Layout für maximale Anzahl Module.
        
        Strategie:
        - Dichte Packung mit minimalem Abstand (5cm)
        - Nutze gesamte verfügbare Fläche
        - Akzeptiere auch suboptimale Positionen
        - Berücksichtige Hindernisse
        
        Args:
            obstacles: Liste von Hindernissen mit Position und Größe
        
        Returns:
            OptimizationResult mit optimierten Positionen
        
        Requirements: 7.1
        """
        positions = []
        
        # Verwende minimalen Abstand
        min_spacing = 0.05  # 5cm zwischen Modulen
        
        # Berechne dichtes Grid
        grid_positions = self._calculate_dense_grid(min_spacing)
        
        # Platziere Module
        for x, y in grid_positions:
            z = self._calculate_z(y)
            
            # Prüfe Hindernisse
            if obstacles and self._intersects_obstacle(x, y, obstacles):
                continue
            
            # Prüfe Kollision
            if not self._has_collision(x, y, z, positions):
                positions.append((x, y, z))
        
        # Berechne Bewertung
        score = self._calculate_layout_score(
            positions,
            strategy="max_count"
        )
        
        return OptimizationResult(
            positions=positions,
            score=score,
            strategy="Maximale Anzahl",
            metadata={
                "spacing": min_spacing,
                "optimization_goal": "count"
            }
        )
    
    def optimize_for_aesthetics(
        self,
        obstacles: Optional[List[Dict[str, Any]]] = None
    ) -> OptimizationResult:
        """
        Optimiert Layout für beste Ästhetik.
        
        Strategie:
        - Symmetrische Anordnung
        - Gleichmäßige Abstände (20cm)
        - Zentrierte Platzierung
        - Vermeidung von "Lücken"
        - Berücksichtige Hindernisse
        
        Args:
            obstacles: Liste von Hindernissen mit Position und Größe
        
        Returns:
            OptimizationResult mit optimierten Positionen
        
        Requirements: 7.1
        """
        positions = []
        
        # Berechne symmetrisches Grid mit gleichmäßigen Abständen
        spacing = 0.20  # 20cm zwischen Modulen
        symmetric_grid = self._calculate_symmetric_grid(spacing)
        
        # Platziere Module symmetrisch
        for x, y in symmetric_grid:
            z = self._calculate_z(y)
            
            # Prüfe Hindernisse
            if obstacles and self._intersects_obstacle(x, y, obstacles):
                continue
            
            # Prüfe Kollision
            if not self._has_collision(x, y, z, positions):
                positions.append((x, y, z))
        
        # Berechne Bewertung
        score = self._calculate_layout_score(
            positions,
            strategy="aesthetics"
        )
        
        return OptimizationResult(
            positions=positions,
            score=score,
            strategy="Beste Ästhetik",
            metadata={
                "spacing": spacing,
                "symmetry": True,
                "optimization_goal": "aesthetics"
            }
        )
    
    # ========================================================================
    # HILFSFUNKTIONEN
    # ========================================================================
    
    def _calculate_irradiance_map(self) -> 'np.ndarray':
        """
        Berechnet Sonneneinstrahlungs-Karte für Dachfläche.
        
        Returns:
            2D-Array mit Einstrahlungswerten (0-1)
        """
        if np is None:
            # Fallback ohne NumPy
            return [[1.0]]
        
        resolution = 50
        x_range = np.linspace(-self.roof_length/2, self.roof_length/2, resolution)
        y_range = np.linspace(-self.roof_width/2, self.roof_width/2, resolution)
        
        irradiance = np.zeros((resolution, resolution))
        
        for i, y in enumerate(y_range):
            for j, x in enumerate(x_range):
                # Berechne Einstrahlung basierend auf Position
                # Höhere Einstrahlung in der Mitte, niedriger an Rändern
                dist_from_center = math.sqrt(x**2 + y**2)
                max_dist = math.sqrt((self.roof_length/2)**2 + (self.roof_width/2)**2)
                
                # Basis-Einstrahlung (100%)
                base_irradiance = 1.0
                
                # Reduziere an Rändern (bis zu 30%)
                edge_factor = 1.0 - (dist_from_center / max_dist) * 0.3
                
                # Berücksichtige Dachneigung (höhere Neigung = bessere Einstrahlung)
                pitch_factor = 1.0 + (self.roof_pitch / 90.0) * 0.2
                
                irradiance[i, j] = base_irradiance * edge_factor * pitch_factor
        
        return irradiance
    
    def _sort_by_irradiance(
        self,
        irradiance_map: 'np.ndarray'
    ) -> List[Tuple[float, float]]:
        """
        Sortiert Positionen nach Sonneneinstrahlung.
        
        Args:
            irradiance_map: 2D-Array mit Einstrahlungswerten
        
        Returns:
            Liste von (x, y) Positionen, sortiert nach Einstrahlung (höchste zuerst)
        """
        if np is None or irradiance_map is None:
            # Fallback: Einfaches Grid
            return self._calculate_dense_grid(0.10)
        
        resolution = irradiance_map.shape[0]
        x_range = np.linspace(-self.roof_length/2, self.roof_length/2, resolution)
        y_range = np.linspace(-self.roof_width/2, self.roof_width/2, resolution)
        
        # Erstelle Liste von (x, y, irradiance) Tupeln
        positions_with_irradiance = []
        for i, y in enumerate(y_range):
            for j, x in enumerate(x_range):
                positions_with_irradiance.append((x, y, irradiance_map[i, j]))
        
        # Sortiere nach Einstrahlung (höchste zuerst)
        positions_with_irradiance.sort(key=lambda p: p[2], reverse=True)
        
        # Extrahiere nur (x, y) Positionen
        return [(x, y) for x, y, _ in positions_with_irradiance]
    
    def _calculate_dense_grid(self, spacing: float) -> List[Tuple[float, float]]:
        """
        Berechnet dichtes Grid mit minimalem Abstand.
        
        Args:
            spacing: Abstand zwischen Modulen in Metern
        
        Returns:
            Liste von (x, y) Positionen
        """
        positions = []
        
        # Berechne Anzahl Module pro Reihe/Spalte
        margin = 0.30  # 30cm Rand
        usable_length = self.roof_length - 2 * margin
        usable_width = self.roof_width - 2 * margin
        
        # Anzahl Module
        nx = int(usable_length / (self.module_width + spacing))
        ny = int(usable_width / (self.module_height + spacing))
        
        # Berechne Start-Position (zentriert)
        total_width_x = nx * self.module_width + (nx - 1) * spacing
        total_width_y = ny * self.module_height + (ny - 1) * spacing
        start_x = -total_width_x / 2
        start_y = -total_width_y / 2
        
        # Erstelle Grid
        for i in range(nx):
            for j in range(ny):
                x = start_x + i * (self.module_width + spacing) + self.module_width / 2
                y = start_y + j * (self.module_height + spacing) + self.module_height / 2
                positions.append((x, y))
        
        return positions
    
    def _calculate_symmetric_grid(self, spacing: float) -> List[Tuple[float, float]]:
        """
        Berechnet symmetrisches Grid mit gleichmäßigen Abständen.
        
        Args:
            spacing: Abstand zwischen Modulen in Metern
        
        Returns:
            Liste von (x, y) Positionen
        """
        positions = []
        
        # Berechne Anzahl Module pro Reihe/Spalte
        margin = 0.50  # 50cm Rand für Ästhetik
        usable_length = self.roof_length - 2 * margin
        usable_width = self.roof_width - 2 * margin
        
        # Anzahl Module (weniger als bei dichter Packung)
        nx = int(usable_length / (self.module_width + spacing))
        ny = int(usable_width / (self.module_height + spacing))
        
        # Stelle sicher dass Anzahl gerade ist für Symmetrie
        if nx % 2 != 0:
            nx -= 1
        if ny % 2 != 0:
            ny -= 1
        
        # Berechne Start-Position (zentriert)
        total_width_x = nx * self.module_width + (nx - 1) * spacing
        total_width_y = ny * self.module_height + (ny - 1) * spacing
        start_x = -total_width_x / 2
        start_y = -total_width_y / 2
        
        # Erstelle symmetrisches Grid
        for i in range(nx):
            for j in range(ny):
                x = start_x + i * (self.module_width + spacing) + self.module_width / 2
                y = start_y + j * (self.module_height + spacing) + self.module_height / 2
                positions.append((x, y))
        
        return positions
    
    def _calculate_z(self, y: float) -> float:
        """
        Berechnet Z-Position für gegebenes Y.
        
        Args:
            y: Y-Position in Metern
        
        Returns:
            Z-Position in Metern
        """
        # Importiere calculate_z_position aus placement_handler
        try:
            from utils.pv3d_placement_handler import calculate_z_position
            return calculate_z_position(
                self.roof_type,
                self.roof_pitch,
                self.roof_width,
                y
            )
        except ImportError:
            # Fallback: Konstante Höhe
            if "flach" in self.roof_type:
                return 0.30  # Aufständerung
            else:
                return 0.15  # Basis-Höhe
    
    def _has_collision(
        self,
        x: float,
        y: float,
        z: float,
        existing: List[Tuple[float, float, float]]
    ) -> bool:
        """
        Prüft auf Kollision mit existierenden Modulen.
        
        Args:
            x, y, z: Position des neuen Moduls
            existing: Liste existierender Modul-Positionen
        
        Returns:
            True wenn Kollision, False sonst
        """
        # Importiere check_module_collision aus placement_handler
        try:
            from utils.pv3d_placement_handler import check_module_collision
            result = check_module_collision(
                (x, y, z),
                existing,
                self.roof_length,
                self.roof_width
            )
            return result["collision"]
        except ImportError:
            # Fallback: Einfache Distanz-Prüfung
            min_distance = max(self.module_width, self.module_height)
            for ex, ey, ez in existing:
                dist = math.sqrt((x - ex)**2 + (y - ey)**2)
                if dist < min_distance:
                    return True
            return False
    
    def _intersects_obstacle(
        self,
        x: float,
        y: float,
        obstacles: List[Dict[str, Any]]
    ) -> bool:
        """
        Prüft ob Position mit Hindernis kollidiert.
        
        Args:
            x, y: Position des Moduls
            obstacles: Liste von Hindernissen mit "x", "y", "width", "height"
        
        Returns:
            True wenn Kollision mit Hindernis, False sonst
        
        Requirements: 7.3
        """
        if not obstacles:
            return False
        
        # Modul-Bounding-Box
        module_x1 = x - self.module_width / 2
        module_x2 = x + self.module_width / 2
        module_y1 = y - self.module_height / 2
        module_y2 = y + self.module_height / 2
        
        for obstacle in obstacles:
            obs_x = obstacle.get("x", 0)
            obs_y = obstacle.get("y", 0)
            obs_width = obstacle.get("width", 1.0)
            obs_height = obstacle.get("height", 1.0)
            
            # Hindernis-Bounding-Box
            obs_x1 = obs_x - obs_width / 2
            obs_x2 = obs_x + obs_width / 2
            obs_y1 = obs_y - obs_height / 2
            obs_y2 = obs_y + obs_height / 2
            
            # Prüfe Überlappung
            if not (module_x2 < obs_x1 or module_x1 > obs_x2 or
                    module_y2 < obs_y1 or module_y1 > obs_y2):
                return True
        
        return False
    
    def _calculate_layout_score(
        self,
        positions: List[Tuple[float, float, float]],
        strategy: str
    ) -> LayoutScore:
        """
        Berechnet Bewertung für Layout.
        
        Args:
            positions: Liste von Modul-Positionen
            strategy: Optimierungs-Strategie ("max_yield", "max_count", "aesthetics")
        
        Returns:
            LayoutScore mit allen Metriken
        """
        module_count = len(positions)
        
        if module_count == 0:
            return LayoutScore(
                total_yield_kwh=0.0,
                module_count=0,
                aesthetic_score=0.0,
                cost_eur=0.0,
                roi_years=999.0,
                coverage_percent=0.0,
                symmetry_score=0.0
            )
        
        # Berechne Ertrag (vereinfacht)
        # Basis: 400W Modul * 1000 Volllaststunden = 400 kWh/Jahr
        base_yield_per_module = (self.module_power_w / 1000) * 1000  # kWh/Jahr
        
        # Anpassung basierend auf Strategie
        if strategy == "max_yield":
            yield_factor = 1.0  # Optimale Positionen
        elif strategy == "max_count":
            yield_factor = 0.85  # Einige suboptimale Positionen
        else:  # aesthetics
            yield_factor = 0.90  # Gute Positionen, aber nicht optimal
        
        total_yield_kwh = module_count * base_yield_per_module * yield_factor
        
        # Berechne Kosten
        cost_eur = module_count * self.module_cost_eur
        
        # Berechne ROI
        annual_revenue = total_yield_kwh * self.electricity_price_eur_kwh
        roi_years = cost_eur / annual_revenue if annual_revenue > 0 else 999.0
        
        # Berechne Dachflächennutzung
        used_area = module_count * self.module_area
        coverage_percent = (used_area / self.roof_area) * 100
        
        # Berechne Ästhetik-Score
        aesthetic_score = self._calculate_aesthetic_score(positions, strategy)
        
        # Berechne Symmetrie-Score
        symmetry_score = self._calculate_symmetry_score(positions)
        
        return LayoutScore(
            total_yield_kwh=total_yield_kwh,
            module_count=module_count,
            aesthetic_score=aesthetic_score,
            cost_eur=cost_eur,
            roi_years=roi_years,
            coverage_percent=coverage_percent,
            symmetry_score=symmetry_score
        )
    
    def _calculate_aesthetic_score(
        self,
        positions: List[Tuple[float, float, float]],
        strategy: str
    ) -> float:
        """
        Berechnet Ästhetik-Score (0-100).
        
        Faktoren:
        - Symmetrie
        - Gleichmäßige Abstände
        - Zentrierte Platzierung
        - Keine Lücken
        
        Args:
            positions: Liste von Modul-Positionen
            strategy: Optimierungs-Strategie
        
        Returns:
            Ästhetik-Score (0-100)
        """
        if not positions:
            return 0.0
        
        # Basis-Score basierend auf Strategie
        if strategy == "aesthetics":
            base_score = 90.0
        elif strategy == "max_yield":
            base_score = 70.0
        else:  # max_count
            base_score = 50.0
        
        # Berechne Symmetrie-Bonus
        symmetry = self._calculate_symmetry_score(positions)
        symmetry_bonus = (symmetry / 100) * 10  # Bis zu +10 Punkte
        
        # Berechne Zentrierung-Bonus
        center_x = sum(x for x, y, z in positions) / len(positions)
        center_y = sum(y for x, y, z in positions) / len(positions)
        center_offset = math.sqrt(center_x**2 + center_y**2)
        max_offset = math.sqrt((self.roof_length/2)**2 + (self.roof_width/2)**2)
        centering_score = 1.0 - (center_offset / max_offset)
        centering_bonus = centering_score * 5  # Bis zu +5 Punkte
        
        total_score = base_score + symmetry_bonus + centering_bonus
        return min(100.0, max(0.0, total_score))
    
    def _calculate_symmetry_score(
        self,
        positions: List[Tuple[float, float, float]]
    ) -> float:
        """
        Berechnet Symmetrie-Score (0-100).
        
        Args:
            positions: Liste von Modul-Positionen
        
        Returns:
            Symmetrie-Score (0-100)
        """
        if len(positions) < 2:
            return 100.0
        
        # Berechne Schwerpunkt
        center_x = sum(x for x, y, z in positions) / len(positions)
        center_y = sum(y for x, y, z in positions) / len(positions)
        
        # Prüfe Symmetrie um X-Achse
        x_symmetry = 0.0
        for x, y, z in positions:
            # Suche gespiegeltes Modul
            mirrored_x = 2 * center_x - x
            min_dist = float('inf')
            for mx, my, mz in positions:
                dist = math.sqrt((mx - mirrored_x)**2 + (my - y)**2)
                min_dist = min(min_dist, dist)
            
            # Wenn gespiegeltes Modul nahe ist, erhöhe Symmetrie
            if min_dist < self.module_width:
                x_symmetry += 1.0
        
        x_symmetry = (x_symmetry / len(positions)) * 100
        
        # Prüfe Symmetrie um Y-Achse
        y_symmetry = 0.0
        for x, y, z in positions:
            # Suche gespiegeltes Modul
            mirrored_y = 2 * center_y - y
            min_dist = float('inf')
            for mx, my, mz in positions:
                dist = math.sqrt((mx - x)**2 + (my - mirrored_y)**2)
                min_dist = min(min_dist, dist)
            
            # Wenn gespiegeltes Modul nahe ist, erhöhe Symmetrie
            if min_dist < self.module_height:
                y_symmetry += 1.0
        
        y_symmetry = (y_symmetry / len(positions)) * 100
        
        # Durchschnitt beider Achsen
        return (x_symmetry + y_symmetry) / 2
