"""Enhanced Pricing System

A comprehensive pricing calculation system for PV and heat pump applications
with dynamic key generation for PDF integration, profit margin management,
and separate handling of different system types.
"""

from .dynamic_key_manager import DynamicKeyManager, KeyCategory
from .enhanced_pricing_engine import FinalPricingResult, PricingEngine, PricingResult

__version__ = "1.0.0"
__all__ = [
    "PricingEngine",
    "PricingResult",
    "FinalPricingResult",
    "DynamicKeyManager",
    "KeyCategory"
]
