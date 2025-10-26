"""
StorageModelResolver for correct storage model name resolution.

This module provides functionality to resolve storage IDs to model names
for use in price matrix lookups, with proper fallback handling.
"""

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class StorageModelResolver:
    """
    Resolves storage IDs to model names for price matrix lookups.

    This class handles the conversion from storage product IDs (used in the UI)
    to storage model names (used in the price matrix columns) with proper
    fallback logic for "Ohne Speicher" scenarios.
    """

    def __init__(self):
        """Initialize the StorageModelResolver."""
        self._cache = {}  # Simple cache for resolved names
        logger.debug("StorageModelResolver initialized")

    def resolve_storage_name(self,
                             storage_id: str | None,
                             include_storage: bool,
                             get_product_func: Callable[[int],
                                                        dict[str,
                                                             Any] | None]) -> str:
        """
        Resolve storage ID to model name for matrix lookup.

        Args:
            storage_id: Product ID of the selected storage (can be None)
            include_storage: Whether storage is included in the calculation
            get_product_func: Function to retrieve product details by ID

        Returns:
            Storage model name for matrix lookup or "Ohne Speicher"

        The resolution logic follows this priority:
        1. If include_storage is False -> "Ohne Speicher"
        2. If storage_id is None/empty -> "Ohne Speicher"
        3. Try to get product by ID and extract model_name
        4. If product not found or no model_name -> "Ohne Speicher"
        5. Return the resolved model_name
        """
        # Step 1: Check if storage should be included
        if not include_storage:
            logger.debug("Storage not included, returning 'Ohne Speicher'")
            return "Ohne Speicher"

        # Step 2: Check if storage_id is provided
        if not storage_id:
            logger.debug("No storage_id provided, returning 'Ohne Speicher'")
            return "Ohne Speicher"

        # Step 3: Try to convert storage_id to integer
        try:
            storage_id_int = int(storage_id)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid storage_id format: '{storage_id}', returning 'Ohne Speicher'")
            return "Ohne Speicher"

        # Step 4: Check cache first
        cache_key = f"storage_{storage_id_int}"
        if cache_key in self._cache:
            cached_result = self._cache[cache_key]
            logger.debug(
                f"Using cached result for storage_id {storage_id_int}: '{cached_result}'")
            return cached_result

        # Step 5: Try to get product details
        try:
            storage_details = get_product_func(storage_id_int)
        except Exception as e:
            logger.error(
                f"Error calling get_product_func for storage_id {storage_id_int}: {e}")
            storage_details = None

        # Step 6: Extract model name
        if not storage_details:
            logger.warning(
                f"Storage product with ID {storage_id_int} not found in database")
            result = "Ohne Speicher"
        else:
            model_name = storage_details.get('model_name')
            if not model_name or not model_name.strip():
                logger.warning(
                    f"Storage product ID {storage_id_int} has no model_name")
                result = "Ohne Speicher"
            else:
                result = model_name.strip()
                logger.debug(
                    f"Resolved storage_id {storage_id_int} to model_name: '{result}'")

        # Step 7: Cache the result
        self._cache[cache_key] = result

        return result

    def normalize_storage_name(self, storage_name: str) -> str:
        """
        Normalize storage name for consistent matching.

        Args:
            storage_name: Raw storage name

        Returns:
            Normalized storage name (trimmed, consistent case)
        """
        if not storage_name:
            return "Ohne Speicher"

        normalized = str(storage_name).strip()

        # Handle common variations of "no storage"
        no_storage_variants = [
            "ohne speicher", "kein speicher", "no storage",
            "ohne", "none", "null", ""
        ]

        if normalized.lower() in no_storage_variants:
            return "Ohne Speicher"

        return normalized

    def validate_storage_name_in_matrix(
            self, storage_name: str, available_storage_models: list) -> tuple[str, bool]:
        """
        Validate if storage name exists in matrix and suggest fallback.

        Args:
            storage_name: Storage model name to validate
            available_storage_models: List of available storage models in matrix

        Returns:
            Tuple of (final_storage_name, is_exact_match)
            - final_storage_name: Name to use for lookup (may be fallback)
            - is_exact_match: True if exact match found, False if using fallback
        """
        if not storage_name or not available_storage_models:
            return "Ohne Speicher", False

        normalized_input = storage_name.strip().lower()

        # Check for exact match (case-insensitive)
        for model in available_storage_models:
            if model.strip().lower() == normalized_input:
                logger.debug(
                    f"Exact match found for storage '{storage_name}': '{model}'")
                return model, True

        # Check for partial match (contains)
        for model in available_storage_models:
            if normalized_input in model.strip().lower(
            ) or model.strip().lower() in normalized_input:
                logger.info(
                    f"Partial match found for storage '{storage_name}': '{model}'")
                return model, False

        # No match found, use fallback
        logger.warning(f"Storage model '{storage_name}' not found in matrix. "
                       f"Available models: {available_storage_models}. Using 'Ohne Speicher'")
        return "Ohne Speicher", False

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        logger.debug("Storage resolver cache cleared")

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache information
        """
        return {
            "cache_size": len(self._cache),
            "cached_items": list(self._cache.keys())
        }


# Convenience function for direct usage
def resolve_storage_model_name(storage_id: str | None,
                               include_storage: bool,
                               get_product_func: Callable[[int],
                                                          dict[str,
                                                               Any] | None]) -> str:
    """
    Convenience function to resolve storage model name.

    Args:
        storage_id: Product ID of the selected storage
        include_storage: Whether storage is included
        get_product_func: Function to get product by ID

    Returns:
        Resolved storage model name
    """
    resolver = StorageModelResolver()
    return resolver.resolve_storage_name(
        storage_id, include_storage, get_product_func)
