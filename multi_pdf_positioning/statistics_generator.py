"""
Statistics Generator Module for Multi-PDF Positioning System

This module generates comprehensive statistics about position changes,
strategy distribution, and optimization results.

Requirements covered:
- 7.3: Calculate average position changes
- 7.4: Document strategy distribution and optimization summary
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

from multi_pdf_positioning.yml_parser import YMLElement


@dataclass
class PositionChange:
    """
    Information about a position change for a single element.
    
    Attributes:
        element_index: Index of the element
        element_text: Text content of the element
        old_position: Old position tuple (x1, y1, x2, y2)
        new_position: New position tuple (x1, y1, x2, y2)
        distance_moved: Distance moved (in points)
        x_change: Change in X coordinate (center)
        y_change: Change in Y coordinate (center)
        area_change: Change in area (square points)
    """
    element_index: int
    element_text: str
    old_position: Tuple[float, float, float, float]
    new_position: Tuple[float, float, float, float]
    distance_moved: float
    x_change: float
    y_change: float
    area_change: float


@dataclass
class StrategyStatistics:
    """
    Statistics for a specific positioning strategy.
    
    Attributes:
        strategy_name: Name of the strategy
        firma: Firma number
        seite: Seite number
        elements_count: Number of elements positioned
        avg_distance_moved: Average distance moved (in points)
        max_distance_moved: Maximum distance moved (in points)
        min_distance_moved: Minimum distance moved (in points)
        avg_x_change: Average X coordinate change
        avg_y_change: Average Y coordinate change
        collisions_before: Number of collisions before optimization
        collisions_after: Number of collisions after optimization
        validation_errors: Number of validation errors
        validation_warnings: Number of validation warnings
    """
    strategy_name: str
    firma: int
    seite: int
    elements_count: int = 0
    avg_distance_moved: float = 0.0
    max_distance_moved: float = 0.0
    min_distance_moved: float = 0.0
    avg_x_change: float = 0.0
    avg_y_change: float = 0.0
    collisions_before: int = 0
    collisions_after: int = 0
    validation_errors: int = 0
    validation_warnings: int = 0


@dataclass
class OptimizationSummary:
    """
    Overall summary of optimization results.
    
    Attributes:
        timestamp: When the summary was generated
        total_combinations: Total number of firma-seite combinations
        total_elements: Total number of elements processed
        strategies_used: Dictionary mapping strategy names to usage count
        avg_distance_moved: Overall average distance moved
        total_collisions_resolved: Total number of collisions resolved
        total_validation_errors: Total validation errors
        total_validation_warnings: Total validation warnings
        strategy_statistics: List of StrategyStatistics for each combination
        position_changes: List of all PositionChange objects
    """
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_combinations: int = 0
    total_elements: int = 0
    strategies_used: Dict[str, int] = field(default_factory=dict)
    avg_distance_moved: float = 0.0
    total_collisions_resolved: int = 0
    total_validation_errors: int = 0
    total_validation_warnings: int = 0
    strategy_statistics: List[StrategyStatistics] = field(default_factory=list)
    position_changes: List[PositionChange] = field(default_factory=list)


class StatisticsGenerator:
    """
    Generator for comprehensive statistics about position optimization.
    
    This class calculates statistics about position changes, strategy usage,
    and optimization results.
    """
    
    def __init__(self):
        """Initialize the statistics generator."""
        self.position_changes: List[PositionChange] = []
        self.strategy_stats: List[StrategyStatistics] = []
    
    def calculate_position_change(
        self,
        old_position: Tuple[float, float, float, float],
        new_position: Tuple[float, float, float, float],
        element_index: int,
        element_text: str = ""
    ) -> PositionChange:
        """
        Calculate statistics for a single position change.
        
        Args:
            old_position: Old position tuple (x1, y1, x2, y2)
            new_position: New position tuple (x1, y1, x2, y2)
            element_index: Index of the element
            element_text: Text content of the element
            
        Returns:
            PositionChange object with calculated statistics
            
        Requirements: 7.3
        """
        # Calculate centers
        old_center_x = (old_position[0] + old_position[2]) / 2
        old_center_y = (old_position[1] + old_position[3]) / 2
        new_center_x = (new_position[0] + new_position[2]) / 2
        new_center_y = (new_position[1] + new_position[3]) / 2
        
        # Calculate changes
        x_change = new_center_x - old_center_x
        y_change = new_center_y - old_center_y
        
        # Calculate distance moved (Euclidean distance)
        distance_moved = (x_change**2 + y_change**2)**0.5
        
        # Calculate area change
        old_area = (old_position[2] - old_position[0]) * (old_position[3] - old_position[1])
        new_area = (new_position[2] - new_position[0]) * (new_position[3] - new_position[1])
        area_change = new_area - old_area
        
        return PositionChange(
            element_index=element_index,
            element_text=element_text,
            old_position=old_position,
            new_position=new_position,
            distance_moved=distance_moved,
            x_change=x_change,
            y_change=y_change,
            area_change=area_change
        )
    
    def calculate_average_position_changes(
        self,
        old_positions: List[Tuple[float, float, float, float]],
        new_positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None
    ) -> Dict[str, float]:
        """
        Calculate average position changes for a set of positions.
        
        Args:
            old_positions: List of old position tuples
            new_positions: List of new position tuples
            elements: Optional list of YMLElement objects
            
        Returns:
            Dictionary with average statistics
            
        Requirements: 7.3
        """
        if not old_positions or not new_positions:
            return {
                "avg_distance_moved": 0.0,
                "avg_x_change": 0.0,
                "avg_y_change": 0.0,
                "avg_area_change": 0.0,
                "max_distance_moved": 0.0,
                "min_distance_moved": 0.0
            }
        
        changes = []
        for i in range(min(len(old_positions), len(new_positions))):
            element_text = ""
            if elements and i < len(elements):
                element_text = elements[i].text
            
            change = self.calculate_position_change(
                old_positions[i],
                new_positions[i],
                i,
                element_text
            )
            changes.append(change)
        
        # Calculate averages
        total_distance = sum(c.distance_moved for c in changes)
        total_x_change = sum(c.x_change for c in changes)
        total_y_change = sum(c.y_change for c in changes)
        total_area_change = sum(c.area_change for c in changes)
        
        count = len(changes)
        
        return {
            "avg_distance_moved": total_distance / count if count > 0 else 0.0,
            "avg_x_change": total_x_change / count if count > 0 else 0.0,
            "avg_y_change": total_y_change / count if count > 0 else 0.0,
            "avg_area_change": total_area_change / count if count > 0 else 0.0,
            "max_distance_moved": max((c.distance_moved for c in changes), default=0.0),
            "min_distance_moved": min((c.distance_moved for c in changes), default=0.0),
            "total_elements": count
        }
    
    def generate_strategy_statistics(
        self,
        strategy_name: str,
        firma: int,
        seite: int,
        old_positions: List[Tuple[float, float, float, float]],
        new_positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None,
        collisions_before: int = 0,
        collisions_after: int = 0,
        validation_errors: int = 0,
        validation_warnings: int = 0
    ) -> StrategyStatistics:
        """
        Generate statistics for a specific strategy application.
        
        Args:
            strategy_name: Name of the positioning strategy
            firma: Firma number
            seite: Seite number
            old_positions: List of old position tuples
            new_positions: List of new position tuples
            elements: Optional list of YMLElement objects
            collisions_before: Number of collisions before optimization
            collisions_after: Number of collisions after optimization
            validation_errors: Number of validation errors
            validation_warnings: Number of validation warnings
            
        Returns:
            StrategyStatistics object
            
        Requirements: 7.4
        """
        # Calculate position changes
        avg_stats = self.calculate_average_position_changes(
            old_positions,
            new_positions,
            elements
        )
        
        return StrategyStatistics(
            strategy_name=strategy_name,
            firma=firma,
            seite=seite,
            elements_count=avg_stats["total_elements"],
            avg_distance_moved=avg_stats["avg_distance_moved"],
            max_distance_moved=avg_stats["max_distance_moved"],
            min_distance_moved=avg_stats["min_distance_moved"],
            avg_x_change=avg_stats["avg_x_change"],
            avg_y_change=avg_stats["avg_y_change"],
            collisions_before=collisions_before,
            collisions_after=collisions_after,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings
        )
    
    def generate_optimization_summary(
        self,
        strategy_statistics: List[StrategyStatistics],
        position_changes: Optional[List[PositionChange]] = None
    ) -> OptimizationSummary:
        """
        Generate overall optimization summary from strategy statistics.
        
        Args:
            strategy_statistics: List of StrategyStatistics objects
            position_changes: Optional list of all PositionChange objects
            
        Returns:
            OptimizationSummary object
            
        Requirements: 7.3, 7.4
        """
        if not strategy_statistics:
            return OptimizationSummary()
        
        # Count strategies used
        strategies_used = {}
        for stat in strategy_statistics:
            strategy_name = stat.strategy_name
            strategies_used[strategy_name] = strategies_used.get(strategy_name, 0) + 1
        
        # Calculate totals
        total_combinations = len(strategy_statistics)
        total_elements = sum(stat.elements_count for stat in strategy_statistics)
        
        # Calculate average distance moved (weighted by element count)
        total_weighted_distance = sum(
            stat.avg_distance_moved * stat.elements_count
            for stat in strategy_statistics
        )
        avg_distance_moved = (
            total_weighted_distance / total_elements if total_elements > 0 else 0.0
        )
        
        # Calculate collision resolution
        total_collisions_before = sum(stat.collisions_before for stat in strategy_statistics)
        total_collisions_after = sum(stat.collisions_after for stat in strategy_statistics)
        total_collisions_resolved = total_collisions_before - total_collisions_after
        
        # Calculate validation totals
        total_validation_errors = sum(stat.validation_errors for stat in strategy_statistics)
        total_validation_warnings = sum(stat.validation_warnings for stat in strategy_statistics)
        
        return OptimizationSummary(
            total_combinations=total_combinations,
            total_elements=total_elements,
            strategies_used=strategies_used,
            avg_distance_moved=avg_distance_moved,
            total_collisions_resolved=total_collisions_resolved,
            total_validation_errors=total_validation_errors,
            total_validation_warnings=total_validation_warnings,
            strategy_statistics=strategy_statistics,
            position_changes=position_changes or []
        )
    
    def format_summary(self, summary: OptimizationSummary) -> str:
        """
        Format an optimization summary as a human-readable string.
        
        Args:
            summary: OptimizationSummary to format
            
        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("OPTIMIZATION SUMMARY")
        lines.append("=" * 70)
        lines.append(f"Generated: {summary.timestamp}")
        lines.append("")
        
        # Overall statistics
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 70)
        lines.append(f"  Total combinations processed: {summary.total_combinations}")
        lines.append(f"  Total elements optimized: {summary.total_elements}")
        lines.append(f"  Average distance moved: {summary.avg_distance_moved:.2f} pts")
        lines.append(f"  Collisions resolved: {summary.total_collisions_resolved}")
        lines.append(f"  Validation errors: {summary.total_validation_errors}")
        lines.append(f"  Validation warnings: {summary.total_validation_warnings}")
        lines.append("")
        
        # Strategy distribution
        lines.append("STRATEGY DISTRIBUTION")
        lines.append("-" * 70)
        for strategy, count in sorted(summary.strategies_used.items()):
            percentage = (count / summary.total_combinations * 100) if summary.total_combinations > 0 else 0
            lines.append(f"  {strategy}: {count} ({percentage:.1f}%)")
        lines.append("")
        
        # Top movers (elements that moved the most)
        if summary.position_changes:
            lines.append("TOP 10 POSITION CHANGES")
            lines.append("-" * 70)
            sorted_changes = sorted(
                summary.position_changes,
                key=lambda c: c.distance_moved,
                reverse=True
            )
            for i, change in enumerate(sorted_changes[:10], 1):
                text_preview = change.element_text[:30] if change.element_text else "N/A"
                lines.append(
                    f"  {i}. Element {change.element_index} ('{text_preview}'): "
                    f"{change.distance_moved:.2f} pts"
                )
            lines.append("")
        
        # Strategy performance
        lines.append("STRATEGY PERFORMANCE")
        lines.append("-" * 70)
        
        # Group by strategy
        strategy_groups = {}
        for stat in summary.strategy_statistics:
            if stat.strategy_name not in strategy_groups:
                strategy_groups[stat.strategy_name] = []
            strategy_groups[stat.strategy_name].append(stat)
        
        for strategy_name, stats in sorted(strategy_groups.items()):
            lines.append(f"\n  {strategy_name}:")
            
            # Calculate averages for this strategy
            avg_distance = sum(s.avg_distance_moved for s in stats) / len(stats)
            avg_collisions_before = sum(s.collisions_before for s in stats) / len(stats)
            avg_collisions_after = sum(s.collisions_after for s in stats) / len(stats)
            total_errors = sum(s.validation_errors for s in stats)
            total_warnings = sum(s.validation_warnings for s in stats)
            
            lines.append(f"    Applications: {len(stats)}")
            lines.append(f"    Avg distance moved: {avg_distance:.2f} pts")
            lines.append(f"    Avg collisions before: {avg_collisions_before:.1f}")
            lines.append(f"    Avg collisions after: {avg_collisions_after:.1f}")
            lines.append(f"    Total validation errors: {total_errors}")
            lines.append(f"    Total validation warnings: {total_warnings}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def export_to_json(
        self,
        summary: OptimizationSummary,
        output_path: str
    ):
        """
        Export optimization summary to JSON file.
        
        Args:
            summary: OptimizationSummary to export
            output_path: Path to output JSON file
        """
        # Convert to dictionary
        data = {
            "timestamp": summary.timestamp,
            "total_combinations": summary.total_combinations,
            "total_elements": summary.total_elements,
            "strategies_used": summary.strategies_used,
            "avg_distance_moved": summary.avg_distance_moved,
            "total_collisions_resolved": summary.total_collisions_resolved,
            "total_validation_errors": summary.total_validation_errors,
            "total_validation_warnings": summary.total_validation_warnings,
            "strategy_statistics": [
                {
                    "strategy_name": stat.strategy_name,
                    "firma": stat.firma,
                    "seite": stat.seite,
                    "elements_count": stat.elements_count,
                    "avg_distance_moved": stat.avg_distance_moved,
                    "max_distance_moved": stat.max_distance_moved,
                    "min_distance_moved": stat.min_distance_moved,
                    "avg_x_change": stat.avg_x_change,
                    "avg_y_change": stat.avg_y_change,
                    "collisions_before": stat.collisions_before,
                    "collisions_after": stat.collisions_after,
                    "validation_errors": stat.validation_errors,
                    "validation_warnings": stat.validation_warnings
                }
                for stat in summary.strategy_statistics
            ],
            "position_changes": [
                {
                    "element_index": change.element_index,
                    "element_text": change.element_text,
                    "old_position": change.old_position,
                    "new_position": change.new_position,
                    "distance_moved": change.distance_moved,
                    "x_change": change.x_change,
                    "y_change": change.y_change,
                    "area_change": change.area_change
                }
                for change in summary.position_changes
            ]
        }
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_to_csv(
        self,
        summary: OptimizationSummary,
        output_path: str
    ):
        """
        Export strategy statistics to CSV file.
        
        Args:
            summary: OptimizationSummary to export
            output_path: Path to output CSV file
        """
        import csv
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Strategy",
                "Firma",
                "Seite",
                "Elements",
                "Avg Distance Moved",
                "Max Distance Moved",
                "Min Distance Moved",
                "Avg X Change",
                "Avg Y Change",
                "Collisions Before",
                "Collisions After",
                "Validation Errors",
                "Validation Warnings"
            ])
            
            # Write data
            for stat in summary.strategy_statistics:
                writer.writerow([
                    stat.strategy_name,
                    stat.firma,
                    stat.seite,
                    stat.elements_count,
                    f"{stat.avg_distance_moved:.2f}",
                    f"{stat.max_distance_moved:.2f}",
                    f"{stat.min_distance_moved:.2f}",
                    f"{stat.avg_x_change:.2f}",
                    f"{stat.avg_y_change:.2f}",
                    stat.collisions_before,
                    stat.collisions_after,
                    stat.validation_errors,
                    stat.validation_warnings
                ])


# Convenience functions
def generate_statistics(
    old_positions: List[Tuple[float, float, float, float]],
    new_positions: List[Tuple[float, float, float, float]],
    elements: Optional[List[YMLElement]] = None
) -> Dict[str, float]:
    """
    Convenience function to generate statistics.
    
    Args:
        old_positions: List of old position tuples
        new_positions: List of new position tuples
        elements: Optional list of YMLElement objects
        
    Returns:
        Dictionary with statistics
    """
    generator = StatisticsGenerator()
    return generator.calculate_average_position_changes(old_positions, new_positions, elements)


if __name__ == "__main__":
    # Example usage
    print("\n=== Statistics Generator Demo ===\n")
    
    # Create generator
    generator = StatisticsGenerator()
    
    # Test positions
    old_positions = [
        (50, 700, 200, 750),
        (250, 700, 400, 750),
        (50, 600, 200, 650),
    ]
    
    new_positions = [
        (100, 720, 250, 770),
        (300, 680, 450, 730),
        (80, 580, 230, 630),
    ]
    
    print("Calculating position changes...")
    stats = generator.calculate_average_position_changes(old_positions, new_positions)
    
    print("\nAverage Position Changes:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}")
    
    # Generate strategy statistics
    print("\n--- Generating Strategy Statistics ---")
    strategy_stats = generator.generate_strategy_statistics(
        strategy_name="header-focused",
        firma=1,
        seite=1,
        old_positions=old_positions,
        new_positions=new_positions,
        collisions_before=2,
        collisions_after=0,
        validation_errors=0,
        validation_warnings=1
    )
    
    print(f"Strategy: {strategy_stats.strategy_name}")
    print(f"  Firma: {strategy_stats.firma}, Seite: {strategy_stats.seite}")
    print(f"  Elements: {strategy_stats.elements_count}")
    print(f"  Avg distance moved: {strategy_stats.avg_distance_moved:.2f} pts")
    print(f"  Collisions: {strategy_stats.collisions_before} → {strategy_stats.collisions_after}")
    
    # Generate optimization summary
    print("\n--- Generating Optimization Summary ---")
    summary = generator.generate_optimization_summary([strategy_stats])
    
    print(generator.format_summary(summary))
    
    print("\n✓ Statistics Generator module ready")
