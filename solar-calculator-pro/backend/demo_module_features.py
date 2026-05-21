"""
Module Features Demo

Demonstrates the usage of module-level feature toggles
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.services.module_feature_service import ModuleFeatureService


def demo_initialize():
    """Demo: Initialize module features"""
    print("\n" + "="*80)
    print("DEMO: Initialize Module Features")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = ModuleFeatureService(db)
        results = service.initialize_module_features()
        
        created = sum(1 for v in results.values() if v == "created")
        existing = sum(1 for v in results.values() if v == "already_exists")
        errors = sum(1 for v in results.values() if v.startswith("error"))
        
        print(f"\n Initialization complete!")
        print(f"   Total: {len(results)}")
        print(f"   Created: {created}")
        print(f"   Existing: {existing}")
        print(f"   Errors: {errors}")
        
        if errors > 0:
            print("\n Errors:")
            for key, value in results.items():
                if value.startswith("error"):
                    print(f"   {key}: {value}")
    
    finally:
        db.close()


def demo_check_module():
    """Demo: Check if a module is enabled"""
    print("\n" + "="*80)
    print("DEMO: Check Module Status")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = ModuleFeatureService(db)
        
        modules = [
            ("Solar Calculator", ModuleFeatureService.SOLAR_CALCULATOR),
            ("Heat Pump", ModuleFeatureService.HEAT_PUMP),
            ("Price Matrix", ModuleFeatureService.PRICE_MATRIX),
            ("PDF Generation", ModuleFeatureService.PDF_GENERATION),
            ("CRM", ModuleFeatureService.CRM),
            ("3D Visualization", ModuleFeatureService.VISUALIZATION_3D),
        ]
        
        print("\nModule Status:")
        for name, key in modules:
            is_enabled = service.is_module_enabled(key)
            status = " ENABLED" if is_enabled else " DISABLED"
            print(f"   {name:20} {status}")
    
    finally:
        db.close()


def demo_check_sub_features():
    """Demo: Check sub-feature status"""
    print("\n" + "="*80)
    print("DEMO: Check Sub-Feature Status")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = ModuleFeatureService(db)
        
        print("\nSolar Calculator Sub-Features:")
        sub_features = [
            ("Basic Calculation", ModuleFeatureService.SOLAR_BASIC_CALC),
            ("Advanced Calculation", ModuleFeatureService.SOLAR_ADVANCED_CALC),
            ("Shading Analysis", ModuleFeatureService.SOLAR_SHADING_ANALYSIS),
            ("Battery Storage", ModuleFeatureService.SOLAR_BATTERY_STORAGE),
            ("Financial Analysis", ModuleFeatureService.SOLAR_FINANCIAL_ANALYSIS),
            ("Weather Integration", ModuleFeatureService.SOLAR_WEATHER_INTEGRATION),
            ("Monitoring", ModuleFeatureService.SOLAR_MONITORING),
        ]
        
        for name, key in sub_features:
            is_enabled = service.is_sub_feature_enabled(
                ModuleFeatureService.SOLAR_CALCULATOR,
                key
            )
            status = " ENABLED" if is_enabled else " DISABLED"
            print(f"   {name:25} {status}")
    
    finally:
        db.close()


def demo_toggle_module():
    """Demo: Toggle a module on/off"""
    print("\n" + "="*80)
    print("DEMO: Toggle Module")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = ModuleFeatureService(db)
        
        module_key = ModuleFeatureService.SOLAR_CALCULATOR
        
        # Check current status
        initial_status = service.is_module_enabled(module_key)
        print(f"\nInitial status: {'ENABLED' if initial_status else 'DISABLED'}")
        
        # Disable module
        print("\n Disabling module...")
        service.disable_module(module_key)
        status_after_disable = service.is_module_enabled(module_key)
        print(f"   Status after disable: {'ENABLED' if status_after_disable else 'DISABLED'}")
        
        # Enable module
        print("\n Enabling module...")
        service.enable_module(module_key)
        status_after_enable = service.is_module_enabled(module_key)
        print(f"   Status after enable: {'ENABLED' if status_after_enable else 'DISABLED'}")
        
        # Restore initial status
        if initial_status:
            service.enable_module(module_key)
        else:
            service.disable_module(module_key)
        print(f"\n Restored to initial status: {'ENABLED' if initial_status else 'DISABLED'}")
    
    finally:
        db.close()


def demo_toggle_sub_feature():
    """Demo: Toggle a sub-feature on/off"""
    print("\n" + "="*80)
    print("DEMO: Toggle Sub-Feature")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = ModuleFeatureService(db)
        
        module_key = ModuleFeatureService.SOLAR_CALCULATOR
        sub_feature_key = ModuleFeatureService.SOLAR_SHADING_ANALYSIS
        
        # Ensure module is enabled
        service.enable_module(module_key)
        
        # Check current status
        initial_status = service.is_sub_feature_enabled(module_key, sub_feature_key)
        print(f"\nInitial status: {'ENABLED' if initial_status else 'DISABLED'}")
        
        # Disable sub-feature
        print("\n Disabling sub-feature...")
        service.disable_sub_feature(sub_feature_key)
        status_after_disable = service.is_sub_feature_enabled(module_key, sub_feature_key)
        print(f"   Status after disable: {'ENABLED' if status_after_disable else 'DISABLED'}")
        
        # Enable sub-feature
        print("\n Enabling sub-feature...")
        service.enable_sub_feature(sub_feature_key)
        status_after_enable = service.is_sub_feature_enabled(module_key, sub_feature_key)
        print(f"   Status after enable: {'ENABLED' if status_after_enable else 'DISABLED'}")
        
        # Restore initial status
        if initial_status:
            service.enable_sub_feature(sub_feature_key)
        else:
            service.disable_sub_feature(sub_feature_key)
        print(f"\n Restored to initial status: {'ENABLED' if initial_status else 'DISABLED'}")
    
    finally:
        db.close()


def demo_get_all_status():
    """Demo: Get status of all modules and sub-features"""
    print("\n" + "="*80)
    print("DEMO: Get All Module Status")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = ModuleFeatureService(db)
        status = service.get_module_status()
        
        for module_name, module_data in status.items():
            module_status = " ENABLED" if module_data["enabled"] else " DISABLED"
            print(f"\n{module_name.upper().replace('_', ' ')} {module_status}")
            
            if module_data["sub_features"]:
                print("  Sub-Features:")
                for sub_key, sub_enabled in module_data["sub_features"].items():
                    sub_name = sub_key.split('.')[-1].replace('_', ' ').title()
                    sub_status = "" if sub_enabled else ""
                    print(f"    {sub_status} {sub_name}")
    
    finally:
        db.close()


def demo_parent_module_dependency():
    """Demo: Show that sub-features depend on parent module"""
    print("\n" + "="*80)
    print("DEMO: Parent Module Dependency")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = ModuleFeatureService(db)
        
        module_key = ModuleFeatureService.SOLAR_CALCULATOR
        sub_feature_key = ModuleFeatureService.SOLAR_BASIC_CALC
        
        # Enable sub-feature
        service.enable_sub_feature(sub_feature_key)
        
        # Disable parent module
        print("\n1⃣ Disabling parent module (Solar Calculator)...")
        service.disable_module(module_key)
        
        # Check sub-feature status
        sub_enabled = service.is_sub_feature_enabled(module_key, sub_feature_key)
        print(f"   Sub-feature status: {'ENABLED' if sub_enabled else 'DISABLED'}")
        print("   ℹ  Sub-feature is disabled because parent module is disabled")
        
        # Enable parent module
        print("\n2⃣ Enabling parent module...")
        service.enable_module(module_key)
        
        # Check sub-feature status again
        sub_enabled = service.is_sub_feature_enabled(module_key, sub_feature_key)
        print(f"   Sub-feature status: {'ENABLED' if sub_enabled else 'DISABLED'}")
        print("   ℹ  Sub-feature is now enabled because parent module is enabled")
    
    finally:
        db.close()


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("MODULE FEATURES DEMO")
    print("="*80)
    print("\nThis demo shows how to use module-level feature toggles")
    
    try:
        # Run demos
        demo_initialize()
        demo_check_module()
        demo_check_sub_features()
        demo_get_all_status()
        demo_toggle_module()
        demo_toggle_sub_feature()
        demo_parent_module_dependency()
        
        print("\n" + "="*80)
        print(" ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nNext steps:")
        print("1. Use the admin UI to manage module features")
        print("2. Integrate module checks into your API endpoints")
        print("3. Use frontend hooks to conditionally render features")
        print("4. See MODULE_FEATURES_GUIDE.md for detailed documentation")
        
    except Exception as e:
        print(f"\n Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
