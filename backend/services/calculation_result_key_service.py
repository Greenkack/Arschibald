"""
Calculation Results Dynamic Keys Service

This module provides comprehensive dynamic key management for all calculation
results, including versioning, comparison, history tracking, and export.

Requirements: 14.7
Task: 225
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib

try:
    from backend.core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )
except ImportError:
    from core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )

try:
    from backend.core.german_formatter import GermanNumberFormatter
except ImportError:
    try:
        from core.german_formatter import GermanNumberFormatter
    except ImportError:
        # Fallback: create a simple formatter
        class GermanNumberFormatter:
            def format_number(self, value, decimals=2):
                """Simple German number formatting"""
                if isinstance(value, (int, float)):
                    formatted = f"{value:,.{decimals}f}"
                    # Replace , with temp, . with ,, temp with .
                    formatted = formatted.replace(',', 'TEMP')
                    formatted = formatted.replace('.', ',')
                    formatted = formatted.replace('TEMP', '.')
                    return formatted
                return str(value)


class CalculationType(str, Enum):
    """Enumeration of calculation types"""
    SOLAR = "solar"
    HEATPUMP = "heatpump"
    COMBINED = "combined"
    PRICE = "price"
    FINANCIAL = "financial"
    ENVIRONMENTAL = "environmental"
    TECHNICAL = "technical"
    CUSTOM = "custom"


@dataclass
class CalculationResultVersion:
    """
    Represents a versioned calculation result.
    """
    version_key: str
    version_number: int
    result_key: str
    calculation_type: CalculationType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    parent_version_key: Optional[str] = None
    change_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary"""
        return {
            'version_key': self.version_key,
            'version_number': self.version_number,
            'result_key': self.result_key,
            'calculation_type': self.calculation_type.value,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'parent_version_key': self.parent_version_key,
            'change_summary': self.change_summary,
            'metadata': self.metadata
        }


@dataclass
class CalculationComparison:
    """
    Represents a comparison between two calculation results.
    """
    comparison_key: str
    result_key_1: str
    result_key_2: str
    differences: Dict[str, Any]
    similarity_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert comparison to dictionary"""
        return {
            'comparison_key': self.comparison_key,
            'result_key_1': self.result_key_1,
            'result_key_2': self.result_key_2,
            'differences': self.differences,
            'similarity_score': self.similarity_score,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class CalculationResultKeyManager:
    """
    Manager for generating and tracking dynamic keys for calculation
    results.

    This class provides methods to attach dynamic keys to all calculation
    results, create result versioning, implement key-based comparison,
    build result history, and create result exports.
    """

    def __init__(self):
        """Initialize the calculation result key manager"""
        self.key_index = get_global_key_index()
        self.result_registry: Dict[str, 'CalculationResult'] = {}
        self.version_registry: Dict[str, List[CalculationResultVersion]] = {}
        self.comparison_registry: Dict[str, CalculationComparison] = {}
        self.history: List[Dict[str, Any]] = []
        self.formatter = GermanNumberFormatter()

    def create_result_key(
        self,
        calculation_type: CalculationType,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        custom_suffix: Optional[str] = None
    ) -> str:
        """
        Create a dynamic key for a calculation result.

        Args:
            calculation_type: Type of calculation
            project_id: Optional project ID
            user_id: Optional user ID
            custom_suffix: Optional custom suffix

        Returns:
            Generated dynamic key

        Example:
            >>> manager = CalculationResultKeyManager()
            >>> key = manager.create_result_key(
            ...     CalculationType.SOLAR,
            ...     project_id="PRJ_123"
            ... )
            >>> print(key)
            'SOL_20231116_143052_a1b2c3d4_PRJ_123'
        """
        # Map calculation type to key prefix
        prefix_map = {
            CalculationType.SOLAR: KeyPrefix.SOLAR_CALCULATION,
            CalculationType.HEATPUMP: KeyPrefix.HEATPUMP_CALCULATION,
            CalculationType.PRICE: KeyPrefix.PRICE_CALCULATION,
            CalculationType.COMBINED: KeyPrefix.SOLAR_CALCULATION,
            CalculationType.FINANCIAL: KeyPrefix.DATA,
            CalculationType.ENVIRONMENTAL: KeyPrefix.DATA,
            CalculationType.TECHNICAL: KeyPrefix.DATA,
            CalculationType.CUSTOM: KeyPrefix.DATA
        }

        prefix = prefix_map.get(calculation_type, KeyPrefix.DATA)

        # Create composite suffix
        suffix_parts = []
        if project_id:
            suffix_parts.append(project_id)
        if user_id:
            suffix_parts.append(user_id)
        if custom_suffix:
            suffix_parts.append(custom_suffix)
        suffix = "_".join(suffix_parts) if suffix_parts else None

        # Generate key using mixin
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            prefix=prefix,
            include_timestamp=True,
            include_uuid=True,
            custom_suffix=suffix
        )

        # Store metadata
        metadata = {
            'calculation_type': calculation_type.value,
            'project_id': project_id,
            'user_id': user_id,
            'created_at': datetime.now().isoformat()
        }

        self.key_index.add(key, None, metadata)

        return key

    def register_calculation_result(
        self,
        calculation_type: CalculationType,
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'CalculationResult':
        """
        Register a calculation result with dynamic key.

        Args:
            calculation_type: Type of calculation
            data: Calculation result data
            project_id: Optional project ID
            user_id: Optional user ID
            session_id: Optional session ID
            metadata: Additional metadata

        Returns:
            CalculationResult object with dynamic key

        Example:
            >>> manager = CalculationResultKeyManager()
            >>> result = manager.register_calculation_result(
            ...     CalculationType.SOLAR,
            ...     {
            ...         'system_size': 10.5,
            ...         'annual_production': 12000,
            ...         'payback_period': 8.5
            ...     },
            ...     project_id="PRJ_123"
            ... )
        """
        # Create result key
        result_key = self.create_result_key(
            calculation_type,
            project_id,
            user_id
        )

        # Create CalculationResult object
        calc_result = CalculationResult(
            key=result_key,
            calculation_type=calculation_type,
            data=data,
            project_id=project_id,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {}
        )

        # Register in registry
        self.result_registry[result_key] = calc_result

        # Create initial version
        self.create_version(result_key, data, user_id, session_id)

        # Add to history
        self.history.append({
            'action': 'register',
            'result_key': result_key,
            'calculation_type': calculation_type.value,
            'timestamp': datetime.now().isoformat()
        })

        return calc_result

    def get_result_by_key(
        self,
        key: str
    ) -> Optional['CalculationResult']:
        """
        Retrieve a calculation result by its dynamic key.

        Args:
            key: Dynamic key to lookup

        Returns:
            CalculationResult object or None if not found
        """
        return self.result_registry.get(key)

    def update_result(
        self,
        key: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        change_summary: Optional[str] = None
    ) -> bool:
        """
        Update a calculation result and create a new version.

        Args:
            key: Dynamic key of the result
            data: Updated calculation data
            user_id: Optional user ID
            session_id: Optional session ID
            change_summary: Optional summary of changes

        Returns:
            True if update successful, False otherwise
        """
        calc_result = self.get_result_by_key(key)
        if not calc_result:
            return False

        # Update data
        calc_result.update_data(data)

        # Create new version
        self.create_version(
            key,
            data,
            user_id,
            session_id,
            change_summary
        )

        # Add to history
        self.history.append({
            'action': 'update',
            'result_key': key,
            'timestamp': datetime.now().isoformat(),
            'change_summary': change_summary
        })

        return True

    def create_version(
        self,
        result_key: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        change_summary: Optional[str] = None
    ) -> CalculationResultVersion:
        """
        Create a new version of a calculation result.

        Args:
            result_key: Key of the result
            data: Result data for this version
            user_id: Optional user ID
            session_id: Optional session ID
            change_summary: Optional summary of changes

        Returns:
            CalculationResultVersion object

        Example:
            >>> manager = CalculationResultKeyManager()
            >>> version = manager.create_version(
            ...     result_key,
            ...     updated_data,
            ...     change_summary="Updated system size"
            ... )
        """
        calc_result = self.get_result_by_key(result_key)
        if not calc_result:
            raise ValueError(f"Result not found: {result_key}")

        # Get current version number
        versions = self.version_registry.get(result_key, [])
        version_number = len(versions) + 1

        # Create version key
        version_key = f"{result_key}_V{version_number}"

        # Get parent version key
        parent_version_key = None
        if versions:
            parent_version_key = versions[-1].version_key

        # Create version object
        version = CalculationResultVersion(
            version_key=version_key,
            version_number=version_number,
            result_key=result_key,
            calculation_type=calc_result.calculation_type,
            data=data.copy(),
            user_id=user_id,
            session_id=session_id,
            parent_version_key=parent_version_key,
            change_summary=change_summary
        )

        # Add to version registry
        if result_key not in self.version_registry:
            self.version_registry[result_key] = []
        self.version_registry[result_key].append(version)

        return version

    def get_versions(
        self,
        result_key: str
    ) -> List[CalculationResultVersion]:
        """
        Get all versions of a calculation result.

        Args:
            result_key: Key of the result

        Returns:
            List of CalculationResultVersion objects
        """
        return self.version_registry.get(result_key, []).copy()

    def get_version(
        self,
        result_key: str,
        version_number: int
    ) -> Optional[CalculationResultVersion]:
        """
        Get a specific version of a calculation result.

        Args:
            result_key: Key of the result
            version_number: Version number to retrieve

        Returns:
            CalculationResultVersion or None if not found
        """
        versions = self.version_registry.get(result_key, [])
        for version in versions:
            if version.version_number == version_number:
                return version
        return None

    def get_latest_version(
        self,
        result_key: str
    ) -> Optional[CalculationResultVersion]:
        """
        Get the latest version of a calculation result.

        Args:
            result_key: Key of the result

        Returns:
            Latest CalculationResultVersion or None if not found
        """
        versions = self.version_registry.get(result_key, [])
        return versions[-1] if versions else None

    def compare_results(
        self,
        key1: str,
        key2: str,
        include_metadata: bool = False
    ) -> CalculationComparison:
        """
        Compare two calculation results.

        Args:
            key1: Key of first result
            key2: Key of second result
            include_metadata: Whether to include metadata in comparison

        Returns:
            CalculationComparison object

        Example:
            >>> manager = CalculationResultKeyManager()
            >>> comparison = manager.compare_results(
            ...     result_key_1,
            ...     result_key_2
            ... )
            >>> print(f"Similarity: {comparison.similarity_score:.2%}")
        """
        result1 = self.get_result_by_key(key1)
        result2 = self.get_result_by_key(key2)

        if not result1 or not result2:
            raise ValueError("One or both results not found")

        # Create comparison key
        comparison_key = f"CMP_{key1}_{key2}"

        # Calculate differences
        differences = self._calculate_differences(
            result1.data,
            result2.data
        )

        # Calculate similarity score
        similarity_score = self._calculate_similarity(
            result1.data,
            result2.data
        )

        # Create comparison object
        comparison = CalculationComparison(
            comparison_key=comparison_key,
            result_key_1=key1,
            result_key_2=key2,
            differences=differences,
            similarity_score=similarity_score,
            metadata={
                'type1': result1.calculation_type.value,
                'type2': result2.calculation_type.value
            }
        )

        # Store comparison
        self.comparison_registry[comparison_key] = comparison

        return comparison

    def _calculate_differences(
        self,
        data1: Dict[str, Any],
        data2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate differences between two data dictionaries.

        Args:
            data1: First data dictionary
            data2: Second data dictionary

        Returns:
            Dictionary of differences
        """
        differences = {}

        # Find keys in both
        all_keys = set(data1.keys()) | set(data2.keys())

        for key in all_keys:
            val1 = data1.get(key)
            val2 = data2.get(key)

            if val1 != val2:
                differences[key] = {
                    'value1': val1,
                    'value2': val2,
                    'change': self._calculate_change(val1, val2)
                }

        return differences

    def _calculate_change(
        self,
        val1: Any,
        val2: Any
    ) -> Optional[Union[float, str]]:
        """
        Calculate the change between two values.

        Args:
            val1: First value
            val2: Second value

        Returns:
            Change value or description
        """
        # Try numeric calculation
        try:
            num1 = float(val1)
            num2 = float(val2)
            if num1 != 0:
                return ((num2 - num1) / num1) * 100  # Percentage change
            else:
                return num2  # Absolute change
        except (ValueError, TypeError):
            # Non-numeric comparison
            if val1 is None and val2 is not None:
                return "added"
            elif val1 is not None and val2 is None:
                return "removed"
            else:
                return "changed"

    def _calculate_similarity(
        self,
        data1: Dict[str, Any],
        data2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity score between two data dictionaries.

        Args:
            data1: First data dictionary
            data2: Second data dictionary

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not data1 and not data2:
            return 1.0

        all_keys = set(data1.keys()) | set(data2.keys())
        if not all_keys:
            return 1.0

        matching_keys = 0
        for key in all_keys:
            if key in data1 and key in data2:
                if data1[key] == data2[key]:
                    matching_keys += 1

        return matching_keys / len(all_keys)

    def get_result_history(
        self,
        result_key: Optional[str] = None,
        calculation_type: Optional[CalculationType] = None,
        user_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get result history with optional filters.

        Args:
            result_key: Optional result key filter
            calculation_type: Optional calculation type filter
            user_id: Optional user ID filter
            limit: Optional limit on number of results

        Returns:
            List of history entries

        Example:
            >>> manager = CalculationResultKeyManager()
            >>> history = manager.get_result_history(
            ...     calculation_type=CalculationType.SOLAR,
            ...     limit=10
            ... )
        """
        filtered = self.history.copy()

        if result_key:
            filtered = [
                e for e in filtered
                if e.get('result_key') == result_key
            ]

        if calculation_type:
            filtered = [
                e for e in filtered
                if e.get('calculation_type') == calculation_type.value
            ]

        if user_id:
            # Need to look up user_id from result
            filtered = [
                e for e in filtered
                if self._entry_matches_user(e, user_id)
            ]

        # Sort by timestamp (most recent first)
        filtered = sorted(
            filtered,
            key=lambda e: e.get('timestamp', ''),
            reverse=True
        )

        if limit:
            filtered = filtered[:limit]

        return filtered

    def _entry_matches_user(
        self,
        entry: Dict[str, Any],
        user_id: str
    ) -> bool:
        """Check if history entry matches user ID"""
        result_key = entry.get('result_key')
        if not result_key:
            return False

        result = self.get_result_by_key(result_key)
        return result and result.user_id == user_id

    def export_result(
        self,
        key: str,
        format: str = 'json',
        include_versions: bool = False,
        include_metadata: bool = True,
        apply_german_formatting: bool = True
    ) -> Union[str, Dict[str, Any]]:
        """
        Export a calculation result.

        Args:
            key: Dynamic key of the result
            format: Export format ('json', 'dict', 'csv')
            include_versions: Whether to include version history
            include_metadata: Whether to include metadata
            apply_german_formatting: Whether to apply German number format

        Returns:
            Exported data in specified format

        Example:
            >>> manager = CalculationResultKeyManager()
            >>> exported = manager.export_result(
            ...     result_key,
            ...     format='json',
            ...     include_versions=True
            ... )
        """
        calc_result = self.get_result_by_key(key)
        if not calc_result:
            raise ValueError(f"Result not found: {key}")

        # Build export data
        export_data = calc_result.to_dict(include_metadata)

        # Apply German formatting if requested
        if apply_german_formatting:
            export_data['data'] = self._apply_german_formatting(
                export_data['data']
            )

        # Include versions if requested
        if include_versions:
            versions = self.get_versions(key)
            export_data['versions'] = [
                v.to_dict() for v in versions
            ]
            if apply_german_formatting:
                for v in export_data['versions']:
                    v['data'] = self._apply_german_formatting(v['data'])

        # Format output
        if format == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format == 'dict':
            return export_data
        elif format == 'csv':
            return self._export_to_csv(export_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _apply_german_formatting(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply German number formatting to numeric values in data.

        Args:
            data: Data dictionary

        Returns:
            Data with German-formatted numbers
        """
        formatted = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                formatted[key] = self.formatter.format_number(value)
            elif isinstance(value, dict):
                formatted[key] = self._apply_german_formatting(value)
            elif isinstance(value, list):
                formatted[key] = [
                    self._apply_german_formatting(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                formatted[key] = value
        return formatted

    def _export_to_csv(self, data: Dict[str, Any]) -> str:
        """
        Export data to CSV format.

        Args:
            data: Data dictionary

        Returns:
            CSV string
        """
        lines = []

        # Header
        lines.append("Key,Value")

        # Flatten data
        flat_data = self._flatten_dict(data.get('data', {}))

        # Add rows
        for key, value in flat_data.items():
            lines.append(f'"{key}","{value}"')

        return "\n".join(lines)

    def _flatten_dict(
        self,
        d: Dict[str, Any],
        parent_key: str = '',
        sep: str = '.'
    ) -> Dict[str, Any]:
        """
        Flatten a nested dictionary.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(
                    self._flatten_dict(v, new_key, sep=sep).items()
                )
            else:
                items.append((new_key, v))
        return dict(items)

    def export_comparison(
        self,
        comparison_key: str,
        format: str = 'json'
    ) -> Union[str, Dict[str, Any]]:
        """
        Export a comparison result.

        Args:
            comparison_key: Key of the comparison
            format: Export format ('json', 'dict')

        Returns:
            Exported comparison data
        """
        comparison = self.comparison_registry.get(comparison_key)
        if not comparison:
            raise ValueError(f"Comparison not found: {comparison_key}")

        export_data = comparison.to_dict()

        if format == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format == 'dict':
            return export_data
        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered results.

        Returns:
            Dictionary with statistics
        """
        total_results = len(self.result_registry)
        total_versions = sum(
            len(versions)
            for versions in self.version_registry.values()
        )
        total_comparisons = len(self.comparison_registry)

        results_by_type = {}
        for result in self.result_registry.values():
            calc_type = result.calculation_type.value
            results_by_type[calc_type] = (
                results_by_type.get(calc_type, 0) + 1
            )

        return {
            'total_results': total_results,
            'total_versions': total_versions,
            'total_comparisons': total_comparisons,
            'results_by_type': results_by_type,
            'average_versions_per_result': (
                total_versions / total_results if total_results > 0 else 0
            ),
            'history_entries': len(self.history)
        }


class CalculationResult:
    """
    Represents a calculation result with dynamic key.
    """

    def __init__(
        self,
        key: str,
        calculation_type: CalculationType,
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize calculation result"""
        self.key = key
        self.calculation_type = calculation_type
        self.data = data.copy()
        self.project_id = project_id
        self.user_id = user_id
        self.session_id = session_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Update the calculation data.

        Args:
            data: New calculation data
        """
        self.data = data.copy()
        self.updated_at = datetime.now()

    def get_data(self) -> Dict[str, Any]:
        """
        Get the calculation data.

        Returns:
            Calculation data dictionary
        """
        return self.data.copy()

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a specific value from the calculation data.

        Args:
            key: Key to lookup
            default: Default value if key not found

        Returns:
            Value or default
        """
        return self.data.get(key, default)

    def set_value(self, key: str, value: Any) -> None:
        """
        Set a specific value in the calculation data.

        Args:
            key: Key to set
            value: Value to set
        """
        self.data[key] = value
        self.updated_at = datetime.now()

    def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Convert the calculation result to a dictionary.

        Args:
            include_metadata: Whether to include metadata

        Returns:
            Dictionary representation
        """
        result = {
            'key': self.key,
            'calculation_type': self.calculation_type.value,
            'data': self.data.copy(),
            'project_id': self.project_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_metadata:
            result['metadata'] = self.metadata

        return result


# Global calculation result key manager instance
_global_calc_result_manager = CalculationResultKeyManager()


def get_calculation_result_manager() -> CalculationResultKeyManager:
    """
    Get the global calculation result key manager instance.

    Returns:
        Global CalculationResultKeyManager instance
    """
    return _global_calc_result_manager
