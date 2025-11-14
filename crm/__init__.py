"""
CRM System Enhancement Package
Erweiterte CRM-Funktionalität für automatische Datenübernahme, 
Berechnungsversionierung, PDF-Archivierung und mehr.
"""

__version__ = "1.0.0"

# Note: Main CRM functions are in ../crm.py (parent directory)
# To use: import crm (from parent) or from crm import save_customer
# The crm/ package contains extensions and features

__all__ = []

def _import_crm_functions():
    """Lazy import of CRM functions to avoid circular imports."""
    import sys
    from pathlib import Path
    
    # Get parent directory and import crm.py directly
    parent_dir = Path(__file__).parent.parent
    crm_file = parent_dir / 'crm.py'
    
    if not crm_file.exists():
        return None
    
    # Load crm.py as a module
    import importlib.util
    spec = importlib.util.spec_from_file_location("crm_main", crm_file)
    if spec and spec.loader:
        crm_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(crm_main)
        return crm_main
    return None

# Provide convenient access (lazy loading)
_crm_module = None

def __getattr__(name):
    """Lazy load CRM functions on demand."""
    global _crm_module
    
    if _crm_module is None:
        _crm_module = _import_crm_functions()
    
    if _crm_module and hasattr(_crm_module, name):
        return getattr(_crm_module, name)
    
    raise AttributeError(f"module 'crm' has no attribute '{name}'")
