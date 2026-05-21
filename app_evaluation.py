"""
Comprehensive Application Evaluation System.

Evaluates application performance, accuracy, and reliability across:
- Calculation accuracy
- Response times
- Error rates
- UI responsiveness
- Data integrity
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceEvaluator:
    """Evaluates application performance metrics."""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
    
    def __call__(self, *, operation: str, execution_time: float, **kwargs) -> Dict[str, Any]:
        """
        Evaluate performance of an operation.
        
        Args:
            operation: Name of the operation
            execution_time: Time taken in seconds
            
        Returns:
            Performance evaluation result
        """
        # Thresholds (in seconds)
        thresholds = {
            "calculation": 1.0,
            "database": 0.5,
            "pdf_generation": 3.0,
            "ui_render": 0.3,
            "default": 1.0
        }
        
        threshold = thresholds.get(operation.split(".")[0], thresholds["default"])
        
        is_acceptable = execution_time <= threshold
        score = 5 if execution_time < threshold * 0.5 else \
                4 if execution_time < threshold * 0.75 else \
                3 if execution_time <= threshold else \
                2 if execution_time < threshold * 1.5 else 1
        
        result = {
            "operation": operation,
            "execution_time_seconds": execution_time,
            "threshold_seconds": threshold,
            "is_acceptable": is_acceptable,
            "performance_score": score,
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics.append(result)
        return result


class AccuracyEvaluator:
    """Evaluates calculation accuracy."""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
    
    def __call__(self, *, calculation_type: str, result: float, expected: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        """
        Evaluate calculation accuracy.
        
        Args:
            calculation_type: Type of calculation
            result: Calculated result
            expected: Expected result (if known)
            
        Returns:
            Accuracy evaluation result
        """
        evaluation = {
            "calculation_type": calculation_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for basic validity
        validations = {
            "is_numeric": isinstance(result, (int, float)),
            "is_finite": isinstance(result, (int, float)) and abs(result) != float('inf'),
            "is_positive": result >= 0 if isinstance(result, (int, float)) else None,
            "is_not_nan": result == result if isinstance(result, (int, float)) else None
        }
        
        evaluation["validations"] = validations
        evaluation["is_valid"] = all(v for v in validations.values() if v is not None)
        
        # Compare with expected if provided
        if expected is not None:
            error = abs(result - expected) / max(abs(expected), 1e-10)
            evaluation["expected"] = expected
            evaluation["error_percentage"] = error * 100
            evaluation["is_accurate"] = error < 0.01  # 1% tolerance
        
        self.metrics.append(evaluation)
        return evaluation


class ErrorRateEvaluator:
    """Evaluates application error rates."""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        self.total_operations = 0
        self.error_count = 0
    
    def __call__(self, *, operation: str, success: bool, error_type: Optional[str] = None, error_message: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Record operation result for error rate calculation.
        
        Args:
            operation: Name of the operation
            success: Whether operation succeeded
            error_type: Type of error if failed
            error_message: Error message if failed
            
        Returns:
            Error rate evaluation result
        """
        self.total_operations += 1
        if not success:
            self.error_count += 1
        
        result = {
            "operation": operation,
            "success": success,
            "error_rate": self.error_count / max(self.total_operations, 1),
            "timestamp": datetime.now().isoformat()
        }
        
        if not success:
            result["error_type"] = error_type
            result["error_message"] = error_message
        
        self.metrics.append(result)
        return result


class DataIntegrityEvaluator:
    """Evaluates data integrity and consistency."""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
    
    def __call__(self, *, data_type: str, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Evaluate data integrity.
        
        Args:
            data_type: Type of data being evaluated
            data: The data to evaluate
            
        Returns:
            Data integrity evaluation result
        """
        checks = {
            "is_not_none": data is not None,
            "is_not_empty": bool(data) if data is not None else False
        }
        
        # Type-specific checks
        if isinstance(data, dict):
            checks["has_required_keys"] = len(data) > 0
        elif isinstance(data, (list, tuple)):
            checks["has_items"] = len(data) > 0
        elif isinstance(data, str):
            checks["not_empty_string"] = len(data.strip()) > 0
        
        result = {
            "data_type": data_type,
            "checks": checks,
            "is_valid": all(checks.values()),
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics.append(result)
        return result


class AppEvaluationSystem:
    """Main evaluation system coordinating all evaluators."""
    
    def __init__(self, output_dir: str = "evaluation_results"):
        """
        Initialize evaluation system.
        
        Args:
            output_dir: Directory to save evaluation results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize evaluators
        self.performance_evaluator = PerformanceEvaluator()
        self.accuracy_evaluator = AccuracyEvaluator()
        self.error_rate_evaluator = ErrorRateEvaluator()
        self.data_integrity_evaluator = DataIntegrityEvaluator()
        
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Evaluation system initialized: {self.session_id}")
    
    def evaluate_operation(self, operation_type: str, **metrics) -> Dict[str, Any]:
        """
        Evaluate an operation comprehensively.
        
        Args:
            operation_type: Type of operation (calculation, database, pdf, ui)
            **metrics: Metrics to evaluate
            
        Returns:
            Combined evaluation results
        """
        results = {
            "operation_type": operation_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Performance evaluation
        if "execution_time" in metrics:
            results["performance"] = self.performance_evaluator(
                operation=operation_type,
                execution_time=metrics["execution_time"]
            )
        
        # Accuracy evaluation
        if "result" in metrics and "calculation_type" in metrics:
            results["accuracy"] = self.accuracy_evaluator(
                calculation_type=metrics["calculation_type"],
                result=metrics["result"],
                expected=metrics.get("expected")
            )
        
        # Error rate tracking
        results["error_tracking"] = self.error_rate_evaluator(
            operation=operation_type,
            success=metrics.get("success", True),
            error_type=metrics.get("error_type"),
            error_message=metrics.get("error_message")
        )
        
        # Data integrity
        if "data" in metrics:
            results["data_integrity"] = self.data_integrity_evaluator(
                data_type=metrics.get("data_type", "unknown"),
                data=metrics["data"]
            )
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.
        
        Returns:
            Evaluation report with aggregate metrics
        """
        report = {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "summary": {}
        }
        
        # Performance summary
        if self.performance_evaluator.metrics:
            perf_metrics = self.performance_evaluator.metrics
            avg_time = sum(m["execution_time_seconds"] for m in perf_metrics) / len(perf_metrics)
            acceptable_count = sum(1 for m in perf_metrics if m["is_acceptable"])
            
            report["summary"]["performance"] = {
                "total_operations": len(perf_metrics),
                "average_execution_time": avg_time,
                "acceptable_performance_rate": acceptable_count / len(perf_metrics),
                "average_score": sum(m["performance_score"] for m in perf_metrics) / len(perf_metrics)
            }
        
        # Accuracy summary
        if self.accuracy_evaluator.metrics:
            acc_metrics = self.accuracy_evaluator.metrics
            valid_count = sum(1 for m in acc_metrics if m["is_valid"])
            
            report["summary"]["accuracy"] = {
                "total_calculations": len(acc_metrics),
                "valid_results_rate": valid_count / len(acc_metrics),
                "accuracy_rate": sum(1 for m in acc_metrics if m.get("is_accurate", True)) / len(acc_metrics)
            }
        
        # Error rate summary
        report["summary"]["errors"] = {
            "total_operations": self.error_rate_evaluator.total_operations,
            "error_count": self.error_rate_evaluator.error_count,
            "error_rate": self.error_rate_evaluator.error_count / max(self.error_rate_evaluator.total_operations, 1),
            "success_rate": 1 - (self.error_rate_evaluator.error_count / max(self.error_rate_evaluator.total_operations, 1))
        }
        
        # Data integrity summary
        if self.data_integrity_evaluator.metrics:
            integrity_metrics = self.data_integrity_evaluator.metrics
            valid_count = sum(1 for m in integrity_metrics if m["is_valid"])
            
            report["summary"]["data_integrity"] = {
                "total_checks": len(integrity_metrics),
                "valid_data_rate": valid_count / len(integrity_metrics)
            }
        
        # Detailed metrics
        report["detailed_metrics"] = {
            "performance": self.performance_evaluator.metrics[-50:],  # Last 50
            "accuracy": self.accuracy_evaluator.metrics[-50:],
            "errors": self.error_rate_evaluator.metrics[-50:],
            "data_integrity": self.data_integrity_evaluator.metrics[-50:]
        }
        
        return report
    
    def save_report(self, report: Optional[Dict[str, Any]] = None) -> Path:
        """
        Save evaluation report to file.
        
        Args:
            report: Report to save (generates new if None)
            
        Returns:
            Path to saved report
        """
        if report is None:
            report = self.generate_report()
        
        filename = f"evaluation_report_{self.session_id}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation report saved: {filepath}")
        return filepath
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status of the application.
        
        Returns:
            Health status summary
        """
        error_rate = self.error_rate_evaluator.error_count / max(self.error_rate_evaluator.total_operations, 1)
        
        # Determine health status
        if error_rate < 0.01:
            health = "HEALTHY"
        elif error_rate < 0.05:
            health = "DEGRADED"
        else:
            health = "UNHEALTHY"
        
        return {
            "status": health,
            "error_rate": error_rate,
            "total_operations": self.error_rate_evaluator.total_operations,
            "timestamp": datetime.now().isoformat()
        }


# Global evaluation system instance
evaluation_system = AppEvaluationSystem()


# Convenience functions
def evaluate_performance(operation: str, execution_time: float) -> Dict[str, Any]:
    """Evaluate operation performance."""
    return evaluation_system.performance_evaluator(
        operation=operation,
        execution_time=execution_time
    )


def evaluate_accuracy(calculation_type: str, result: float, expected: Optional[float] = None) -> Dict[str, Any]:
    """Evaluate calculation accuracy."""
    return evaluation_system.accuracy_evaluator(
        calculation_type=calculation_type,
        result=result,
        expected=expected
    )


def track_error(operation: str, error: Exception) -> Dict[str, Any]:
    """Track an error."""
    return evaluation_system.error_rate_evaluator(
        operation=operation,
        success=False,
        error_type=type(error).__name__,
        error_message=str(error)
    )


def track_success(operation: str) -> Dict[str, Any]:
    """Track a successful operation."""
    return evaluation_system.error_rate_evaluator(
        operation=operation,
        success=True
    )


if __name__ == "__main__":
    # Test evaluation system
    print("Testing Evaluation System...")
    
    # Test performance
    evaluate_performance("calculation.solar_output", 0.5)
    evaluate_performance("database.query", 0.2)
    
    # Test accuracy
    evaluate_accuracy("pv_output", 8251.92, 8250.0)
    
    # Test error tracking
    track_success("ui.render")
    track_error("calculation.error", ValueError("Invalid input"))
    
    # Generate report
    report = evaluation_system.generate_report()
    print(json.dumps(report, indent=2))
    
    # Save report
    evaluation_system.save_report()
