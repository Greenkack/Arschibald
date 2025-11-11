"""
Performance Optimization Module for Multi-PDF Positioning System

This module provides performance measurement, profiling, and optimization
capabilities including:
- Runtime measurement for all 48 combinations
- Component-level performance profiling
- Caching implementation for frequently accessed data
- Performance reporting and recommendations

Requirements: Task 12.1
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from functools import wraps
import hashlib

# Import components for testing
from multi_pdf_positioning.yml_parser import YMLParser, YMLElement
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer, PDFAnalysis
from multi_pdf_positioning.position_calculator import PositionCalculator
from multi_pdf_positioning.yml_generator import YMLGenerator
from multi_pdf_positioning.validation_system import ValidationSystem
from multi_pdf_positioning.config import PDF_DIR, YML_DIR, OUTPUT_DIR, FIRMEN, SEITEN


@dataclass
class ComponentTiming:
    """
    Timing information for a single component operation.
    
    Attributes:
        component: Component name (e.g., "yml_parser", "pdf_analyzer")
        operation: Operation name (e.g., "parse_yml", "analyze_pdf")
        duration: Duration in seconds
        firma: Firma number (if applicable)
        seite: Seite number (if applicable)
        success: Whether operation succeeded
        error: Error message (if failed)
    """
    component: str
    operation: str
    duration: float
    firma: Optional[int] = None
    seite: Optional[int] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for the entire system.
    
    Attributes:
        total_combinations: Total number of combinations processed
        total_duration: Total execution time in seconds
        avg_duration_per_combination: Average time per combination
        component_timings: List of ComponentTiming objects
        cache_stats: Cache hit/miss statistics
        bottlenecks: Identified performance bottlenecks
        recommendations: Performance improvement recommendations
    """
    total_combinations: int
    total_duration: float
    avg_duration_per_combination: float
    component_timings: List[ComponentTiming] = field(default_factory=list)
    cache_stats: Dict[str, Any] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_combinations': self.total_combinations,
            'total_duration': self.total_duration,
            'avg_duration_per_combination': self.avg_duration_per_combination,
            'component_timings': [asdict(t) for t in self.component_timings],
            'cache_stats': self.cache_stats,
            'bottlenecks': self.bottlenecks,
            'recommendations': self.recommendations
        }


class PerformanceCache:
    """
    Simple in-memory cache for frequently accessed data.
    
    Caches:
    - PDF analyses (expensive to compute)
    - YML parsing results (moderate cost)
    - Position calculations (if deterministic)
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._access_count: Dict[str, int] = {}
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a string representation of all arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = "|".join(key_parts)
        
        # Hash for consistent key length
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if key in self._cache:
            self._hits += 1
            self._access_count[key] = self._access_count.get(key, 0) + 1
            return self._cache[key]
        else:
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any):
        """
        Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Evict least recently used if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Find least accessed key
            lru_key = min(self._access_count, key=self._access_count.get)
            del self._cache[lru_key]
            del self._access_count[lru_key]
        
        self._cache[key] = value
        self._access_count[key] = 0
    
    def clear(self):
        """Clear all cached items."""
        self._cache.clear()
        self._access_count.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }


class PerformanceProfiler:
    """
    Performance profiler for measuring component execution times.
    """
    
    def __init__(self):
        """Initialize profiler."""
        self.timings: List[ComponentTiming] = []
        self.cache = PerformanceCache(max_size=100)
    
    def time_operation(
        self,
        component: str,
        operation: str,
        firma: Optional[int] = None,
        seite: Optional[int] = None
    ):
        """
        Decorator to time an operation.
        
        Args:
            component: Component name
            operation: Operation name
            firma: Firma number (optional)
            seite: Seite number (optional)
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    
                    timing = ComponentTiming(
                        component=component,
                        operation=operation,
                        duration=duration,
                        firma=firma,
                        seite=seite,
                        success=success,
                        error=error
                    )
                    self.timings.append(timing)
            
            return wrapper
        return decorator
    
    def get_component_stats(self, component: str) -> Dict[str, Any]:
        """
        Get statistics for a specific component.
        
        Args:
            component: Component name
            
        Returns:
            Dictionary with component statistics
        """
        component_timings = [t for t in self.timings if t.component == component]
        
        if not component_timings:
            return {
                'count': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0
            }
        
        durations = [t.duration for t in component_timings]
        
        return {
            'count': len(component_timings),
            'total_duration': sum(durations),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'success_rate': sum(1 for t in component_timings if t.success) / len(component_timings) * 100
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all components.
        
        Returns:
            Dictionary mapping component names to their statistics
        """
        components = set(t.component for t in self.timings)
        return {comp: self.get_component_stats(comp) for comp in components}
    
    def identify_bottlenecks(self, threshold_percent: float = 20.0) -> List[str]:
        """
        Identify performance bottlenecks.
        
        A component is considered a bottleneck if it takes more than
        threshold_percent of total time.
        
        Args:
            threshold_percent: Percentage threshold for bottleneck identification
            
        Returns:
            List of bottleneck descriptions
        """
        total_duration = sum(t.duration for t in self.timings)
        
        if total_duration == 0:
            return []
        
        stats = self.get_all_stats()
        bottlenecks = []
        
        for component, component_stats in stats.items():
            percentage = (component_stats['total_duration'] / total_duration) * 100
            
            if percentage >= threshold_percent:
                bottlenecks.append(
                    f"{component}: {percentage:.1f}% of total time "
                    f"({component_stats['total_duration']:.2f}s)"
                )
        
        return bottlenecks
    
    def generate_recommendations(self) -> List[str]:
        """
        Generate performance improvement recommendations.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        stats = self.get_all_stats()
        cache_stats = self.cache.get_stats()
        
        # Check cache hit rate
        if cache_stats['hit_rate'] < 50 and cache_stats['total_requests'] > 10:
            recommendations.append(
                f"Low cache hit rate ({cache_stats['hit_rate']:.1f}%). "
                "Consider increasing cache size or improving cache key generation."
            )
        
        # Check for slow components
        for component, component_stats in stats.items():
            if component_stats['avg_duration'] > 1.0:
                recommendations.append(
                    f"{component} is slow (avg {component_stats['avg_duration']:.2f}s). "
                    "Consider optimization or caching."
                )
        
        # Check for high variance
        for component, component_stats in stats.items():
            if component_stats['count'] > 1:
                variance = component_stats['max_duration'] - component_stats['min_duration']
                if variance > component_stats['avg_duration']:
                    recommendations.append(
                        f"{component} has high variance "
                        f"(min: {component_stats['min_duration']:.2f}s, "
                        f"max: {component_stats['max_duration']:.2f}s). "
                        "Performance may be inconsistent."
                    )
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance is good. No major issues detected.")
        
        return recommendations


class PerformanceOptimizer:
    """
    Main performance optimization class.
    
    Measures performance, identifies bottlenecks, and provides optimization
    recommendations.
    """
    
    def __init__(
        self,
        pdf_dir: Optional[Path] = None,
        yml_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        enable_cache: bool = True
    ):
        """
        Initialize performance optimizer.
        
        Args:
            pdf_dir: PDF templates directory
            yml_dir: YML coordinates directory
            output_dir: Output directory
            enable_cache: Whether to enable caching
        """
        self.pdf_dir = Path(pdf_dir) if pdf_dir else PDF_DIR
        self.yml_dir = Path(yml_dir) if yml_dir else YML_DIR
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        self.enable_cache = enable_cache
        self.profiler = PerformanceProfiler()
        
        # Initialize components
        self.yml_parser = YMLParser()
        self.pdf_analyzer = PDFAnalyzer(str(self.pdf_dir))
        self.position_calculator = PositionCalculator()
        self.yml_generator = YMLGenerator()
        self.validation_system = ValidationSystem()
    
    def measure_all_combinations(
        self,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None
    ) -> PerformanceMetrics:
        """
        Measure performance for all combinations.
        
        Args:
            firmen: List of firma numbers (default: all)
            seiten: List of seite numbers (default: all)
            
        Returns:
            PerformanceMetrics with detailed measurements
        """
        if firmen is None:
            firmen = FIRMEN
        if seiten is None:
            seiten = SEITEN
        
        total_combinations = len(firmen) * len(seiten)
        
        print(f"\n=== Performance Measurement ===")
        print(f"Measuring {total_combinations} combinations...")
        print(f"Cache: {'Enabled' if self.enable_cache else 'Disabled'}")
        
        start_time = time.time()
        
        # Process all combinations
        for i, firma in enumerate(firmen):
            for j, seite in enumerate(seiten):
                current = i * len(seiten) + j + 1
                print(f"\r[{current}/{total_combinations}] F{firma}S{seite}...", end="")
                
                self._process_single_combination(firma, seite)
        
        print()  # New line
        
        total_duration = time.time() - start_time
        avg_duration = total_duration / total_combinations
        
        # Generate metrics
        metrics = PerformanceMetrics(
            total_combinations=total_combinations,
            total_duration=total_duration,
            avg_duration_per_combination=avg_duration,
            component_timings=self.profiler.timings,
            cache_stats=self.profiler.cache.get_stats(),
            bottlenecks=self.profiler.identify_bottlenecks(),
            recommendations=self.profiler.generate_recommendations()
        )
        
        return metrics
    
    def _process_single_combination(self, firma: int, seite: int):
        """
        Process a single combination with timing.
        
        Args:
            firma: Firma number
            seite: Seite number
        """
        try:
            # Step 1: Parse YML
            yml_filename = f"seite{seite}_f{firma}.yml"
            yml_path = self.yml_dir / yml_filename
            
            start = time.time()
            elements = self.yml_parser.parse_yml(str(yml_path))
            self.profiler.timings.append(ComponentTiming(
                component="yml_parser",
                operation="parse_yml",
                duration=time.time() - start,
                firma=firma,
                seite=seite,
                success=True
            ))
            
            # Step 2: Analyze PDF (with caching)
            pdf_filename = f"multi_nt_{seite:02d}_f{firma}.pdf"
            pdf_path = self.pdf_dir / pdf_filename
            
            cache_key = f"pdf_{firma}_{seite}"
            
            if self.enable_cache:
                pdf_analysis = self.profiler.cache.get(cache_key)
                if pdf_analysis is None:
                    start = time.time()
                    pdf_analysis = self.pdf_analyzer.analyze_pdf(str(pdf_path))
                    duration = time.time() - start
                    self.profiler.cache.set(cache_key, pdf_analysis)
                else:
                    duration = 0.0  # Cache hit
            else:
                start = time.time()
                pdf_analysis = self.pdf_analyzer.analyze_pdf(str(pdf_path))
                duration = time.time() - start
            
            self.profiler.timings.append(ComponentTiming(
                component="pdf_analyzer",
                operation="analyze_pdf",
                duration=duration,
                firma=firma,
                seite=seite,
                success=True
            ))
            
            # Step 3: Calculate positions
            start = time.time()
            new_positions = self.position_calculator.calculate_positions(
                elements,
                pdf_analysis,
                strategy=f"firma{firma}"
            )
            self.profiler.timings.append(ComponentTiming(
                component="position_calculator",
                operation="calculate_positions",
                duration=time.time() - start,
                firma=firma,
                seite=seite,
                success=True
            ))
            
            # Step 4: Generate YML
            output_path = self.output_dir / yml_filename
            
            start = time.time()
            self.yml_generator.generate_yml(
                elements,
                new_positions,
                str(output_path),
                str(yml_path)
            )
            self.profiler.timings.append(ComponentTiming(
                component="yml_generator",
                operation="generate_yml",
                duration=time.time() - start,
                firma=firma,
                seite=seite,
                success=True
            ))
            
            # Step 5: Validate
            start = time.time()
            self.validation_system.generate_validation_report(
                new_positions,
                elements,
                firma,
                seite
            )
            self.profiler.timings.append(ComponentTiming(
                component="validation_system",
                operation="validate",
                duration=time.time() - start,
                firma=firma,
                seite=seite,
                success=True
            ))
            
        except Exception as e:
            # Record error
            self.profiler.timings.append(ComponentTiming(
                component="workflow",
                operation="process_combination",
                duration=0,
                firma=firma,
                seite=seite,
                success=False,
                error=str(e)
            ))
    
    def display_metrics(self, metrics: PerformanceMetrics):
        """
        Display performance metrics in a readable format.
        
        Args:
            metrics: PerformanceMetrics to display
        """
        print("\n" + "=" * 70)
        print("PERFORMANCE METRICS")
        print("=" * 70)
        
        print(f"\nOverall:")
        print(f"  Total combinations: {metrics.total_combinations}")
        print(f"  Total duration: {metrics.total_duration:.2f}s")
        print(f"  Avg per combination: {metrics.avg_duration_per_combination:.3f}s")
        
        # Component statistics
        print(f"\nComponent Performance:")
        stats = self.profiler.get_all_stats()
        
        for component, component_stats in sorted(stats.items()):
            print(f"\n  {component}:")
            print(f"    Count: {component_stats['count']}")
            print(f"    Total: {component_stats['total_duration']:.2f}s")
            print(f"    Avg: {component_stats['avg_duration']:.3f}s")
            print(f"    Min: {component_stats['min_duration']:.3f}s")
            print(f"    Max: {component_stats['max_duration']:.3f}s")
            print(f"    Success rate: {component_stats['success_rate']:.1f}%")
        
        # Cache statistics
        if self.enable_cache:
            print(f"\nCache Statistics:")
            cache_stats = metrics.cache_stats
            print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
            print(f"  Hits: {cache_stats['hits']}")
            print(f"  Misses: {cache_stats['misses']}")
            print(f"  Hit rate: {cache_stats['hit_rate']:.1f}%")
        
        # Bottlenecks
        if metrics.bottlenecks:
            print(f"\nBottlenecks:")
            for bottleneck in metrics.bottlenecks:
                print(f"  ⚠ {bottleneck}")
        
        # Recommendations
        print(f"\nRecommendations:")
        for recommendation in metrics.recommendations:
            print(f"  • {recommendation}")
        
        print("=" * 70)
    
    def save_metrics(self, metrics: PerformanceMetrics, output_file: Path):
        """
        Save metrics to JSON file.
        
        Args:
            metrics: PerformanceMetrics to save
            output_file: Output file path
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Metrics saved to: {output_file}")


def measure_performance(
    firmen: Optional[List[int]] = None,
    seiten: Optional[List[int]] = None,
    enable_cache: bool = True,
    output_file: Optional[Path] = None
) -> PerformanceMetrics:
    """
    Convenience function to measure performance.
    
    Args:
        firmen: List of firma numbers (default: all)
        seiten: List of seite numbers (default: all)
        enable_cache: Whether to enable caching
        output_file: Optional output file for metrics
        
    Returns:
        PerformanceMetrics with measurements
        
    Example:
        >>> # Measure all combinations
        >>> metrics = measure_performance()
        
        >>> # Measure with caching disabled
        >>> metrics = measure_performance(enable_cache=False)
        
        >>> # Measure specific combinations
        >>> metrics = measure_performance(firmen=[1, 2], seiten=[1, 2, 3])
    """
    optimizer = PerformanceOptimizer(enable_cache=enable_cache)
    metrics = optimizer.measure_all_combinations(firmen=firmen, seiten=seiten)
    
    optimizer.display_metrics(metrics)
    
    if output_file:
        optimizer.save_metrics(metrics, output_file)
    
    return metrics


if __name__ == "__main__":
    # Run performance measurement
    print("\n=== Performance Optimizer Demo ===\n")
    
    # Measure with cache enabled
    print("Measuring with cache enabled...")
    metrics_cached = measure_performance(
        enable_cache=True,
        output_file=Path("multi_pdf_positioning/performance_metrics_cached.json")
    )
    
    print("\n" + "-" * 70 + "\n")
    
    # Measure with cache disabled
    print("Measuring with cache disabled...")
    metrics_uncached = measure_performance(
        enable_cache=False,
        output_file=Path("multi_pdf_positioning/performance_metrics_uncached.json")
    )
    
    # Compare
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"With cache: {metrics_cached.total_duration:.2f}s")
    print(f"Without cache: {metrics_uncached.total_duration:.2f}s")
    
    speedup = metrics_uncached.total_duration / metrics_cached.total_duration
    print(f"Speedup: {speedup:.2f}x")
    print("=" * 70)
