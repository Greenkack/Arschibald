"""
3D Module Placement Algorithms Service

This module implements advanced algorithms for optimal placement of PV modules
on roof surfaces, including automatic optimal placement, constraint-based placement,
spacing calculations, orientation optimization, row/column layout algorithms,
and custom placement patterns.

Task 135: 3D Module Placement Algorithms
Requirements: 1.3, 6.1

Key Features:
    - Automatic optimal placement with maximum coverage
    - Constraint-based placement (obstacles, shading, boundaries)
    - Intelligent spacing calculations
    - Orientation optimization (portrait/landscape)
    - Row/column layout algorithms
    - Custom placement patterns (grid, staggered, custom)
"""

from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import math


class PlacementStrategy(Enum):
    """Placement strategy types"""
    OPTIMAL = "optimal"  # Maximum coverage with optimal spacing
    GRID = "grid"  # Regular grid pattern
    STAGGERED = "staggered"  # Staggered/brick pattern
    CUSTOM = "custom"  # Custom user-defined pattern
    CONSTRAINT_BASED = "constraint_based"  # Based on constraints


class ModuleOrientation(Enum):
    """Module orientation options"""
    PORTRAIT = "portrait"  # Vertical orientation (1.05m x 1.76m)
    LANDSCAPE = "landscape"  # Horizontal orientation (1.76m x 1.05m)
    AUTO = "auto"  # Automatically determine best orientation


@dataclass
class ModuleDimensions:
    """Standard PV module dimensions"""
    width: float = 1.05  # meters (portrait)
    height: float = 1.76  # meters (portrait)
    
    def get_dimensions(self, orientation: ModuleOrientation) -> Tuple[float, float]:
        """Get width and height based on orientation"""
        if orientation == ModuleOrientation.LANDSCAPE:
            return (self.height, self.width)
        return (self.width, self.height)


@dataclass
class PlacementConstraint:
    """Constraint for module placement"""
    x: float  # X-coordinate of constraint center
    y: float  # Y-coordinate of constraint center
    width: float  # Width of constraint area
    height: float  # Height of constraint area
    type: str = "obstacle"  # Type: obstacle, shading, exclusion


@dataclass
class RoofSurface:
    """Roof surface definition"""
    length: float  # X-axis length (meters)
    width: float  # Y-axis length (meters)
    type: str = "flat"  # flat, gable, shed, hip, etc.
    pitch: float = 0.0  # Roof pitch angle (degrees)
    azimuth: float = 180.0  # Roof azimuth (degrees, 180=south)


@dataclass
class PlacementConfig:
    """Configuration for module placement"""
    roof: RoofSurface
    module_quantity: int
    module_dims: ModuleDimensions = None
    orientation: ModuleOrientation = ModuleOrientation.AUTO
    strategy: PlacementStrategy = PlacementStrategy.OPTIMAL
    spacing: float = 0.05  # Spacing between modules (meters)
    margin: float = 0.30  # Margin from roof edges (meters)
    constraints: List[PlacementConstraint] = None
    
    def __post_init__(self):
        if self.module_dims is None:
            self.module_dims = ModuleDimensions()
        if self.constraints is None:
            self.constraints = []


@dataclass
class PlacementResult:
    """Result of placement algorithm"""
    positions: List[Tuple[float, float, float]]  # (x, y, z) positions
    orientations: List[ModuleOrientation]  # Orientation for each module
    count: int  # Number of modules placed
    coverage: float  # Percentage of roof covered
    efficiency: float  # Placement efficiency score (0-1)
    strategy_used: PlacementStrategy
    message: str = ""



class ModulePlacementAlgorithms:
    """
    Advanced algorithms for PV module placement on roof surfaces.
    
    This class implements various placement strategies including:
    - Automatic optimal placement
    - Constraint-based placement
    - Spacing calculations
    - Orientation optimization
    - Row/column layout algorithms
    - Custom placement patterns
    """
    
    def __init__(self):
        self.module_dims = ModuleDimensions()
    
    def calculate_optimal_placement(
        self,
        config: PlacementConfig
    ) -> PlacementResult:
        """
        Calculate optimal module placement with maximum coverage.
        
        This algorithm:
        1. Determines optimal orientation (portrait vs landscape)
        2. Calculates maximum number of rows and columns
        3. Places modules with optimal spacing
        4. Respects constraints and boundaries
        5. Maximizes roof coverage
        
        Args:
            config: Placement configuration
            
        Returns:
            PlacementResult with optimal positions
        """
        # Step 1: Determine optimal orientation
        orientation = self._determine_optimal_orientation(config)
        
        # Step 2: Calculate available space
        available_length = config.roof.length - (2 * config.margin)
        available_width = config.roof.width - (2 * config.margin)
        
        # Step 3: Get module dimensions for chosen orientation
        module_w, module_h = self.module_dims.get_dimensions(orientation)
        
        # Step 4: Calculate maximum rows and columns
        max_cols = int(available_length / (module_w + config.spacing))
        max_rows = int(available_width / (module_h + config.spacing))
        
        # Step 5: Calculate actual number of modules to place
        max_possible = max_cols * max_rows
        actual_count = min(config.module_quantity, max_possible)
        
        # Step 6: Generate grid positions
        positions = self._generate_grid_positions(
            config, orientation, max_cols, max_rows, actual_count
        )
        
        # Step 7: Filter positions based on constraints
        if config.constraints:
            positions = self._filter_constrained_positions(positions, config)
        
        # Step 8: Calculate coverage and efficiency
        coverage = self._calculate_coverage(positions, config.roof, module_w, module_h)
        efficiency = len(positions) / max(config.module_quantity, 1)
        
        return PlacementResult(
            positions=positions,
            orientations=[orientation] * len(positions),
            count=len(positions),
            coverage=coverage,
            efficiency=efficiency,
            strategy_used=PlacementStrategy.OPTIMAL,
            message=f"Placed {len(positions)} modules with {coverage:.1f}% coverage"
        )

    
    def calculate_constraint_based_placement(
        self,
        config: PlacementConfig
    ) -> PlacementResult:
        """
        Calculate placement based on constraints (obstacles, shading, exclusions).
        
        This algorithm:
        1. Identifies all constraint areas
        2. Calculates available placement zones
        3. Places modules avoiding constraints
        4. Optimizes placement within available zones
        
        Args:
            config: Placement configuration with constraints
            
        Returns:
            PlacementResult with constraint-aware positions
        """
        # Start with optimal placement
        result = self.calculate_optimal_placement(config)
        
        # Filter out positions that violate constraints
        valid_positions = []
        valid_orientations = []
        
        for pos, orient in zip(result.positions, result.orientations):
            if not self._violates_constraints(pos, orient, config):
                valid_positions.append(pos)
                valid_orientations.append(orient)
        
        # Recalculate metrics
        module_w, module_h = self.module_dims.get_dimensions(valid_orientations[0] if valid_orientations else ModuleOrientation.PORTRAIT)
        coverage = self._calculate_coverage(valid_positions, config.roof, module_w, module_h)
        efficiency = len(valid_positions) / max(config.module_quantity, 1)
        
        return PlacementResult(
            positions=valid_positions,
            orientations=valid_orientations,
            count=len(valid_positions),
            coverage=coverage,
            efficiency=efficiency,
            strategy_used=PlacementStrategy.CONSTRAINT_BASED,
            message=f"Placed {len(valid_positions)} modules avoiding {len(config.constraints)} constraints"
        )
    
    def calculate_spacing(
        self,
        module_count: int,
        roof_length: float,
        roof_width: float,
        orientation: ModuleOrientation,
        margin: float = 0.30
    ) -> Tuple[float, float]:
        """
        Calculate optimal spacing between modules.
        
        Args:
            module_count: Number of modules to place
            roof_length: Roof length (X-axis)
            roof_width: Roof width (Y-axis)
            orientation: Module orientation
            margin: Margin from edges
            
        Returns:
            Tuple of (spacing_x, spacing_y) in meters
        """
        module_w, module_h = self.module_dims.get_dimensions(orientation)
        
        # Calculate available space
        available_length = roof_length - (2 * margin)
        available_width = roof_width - (2 * margin)
        
        # Estimate rows and columns
        aspect_ratio = available_length / available_width
        cols = int(math.sqrt(module_count * aspect_ratio))
        rows = int(module_count / cols) + (1 if module_count % cols else 0)
        
        # Calculate spacing
        spacing_x = (available_length - (cols * module_w)) / max(cols - 1, 1)
        spacing_y = (available_width - (rows * module_h)) / max(rows - 1, 1)
        
        # Ensure minimum spacing
        spacing_x = max(0.05, spacing_x)
        spacing_y = max(0.05, spacing_y)
        
        return (spacing_x, spacing_y)

    
    def optimize_orientation(
        self,
        roof: RoofSurface,
        module_quantity: int,
        margin: float = 0.30
    ) -> ModuleOrientation:
        """
        Determine optimal module orientation (portrait vs landscape).
        
        This algorithm considers:
        - Roof dimensions and aspect ratio
        - Number of modules to place
        - Maximum coverage potential
        
        Args:
            roof: Roof surface definition
            module_quantity: Number of modules
            margin: Margin from edges
            
        Returns:
            Optimal ModuleOrientation
        """
        available_length = roof.length - (2 * margin)
        available_width = roof.width - (2 * margin)
        
        # Try portrait orientation
        portrait_w, portrait_h = self.module_dims.get_dimensions(ModuleOrientation.PORTRAIT)
        portrait_cols = int(available_length / portrait_w)
        portrait_rows = int(available_width / portrait_h)
        portrait_capacity = portrait_cols * portrait_rows
        
        # Try landscape orientation
        landscape_w, landscape_h = self.module_dims.get_dimensions(ModuleOrientation.LANDSCAPE)
        landscape_cols = int(available_length / landscape_w)
        landscape_rows = int(available_width / landscape_h)
        landscape_capacity = landscape_cols * landscape_rows
        
        # Choose orientation that can fit more modules
        if landscape_capacity > portrait_capacity:
            return ModuleOrientation.LANDSCAPE
        elif portrait_capacity > landscape_capacity:
            return ModuleOrientation.PORTRAIT
        else:
            # If equal, prefer portrait (standard orientation)
            return ModuleOrientation.PORTRAIT
    
    def generate_row_column_layout(
        self,
        config: PlacementConfig,
        rows: int,
        cols: int
    ) -> PlacementResult:
        """
        Generate module layout with specified rows and columns.
        
        Args:
            config: Placement configuration
            rows: Number of rows
            cols: Number of columns
            
        Returns:
            PlacementResult with row/column layout
        """
        orientation = config.orientation
        if orientation == ModuleOrientation.AUTO:
            orientation = self._determine_optimal_orientation(config)
        
        module_w, module_h = self.module_dims.get_dimensions(orientation)
        
        # Calculate spacing
        available_length = config.roof.length - (2 * config.margin)
        available_width = config.roof.width - (2 * config.margin)
        
        spacing_x = (available_length - (cols * module_w)) / max(cols - 1, 1)
        spacing_y = (available_width - (rows * module_h)) / max(rows - 1, 1)
        
        # Generate positions
        positions = []
        start_x = -(config.roof.length / 2) + config.margin + (module_w / 2)
        start_y = -(config.roof.width / 2) + config.margin + (module_h / 2)
        
        for row in range(rows):
            for col in range(cols):
                if len(positions) >= config.module_quantity:
                    break
                
                x = start_x + col * (module_w + spacing_x)
                y = start_y + row * (module_h + spacing_y)
                z = self._calculate_z_position(config.roof, y)
                
                positions.append((x, y, z))
            
            if len(positions) >= config.module_quantity:
                break
        
        coverage = self._calculate_coverage(positions, config.roof, module_w, module_h)
        efficiency = len(positions) / max(config.module_quantity, 1)
        
        return PlacementResult(
            positions=positions,
            orientations=[orientation] * len(positions),
            count=len(positions),
            coverage=coverage,
            efficiency=efficiency,
            strategy_used=PlacementStrategy.GRID,
            message=f"Generated {rows}x{cols} grid with {len(positions)} modules"
        )

    
    def generate_staggered_pattern(
        self,
        config: PlacementConfig
    ) -> PlacementResult:
        """
        Generate staggered/brick pattern placement.
        
        This pattern offsets alternating rows for better coverage
        and aesthetic appearance.
        
        Args:
            config: Placement configuration
            
        Returns:
            PlacementResult with staggered pattern
        """
        orientation = config.orientation
        if orientation == ModuleOrientation.AUTO:
            orientation = self._determine_optimal_orientation(config)
        
        module_w, module_h = self.module_dims.get_dimensions(orientation)
        
        # Calculate rows and columns
        available_length = config.roof.length - (2 * config.margin)
        available_width = config.roof.width - (2 * config.margin)
        
        cols = int(available_length / (module_w + config.spacing))
        rows = int(available_width / (module_h + config.spacing))
        
        # Generate staggered positions
        positions = []
        start_x = -(config.roof.length / 2) + config.margin + (module_w / 2)
        start_y = -(config.roof.width / 2) + config.margin + (module_h / 2)
        
        for row in range(rows):
            # Offset every other row by half module width
            offset = (module_w / 2) if row % 2 == 1 else 0
            
            for col in range(cols):
                if len(positions) >= config.module_quantity:
                    break
                
                x = start_x + col * (module_w + config.spacing) + offset
                y = start_y + row * (module_h + config.spacing)
                
                # Check if position is within bounds
                if abs(x) <= (config.roof.length / 2) - config.margin:
                    z = self._calculate_z_position(config.roof, y)
                    positions.append((x, y, z))
            
            if len(positions) >= config.module_quantity:
                break
        
        coverage = self._calculate_coverage(positions, config.roof, module_w, module_h)
        efficiency = len(positions) / max(config.module_quantity, 1)
        
        return PlacementResult(
            positions=positions,
            orientations=[orientation] * len(positions),
            count=len(positions),
            coverage=coverage,
            efficiency=efficiency,
            strategy_used=PlacementStrategy.STAGGERED,
            message=f"Generated staggered pattern with {len(positions)} modules"
        )
    
    def generate_custom_pattern(
        self,
        config: PlacementConfig,
        pattern_func: callable
    ) -> PlacementResult:
        """
        Generate custom placement pattern using user-defined function.
        
        Args:
            config: Placement configuration
            pattern_func: Function that generates positions
                         Signature: (config) -> List[Tuple[float, float, float]]
            
        Returns:
            PlacementResult with custom pattern
        """
        try:
            positions = pattern_func(config)
            
            orientation = config.orientation
            if orientation == ModuleOrientation.AUTO:
                orientation = self._determine_optimal_orientation(config)
            
            module_w, module_h = self.module_dims.get_dimensions(orientation)
            
            # Filter positions based on constraints
            if config.constraints:
                positions = self._filter_constrained_positions(positions, config)
            
            coverage = self._calculate_coverage(positions, config.roof, module_w, module_h)
            efficiency = len(positions) / max(config.module_quantity, 1)
            
            return PlacementResult(
                positions=positions,
                orientations=[orientation] * len(positions),
                count=len(positions),
                coverage=coverage,
                efficiency=efficiency,
                strategy_used=PlacementStrategy.CUSTOM,
                message=f"Generated custom pattern with {len(positions)} modules"
            )
        except Exception as e:
            return PlacementResult(
                positions=[],
                orientations=[],
                count=0,
                coverage=0.0,
                efficiency=0.0,
                strategy_used=PlacementStrategy.CUSTOM,
                message=f"Error generating custom pattern: {str(e)}"
            )

    
    # Private helper methods
    
    def _determine_optimal_orientation(self, config: PlacementConfig) -> ModuleOrientation:
        """Determine optimal orientation based on configuration"""
        if config.orientation != ModuleOrientation.AUTO:
            return config.orientation
        return self.optimize_orientation(config.roof, config.module_quantity, config.margin)
    
    def _generate_grid_positions(
        self,
        config: PlacementConfig,
        orientation: ModuleOrientation,
        max_cols: int,
        max_rows: int,
        count: int
    ) -> List[Tuple[float, float, float]]:
        """Generate grid positions for modules"""
        module_w, module_h = self.module_dims.get_dimensions(orientation)
        
        positions = []
        start_x = -(config.roof.length / 2) + config.margin + (module_w / 2)
        start_y = -(config.roof.width / 2) + config.margin + (module_h / 2)
        
        for row in range(max_rows):
            for col in range(max_cols):
                if len(positions) >= count:
                    break
                
                x = start_x + col * (module_w + config.spacing)
                y = start_y + row * (module_h + config.spacing)
                z = self._calculate_z_position(config.roof, y)
                
                positions.append((x, y, z))
            
            if len(positions) >= count:
                break
        
        return positions
    
    def _calculate_z_position(self, roof: RoofSurface, y: float) -> float:
        """Calculate Z-position based on roof type and Y-position"""
        if roof.type.lower() == "flat":
            # Flat roof: constant height with mounting frame
            return 0.30  # 30cm elevation for mounting frame
        else:
            # Pitched roof: calculate based on position and pitch
            base_z = 0.15  # 15cm clearance above roof base
            
            if roof.pitch > 0:
                # Calculate height based on Y-position on sloped roof
                inclination_rad = math.radians(roof.pitch)
                dist_from_eave = y + roof.width / 2
                z_offset = dist_from_eave * math.tan(inclination_rad)
                return base_z + z_offset
            
            return base_z
    
    def _filter_constrained_positions(
        self,
        positions: List[Tuple[float, float, float]],
        config: PlacementConfig
    ) -> List[Tuple[float, float, float]]:
        """Filter out positions that violate constraints"""
        valid_positions = []
        
        for pos in positions:
            if not self._violates_constraints(pos, config.orientation, config):
                valid_positions.append(pos)
        
        return valid_positions
    
    def _violates_constraints(
        self,
        position: Tuple[float, float, float],
        orientation: ModuleOrientation,
        config: PlacementConfig
    ) -> bool:
        """Check if position violates any constraints"""
        x, y, z = position
        module_w, module_h = self.module_dims.get_dimensions(orientation)
        
        # Check each constraint
        for constraint in config.constraints:
            # Calculate module bounding box
            module_left = x - module_w / 2
            module_right = x + module_w / 2
            module_bottom = y - module_h / 2
            module_top = y + module_h / 2
            
            # Calculate constraint bounding box
            constraint_left = constraint.x - constraint.width / 2
            constraint_right = constraint.x + constraint.width / 2
            constraint_bottom = constraint.y - constraint.height / 2
            constraint_top = constraint.y + constraint.height / 2
            
            # Check for overlap
            if (module_right > constraint_left and
                module_left < constraint_right and
                module_top > constraint_bottom and
                module_bottom < constraint_top):
                return True
        
        return False
    
    def _calculate_coverage(
        self,
        positions: List[Tuple[float, float, float]],
        roof: RoofSurface,
        module_w: float,
        module_h: float
    ) -> float:
        """Calculate percentage of roof covered by modules"""
        if not positions:
            return 0.0
        
        module_area = module_w * module_h
        total_module_area = len(positions) * module_area
        roof_area = roof.length * roof.width
        
        coverage = (total_module_area / roof_area) * 100
        return min(coverage, 100.0)  # Cap at 100%


# Example usage
if __name__ == "__main__":
    print("=== Module Placement Algorithms Test ===\n")
    
    # Create test configuration
    roof = RoofSurface(length=10.0, width=8.0, type="flat", pitch=0.0)
    config = PlacementConfig(
        roof=roof,
        module_quantity=30,
        orientation=ModuleOrientation.AUTO,
        strategy=PlacementStrategy.OPTIMAL,
        spacing=0.05,
        margin=0.30
    )
    
    # Initialize algorithms
    algorithms = ModulePlacementAlgorithms()
    
    # Test 1: Optimal placement
    print("Test 1: Optimal Placement")
    result = algorithms.calculate_optimal_placement(config)
    print(f"  Placed: {result.count} modules")
    print(f"  Coverage: {result.coverage:.1f}%")
    print(f"  Efficiency: {result.efficiency:.2f}")
    print(f"  Message: {result.message}\n")
    
    # Test 2: Orientation optimization
    print("Test 2: Orientation Optimization")
    optimal_orient = algorithms.optimize_orientation(roof, 30, 0.30)
    print(f"  Optimal orientation: {optimal_orient.value}\n")
    
    # Test 3: Spacing calculation
    print("Test 3: Spacing Calculation")
    spacing_x, spacing_y = algorithms.calculate_spacing(30, 10.0, 8.0, ModuleOrientation.PORTRAIT)
    print(f"  Spacing X: {spacing_x:.3f}m")
    print(f"  Spacing Y: {spacing_y:.3f}m\n")
    
    # Test 4: Row/column layout
    print("Test 4: Row/Column Layout")
    result = algorithms.generate_row_column_layout(config, rows=5, cols=6)
    print(f"  Placed: {result.count} modules")
    print(f"  Coverage: {result.coverage:.1f}%")
    print(f"  Message: {result.message}\n")
    
    # Test 5: Staggered pattern
    print("Test 5: Staggered Pattern")
    result = algorithms.generate_staggered_pattern(config)
    print(f"  Placed: {result.count} modules")
    print(f"  Coverage: {result.coverage:.1f}%")
    print(f"  Message: {result.message}\n")
    
    print("=== All tests completed ===")
