"""
3D Mounting System Visualization Service

This service provides comprehensive mounting system visualization including:
- Mounting rail visualization
- Mounting clamp placement
- Roof penetration visualization
- Cable routing visualization
- BOM (Bill of Materials) generation
- Mounting system cost calculation

Requirements: 1.3, 6.1
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import logging

logger = logging.getLogger(__name__)


class MountingType(Enum):
    """Types of mounting systems"""
    FLAT_ROOF = "flat_roof"
    PITCHED_ROOF = "pitched_roof"
    GROUND_MOUNT = "ground_mount"
    FACADE = "facade"


class RailOrientation(Enum):
    """Rail orientation options"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class ClampType(Enum):
    """Types of mounting clamps"""
    END_CLAMP = "end_clamp"
    MID_CLAMP = "mid_clamp"
    CORNER_CLAMP = "corner_clamp"


class PenetrationType(Enum):
    """Types of roof penetrations"""
    HOOK = "hook"
    ANCHOR = "anchor"
    BALLAST = "ballast"
    NONE = "none"


@dataclass
class MountingRail:
    """Represents a mounting rail"""
    id: str
    start_point: Tuple[float, float, float]  # (x, y, z)
    end_point: Tuple[float, float, float]
    length: float
    orientation: RailOrientation
    material: str = "aluminum"
    profile: str = "standard"
    
    def get_midpoint(self) -> Tuple[float, float, float]:
        """Calculate midpoint of rail"""
        return (
            (self.start_point[0] + self.end_point[0]) / 2,
            (self.start_point[1] + self.end_point[1]) / 2,
            (self.start_point[2] + self.end_point[2]) / 2
        )


@dataclass
class MountingClamp:
    """Represents a mounting clamp"""
    id: str
    position: Tuple[float, float, float]
    clamp_type: ClampType
    rail_id: str
    module_id: Optional[str] = None
    torque_spec: float = 15.0  # Nm


@dataclass
class RoofPenetration:
    """Represents a roof penetration point"""
    id: str
    position: Tuple[float, float, float]
    penetration_type: PenetrationType
    rail_id: str
    waterproofing: bool = True
    load_capacity: float = 500.0  # kg


@dataclass
class CableRoute:
    """Represents a cable routing path"""
    id: str
    waypoints: List[Tuple[float, float, float]]
    cable_type: str
    diameter: float  # mm
    length: float  # meters
    
    def calculate_length(self) -> float:
        """Calculate total cable length"""
        total = 0.0
        for i in range(len(self.waypoints) - 1):
            p1 = self.waypoints[i]
            p2 = self.waypoints[i + 1]
            distance = math.sqrt(
                (p2[0] - p1[0])**2 + 
                (p2[1] - p1[1])**2 + 
                (p2[2] - p1[2])**2
            )
            total += distance
        return total


@dataclass
class BOMItem:
    """Bill of Materials item"""
    item_id: str
    description: str
    quantity: int
    unit: str
    unit_price: float
    total_price: float
    category: str
    manufacturer: Optional[str] = None
    part_number: Optional[str] = None


@dataclass
class MountingSystemVisualization:
    """Complete mounting system visualization data"""
    rails: List[MountingRail] = field(default_factory=list)
    clamps: List[MountingClamp] = field(default_factory=list)
    penetrations: List[RoofPenetration] = field(default_factory=list)
    cable_routes: List[CableRoute] = field(default_factory=list)
    bom: List[BOMItem] = field(default_factory=list)
    total_cost: float = 0.0
    mounting_type: MountingType = MountingType.PITCHED_ROOF


class MountingSystemService:
    """Service for 3D mounting system visualization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Standard component prices (EUR)
        self.component_prices = {
            "rail_per_meter": 12.50,
            "end_clamp": 3.50,
            "mid_clamp": 2.80,
            "corner_clamp": 4.20,
            "hook_penetration": 8.50,
            "anchor_penetration": 12.00,
            "ballast_block": 15.00,
            "cable_per_meter_dc": 2.50,
            "cable_per_meter_ac": 3.20,
            "cable_tray_per_meter": 8.00,
            "junction_box": 25.00,
            "connector_mc4": 1.50,
        }
    
    def generate_mounting_rails(
        self,
        module_positions: List[Dict[str, Any]],
        mounting_type: MountingType,
        rail_orientation: RailOrientation
    ) -> List[MountingRail]:
        """
        Generate mounting rails based on module positions
        
        Args:
            module_positions: List of module position dictionaries
            mounting_type: Type of mounting system
            rail_orientation: Orientation of rails
            
        Returns:
            List of MountingRail objects
        """
        self.logger.info(f"Generating mounting rails for {len(module_positions)} modules")
        
        rails = []
        
        if rail_orientation == RailOrientation.HORIZONTAL:
            # Group modules by rows
            rows = self._group_modules_by_rows(module_positions)
            
            for row_idx, row_modules in enumerate(rows):
                # Create rails for this row
                row_rails = self._create_rails_for_row(
                    row_modules, 
                    row_idx, 
                    mounting_type
                )
                rails.extend(row_rails)
        else:
            # Group modules by columns
            columns = self._group_modules_by_columns(module_positions)
            
            for col_idx, col_modules in enumerate(columns):
                # Create rails for this column
                col_rails = self._create_rails_for_column(
                    col_modules, 
                    col_idx, 
                    mounting_type
                )
                rails.extend(col_rails)
        
        self.logger.info(f"Generated {len(rails)} mounting rails")
        return rails
    
    def generate_mounting_clamps(
        self,
        rails: List[MountingRail],
        module_positions: List[Dict[str, Any]]
    ) -> List[MountingClamp]:
        """
        Generate mounting clamps for rails and modules
        
        Args:
            rails: List of mounting rails
            module_positions: List of module positions
            
        Returns:
            List of MountingClamp objects
        """
        self.logger.info("Generating mounting clamps")
        
        clamps = []
        clamp_id = 0
        
        for rail in rails:
            # Find modules attached to this rail
            attached_modules = self._find_modules_on_rail(rail, module_positions)
            
            if not attached_modules:
                continue
            
            # Sort modules along rail
            sorted_modules = self._sort_modules_along_rail(attached_modules, rail)
            
            # Generate clamps for each module
            for idx, module in enumerate(sorted_modules):
                module_id = module.get('id', f"module_{idx}")
                
                # Determine clamp positions on module edges
                clamp_positions = self._calculate_clamp_positions(module, rail)
                
                for pos_idx, position in enumerate(clamp_positions):
                    # Determine clamp type
                    if idx == 0 and pos_idx == 0:
                        clamp_type = ClampType.END_CLAMP
                    elif idx == len(sorted_modules) - 1 and pos_idx == len(clamp_positions) - 1:
                        clamp_type = ClampType.END_CLAMP
                    else:
                        clamp_type = ClampType.MID_CLAMP
                    
                    clamp = MountingClamp(
                        id=f"clamp_{clamp_id}",
                        position=position,
                        clamp_type=clamp_type,
                        rail_id=rail.id,
                        module_id=module_id
                    )
                    clamps.append(clamp)
                    clamp_id += 1
        
        self.logger.info(f"Generated {len(clamps)} mounting clamps")
        return clamps
    
    def generate_roof_penetrations(
        self,
        rails: List[MountingRail],
        mounting_type: MountingType,
        roof_angle: float
    ) -> List[RoofPenetration]:
        """
        Generate roof penetration points
        
        Args:
            rails: List of mounting rails
            mounting_type: Type of mounting system
            roof_angle: Roof angle in degrees
            
        Returns:
            List of RoofPenetration objects
        """
        self.logger.info("Generating roof penetrations")
        
        penetrations = []
        penetration_id = 0
        
        # Determine penetration type based on mounting type
        if mounting_type == MountingType.FLAT_ROOF:
            penetration_type = PenetrationType.BALLAST
        elif mounting_type == MountingType.GROUND_MOUNT:
            penetration_type = PenetrationType.ANCHOR
        else:
            penetration_type = PenetrationType.HOOK
        
        # Calculate penetration spacing (typically every 1-1.5 meters)
        penetration_spacing = 1.2  # meters
        
        for rail in rails:
            rail_length = rail.length
            num_penetrations = max(2, int(rail_length / penetration_spacing) + 1)
            
            # Distribute penetrations evenly along rail
            for i in range(num_penetrations):
                t = i / (num_penetrations - 1) if num_penetrations > 1 else 0.5
                
                position = (
                    rail.start_point[0] + t * (rail.end_point[0] - rail.start_point[0]),
                    rail.start_point[1] + t * (rail.end_point[1] - rail.start_point[1]),
                    rail.start_point[2] + t * (rail.end_point[2] - rail.start_point[2])
                )
                
                penetration = RoofPenetration(
                    id=f"penetration_{penetration_id}",
                    position=position,
                    penetration_type=penetration_type,
                    rail_id=rail.id,
                    waterproofing=(penetration_type != PenetrationType.BALLAST)
                )
                penetrations.append(penetration)
                penetration_id += 1
        
        self.logger.info(f"Generated {len(penetrations)} roof penetrations")
        return penetrations
    
    def generate_cable_routing(
        self,
        module_positions: List[Dict[str, Any]],
        inverter_position: Tuple[float, float, float],
        mounting_type: MountingType
    ) -> List[CableRoute]:
        """
        Generate cable routing paths
        
        Args:
            module_positions: List of module positions
            inverter_position: Position of inverter
            mounting_type: Type of mounting system
            
        Returns:
            List of CableRoute objects
        """
        self.logger.info("Generating cable routing")
        
        cable_routes = []
        route_id = 0
        
        # Group modules into strings (series connections)
        strings = self._group_modules_into_strings(module_positions)
        
        for string_idx, string_modules in enumerate(strings):
            # DC cable route from modules to string combiner
            waypoints = []
            
            # Start from first module
            first_module = string_modules[0]
            waypoints.append((
                first_module['position']['x'],
                first_module['position']['y'],
                first_module['position']['z']
            ))
            
            # Route through each module in string
            for module in string_modules[1:]:
                waypoints.append((
                    module['position']['x'],
                    module['position']['y'],
                    module['position']['z']
                ))
            
            # Route to inverter
            waypoints.append(inverter_position)
            
            dc_route = CableRoute(
                id=f"dc_route_{route_id}",
                waypoints=waypoints,
                cable_type="DC",
                diameter=6.0,  # mm
                length=0.0  # Will be calculated
            )
            dc_route.length = dc_route.calculate_length()
            cable_routes.append(dc_route)
            route_id += 1
        
        # AC cable route from inverter to grid connection
        # Simplified: straight line from inverter to edge of roof
        ac_route = CableRoute(
            id=f"ac_route_{route_id}",
            waypoints=[
                inverter_position,
                (inverter_position[0] + 10, inverter_position[1], inverter_position[2])
            ],
            cable_type="AC",
            diameter=10.0,  # mm
            length=0.0
        )
        ac_route.length = ac_route.calculate_length()
        cable_routes.append(ac_route)
        
        self.logger.info(f"Generated {len(cable_routes)} cable routes")
        return cable_routes
    
    def generate_bom(
        self,
        visualization: MountingSystemVisualization
    ) -> List[BOMItem]:
        """
        Generate Bill of Materials from visualization
        
        Args:
            visualization: Complete mounting system visualization
            
        Returns:
            List of BOMItem objects
        """
        self.logger.info("Generating Bill of Materials")
        
        bom = []
        
        # Rails
        total_rail_length = sum(rail.length for rail in visualization.rails)
        if total_rail_length > 0:
            unit_price = self.component_prices["rail_per_meter"]
            bom.append(BOMItem(
                item_id="BOM_001",
                description="Mounting Rails (Aluminum)",
                quantity=int(math.ceil(total_rail_length)),
                unit="meter",
                unit_price=unit_price,
                total_price=total_rail_length * unit_price,
                category="Mounting Structure"
            ))
        
        # Clamps
        clamp_counts = {
            ClampType.END_CLAMP: 0,
            ClampType.MID_CLAMP: 0,
            ClampType.CORNER_CLAMP: 0
        }
        for clamp in visualization.clamps:
            clamp_counts[clamp.clamp_type] += 1
        
        for clamp_type, count in clamp_counts.items():
            if count > 0:
                price_key = f"{clamp_type.value}"
                unit_price = self.component_prices.get(price_key, 3.0)
                bom.append(BOMItem(
                    item_id=f"BOM_{len(bom) + 1:03d}",
                    description=f"Mounting Clamps ({clamp_type.value.replace('_', ' ').title()})",
                    quantity=count,
                    unit="piece",
                    unit_price=unit_price,
                    total_price=count * unit_price,
                    category="Mounting Hardware"
                ))
        
        # Penetrations
        penetration_counts = {}
        for penetration in visualization.penetrations:
            pen_type = penetration.penetration_type
            penetration_counts[pen_type] = penetration_counts.get(pen_type, 0) + 1
        
        for pen_type, count in penetration_counts.items():
            if count > 0:
                price_key = f"{pen_type.value}_penetration"
                unit_price = self.component_prices.get(price_key, 10.0)
                bom.append(BOMItem(
                    item_id=f"BOM_{len(bom) + 1:03d}",
                    description=f"Roof Penetrations ({pen_type.value.replace('_', ' ').title()})",
                    quantity=count,
                    unit="piece",
                    unit_price=unit_price,
                    total_price=count * unit_price,
                    category="Roof Attachment"
                ))
        
        # Cables
        dc_cable_length = sum(
            route.length for route in visualization.cable_routes 
            if route.cable_type == "DC"
        )
        ac_cable_length = sum(
            route.length for route in visualization.cable_routes 
            if route.cable_type == "AC"
        )
        
        if dc_cable_length > 0:
            unit_price = self.component_prices["cable_per_meter_dc"]
            bom.append(BOMItem(
                item_id=f"BOM_{len(bom) + 1:03d}",
                description="DC Cable (6mm²)",
                quantity=int(math.ceil(dc_cable_length)),
                unit="meter",
                unit_price=unit_price,
                total_price=dc_cable_length * unit_price,
                category="Electrical"
            ))
        
        if ac_cable_length > 0:
            unit_price = self.component_prices["cable_per_meter_ac"]
            bom.append(BOMItem(
                item_id=f"BOM_{len(bom) + 1:03d}",
                description="AC Cable (10mm²)",
                quantity=int(math.ceil(ac_cable_length)),
                unit="meter",
                unit_price=unit_price,
                total_price=ac_cable_length * unit_price,
                category="Electrical"
            ))
        
        self.logger.info(f"Generated BOM with {len(bom)} items")
        return bom
    
    def calculate_total_cost(self, bom: List[BOMItem]) -> float:
        """
        Calculate total mounting system cost
        
        Args:
            bom: Bill of Materials
            
        Returns:
            Total cost in EUR
        """
        total = sum(item.total_price for item in bom)
        self.logger.info(f"Total mounting system cost: €{total:,.2f}")
        return total
    
    def create_complete_visualization(
        self,
        module_positions: List[Dict[str, Any]],
        mounting_type: MountingType,
        rail_orientation: RailOrientation,
        roof_angle: float,
        inverter_position: Tuple[float, float, float]
    ) -> MountingSystemVisualization:
        """
        Create complete mounting system visualization
        
        Args:
            module_positions: List of module positions
            mounting_type: Type of mounting system
            rail_orientation: Orientation of rails
            roof_angle: Roof angle in degrees
            inverter_position: Position of inverter
            
        Returns:
            Complete MountingSystemVisualization object
        """
        self.logger.info("Creating complete mounting system visualization")
        
        # Generate all components
        rails = self.generate_mounting_rails(
            module_positions, 
            mounting_type, 
            rail_orientation
        )
        
        clamps = self.generate_mounting_clamps(rails, module_positions)
        
        penetrations = self.generate_roof_penetrations(
            rails, 
            mounting_type, 
            roof_angle
        )
        
        cable_routes = self.generate_cable_routing(
            module_positions, 
            inverter_position, 
            mounting_type
        )
        
        # Create visualization object
        visualization = MountingSystemVisualization(
            rails=rails,
            clamps=clamps,
            penetrations=penetrations,
            cable_routes=cable_routes,
            mounting_type=mounting_type
        )
        
        # Generate BOM
        visualization.bom = self.generate_bom(visualization)
        visualization.total_cost = self.calculate_total_cost(visualization.bom)
        
        self.logger.info("Complete mounting system visualization created")
        return visualization
    
    # Helper methods
    
    def _group_modules_by_rows(
        self, 
        module_positions: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group modules into rows based on Y coordinate"""
        if not module_positions:
            return []
        
        # Sort by Y coordinate
        sorted_modules = sorted(
            module_positions, 
            key=lambda m: m['position']['y']
        )
        
        rows = []
        current_row = [sorted_modules[0]]
        row_tolerance = 0.5  # meters
        
        for module in sorted_modules[1:]:
            if abs(module['position']['y'] - current_row[0]['position']['y']) < row_tolerance:
                current_row.append(module)
            else:
                rows.append(current_row)
                current_row = [module]
        
        if current_row:
            rows.append(current_row)
        
        return rows
    
    def _group_modules_by_columns(
        self, 
        module_positions: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group modules into columns based on X coordinate"""
        if not module_positions:
            return []
        
        # Sort by X coordinate
        sorted_modules = sorted(
            module_positions, 
            key=lambda m: m['position']['x']
        )
        
        columns = []
        current_column = [sorted_modules[0]]
        column_tolerance = 0.5  # meters
        
        for module in sorted_modules[1:]:
            if abs(module['position']['x'] - current_column[0]['position']['x']) < column_tolerance:
                current_column.append(module)
            else:
                columns.append(current_column)
                current_column = [module]
        
        if current_column:
            columns.append(current_column)
        
        return columns
    
    def _create_rails_for_row(
        self,
        row_modules: List[Dict[str, Any]],
        row_idx: int,
        mounting_type: MountingType
    ) -> List[MountingRail]:
        """Create mounting rails for a row of modules"""
        if not row_modules:
            return []
        
        # Sort modules by X coordinate
        sorted_modules = sorted(row_modules, key=lambda m: m['position']['x'])
        
        # Typically 2 rails per row (top and bottom of modules)
        rails = []
        
        # Calculate rail positions
        first_module = sorted_modules[0]
        last_module = sorted_modules[-1]
        
        # Top rail
        top_rail = MountingRail(
            id=f"rail_row{row_idx}_top",
            start_point=(
                first_module['position']['x'] - 0.1,
                first_module['position']['y'] + 0.3,
                first_module['position']['z']
            ),
            end_point=(
                last_module['position']['x'] + 0.1,
                last_module['position']['y'] + 0.3,
                last_module['position']['z']
            ),
            length=0.0,
            orientation=RailOrientation.HORIZONTAL
        )
        top_rail.length = math.sqrt(
            (top_rail.end_point[0] - top_rail.start_point[0])**2 +
            (top_rail.end_point[1] - top_rail.start_point[1])**2
        )
        rails.append(top_rail)
        
        # Bottom rail
        bottom_rail = MountingRail(
            id=f"rail_row{row_idx}_bottom",
            start_point=(
                first_module['position']['x'] - 0.1,
                first_module['position']['y'] - 0.3,
                first_module['position']['z']
            ),
            end_point=(
                last_module['position']['x'] + 0.1,
                last_module['position']['y'] - 0.3,
                last_module['position']['z']
            ),
            length=0.0,
            orientation=RailOrientation.HORIZONTAL
        )
        bottom_rail.length = math.sqrt(
            (bottom_rail.end_point[0] - bottom_rail.start_point[0])**2 +
            (bottom_rail.end_point[1] - bottom_rail.start_point[1])**2
        )
        rails.append(bottom_rail)
        
        return rails
    
    def _create_rails_for_column(
        self,
        col_modules: List[Dict[str, Any]],
        col_idx: int,
        mounting_type: MountingType
    ) -> List[MountingRail]:
        """Create mounting rails for a column of modules"""
        if not col_modules:
            return []
        
        # Sort modules by Y coordinate
        sorted_modules = sorted(col_modules, key=lambda m: m['position']['y'])
        
        rails = []
        
        # Calculate rail positions
        first_module = sorted_modules[0]
        last_module = sorted_modules[-1]
        
        # Left rail
        left_rail = MountingRail(
            id=f"rail_col{col_idx}_left",
            start_point=(
                first_module['position']['x'] - 0.3,
                first_module['position']['y'] - 0.1,
                first_module['position']['z']
            ),
            end_point=(
                last_module['position']['x'] - 0.3,
                last_module['position']['y'] + 0.1,
                last_module['position']['z']
            ),
            length=0.0,
            orientation=RailOrientation.VERTICAL
        )
        left_rail.length = math.sqrt(
            (left_rail.end_point[1] - left_rail.start_point[1])**2 +
            (left_rail.end_point[2] - left_rail.start_point[2])**2
        )
        rails.append(left_rail)
        
        # Right rail
        right_rail = MountingRail(
            id=f"rail_col{col_idx}_right",
            start_point=(
                first_module['position']['x'] + 0.3,
                first_module['position']['y'] - 0.1,
                first_module['position']['z']
            ),
            end_point=(
                last_module['position']['x'] + 0.3,
                last_module['position']['y'] + 0.1,
                last_module['position']['z']
            ),
            length=0.0,
            orientation=RailOrientation.VERTICAL
        )
        right_rail.length = math.sqrt(
            (right_rail.end_point[1] - right_rail.start_point[1])**2 +
            (right_rail.end_point[2] - right_rail.start_point[2])**2
        )
        rails.append(right_rail)
        
        return rails
    
    def _find_modules_on_rail(
        self,
        rail: MountingRail,
        module_positions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find modules that are attached to a specific rail"""
        attached = []
        tolerance = 0.5  # meters
        
        for module in module_positions:
            pos = module['position']
            
            # Check if module is near rail
            if rail.orientation == RailOrientation.HORIZONTAL:
                # Check Y coordinate proximity
                rail_y = rail.start_point[1]
                if abs(pos['y'] - rail_y) < tolerance:
                    # Check if within rail X range
                    if (rail.start_point[0] <= pos['x'] <= rail.end_point[0] or
                        rail.end_point[0] <= pos['x'] <= rail.start_point[0]):
                        attached.append(module)
            else:
                # Check X coordinate proximity
                rail_x = rail.start_point[0]
                if abs(pos['x'] - rail_x) < tolerance:
                    # Check if within rail Y range
                    if (rail.start_point[1] <= pos['y'] <= rail.end_point[1] or
                        rail.end_point[1] <= pos['y'] <= rail.start_point[1]):
                        attached.append(module)
        
        return attached
    
    def _sort_modules_along_rail(
        self,
        modules: List[Dict[str, Any]],
        rail: MountingRail
    ) -> List[Dict[str, Any]]:
        """Sort modules along a rail"""
        if rail.orientation == RailOrientation.HORIZONTAL:
            return sorted(modules, key=lambda m: m['position']['x'])
        else:
            return sorted(modules, key=lambda m: m['position']['y'])
    
    def _calculate_clamp_positions(
        self,
        module: Dict[str, Any],
        rail: MountingRail
    ) -> List[Tuple[float, float, float]]:
        """Calculate clamp positions for a module on a rail"""
        pos = module['position']
        
        # Typically 4 clamps per module (2 per rail, 2 rails per module)
        # For simplicity, return 2 positions (left and right edges)
        if rail.orientation == RailOrientation.HORIZONTAL:
            return [
                (pos['x'] - 0.8, pos['y'], pos['z']),  # Left edge
                (pos['x'] + 0.8, pos['y'], pos['z'])   # Right edge
            ]
        else:
            return [
                (pos['x'], pos['y'] - 0.8, pos['z']),  # Bottom edge
                (pos['x'], pos['y'] + 0.8, pos['z'])   # Top edge
            ]
    
    def _group_modules_into_strings(
        self,
        module_positions: List[Dict[str, Any]],
        modules_per_string: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """Group modules into electrical strings"""
        strings = []
        current_string = []
        
        for module in module_positions:
            current_string.append(module)
            if len(current_string) >= modules_per_string:
                strings.append(current_string)
                current_string = []
        
        if current_string:
            strings.append(current_string)
        
        return strings
