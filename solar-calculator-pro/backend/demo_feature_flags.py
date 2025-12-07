"""
Feature Flag System Demo

This script demonstrates the feature flag system functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base
from backend.services.feature_flag_service import FeatureFlagService
from backend.models.feature_flag_schemas import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagType,
    RoleCreate
)


# Setup database
DATABASE_URL = "sqlite:///./demo_feature_flags.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_global_flags():
    """Demonstrate global feature flags"""
    print_section("1. Global Feature Flags")
    
    db = SessionLocal()
    service = FeatureFlagService(db)
    
    try:
        # Create a global flag
        print("Creating global feature flag...")
        flag_data = FeatureFlagCreate(
            key="solar.advanced_features",
            name="Advanced Solar Features",
            description="Enable advanced solar calculation features",
            enabled=True,
            flag_type=FeatureFlagType.GLOBAL
        )
        
        flag = service.create_feature_flag(flag_data)
        print(f" Created flag: {flag.key}")
        print(f"   Name: {flag.name}")
        print(f"   Enabled: {flag.enabled}")
        print(f"   Type: {flag.flag_type}")
        
        # Check if feature is enabled
        print("\nChecking if feature is enabled...")
        result = service.is_feature_enabled("solar.advanced_features")
        print(f" Feature enabled: {result.enabled}")
        print(f"   Reason: {result.reason}")
        
        # Disable the flag
        print("\nDisabling the flag...")
        update_data = FeatureFlagUpdate(enabled=False)
        updated_flag = service.update_feature_flag(flag.id, update_data)
        print(f" Flag disabled: {updated_flag.enabled}")
        
        # Check again
        result = service.is_feature_enabled("solar.advanced_features")
        print(f" Feature enabled: {result.enabled}")
        print(f"   Reason: {result.reason}")
        
    finally:
        db.close()


def demo_percentage_rollout():
    """Demonstrate percentage rollout flags"""
    print_section("2. Percentage Rollout Flags")
    
    db = SessionLocal()
    service = FeatureFlagService(db)
    
    try:
        # Create a percentage rollout flag
        print("Creating percentage rollout flag (50%)...")
        flag_data = FeatureFlagCreate(
            key="experiment.new_ui",
            name="New UI Experiment",
            description="Gradual rollout of new UI",
            enabled=True,
            flag_type=FeatureFlagType.PERCENTAGE,
            rollout_percentage=50
        )
        
        flag = service.create_feature_flag(flag_data)
        print(f" Created flag: {flag.key}")
        print(f"   Rollout: {flag.rollout_percentage}%")
        
        # Check for multiple users
        print("\nChecking for 10 different users...")
        enabled_count = 0
        for user_id in range(1, 11):
            result = service.is_feature_enabled("experiment.new_ui", user_id)
            status = " Enabled" if result.enabled else " Disabled"
            print(f"   User {user_id:2d}: {status}")
            if result.enabled:
                enabled_count += 1
        
        print(f"\n {enabled_count}/10 users have feature enabled (~{enabled_count*10}%)")
        
        # Update rollout percentage
        print("\nIncreasing rollout to 75%...")
        update_data = FeatureFlagUpdate(rollout_percentage=75)
        service.update_feature_flag(flag.id, update_data)
        
        enabled_count = 0
        for user_id in range(1, 11):
            result = service.is_feature_enabled("experiment.new_ui", user_id)
            if result.enabled:
                enabled_count += 1
        
        print(f" {enabled_count}/10 users have feature enabled (~{enabled_count*10}%)")
        
    finally:
        db.close()


def demo_role_based_flags():
    """Demonstrate role-based feature flags"""
    print_section("3. Role-Based Feature Flags")
    
    db = SessionLocal()
    service = FeatureFlagService(db)
    
    try:
        # Create roles
        print("Creating roles...")
        admin_role = service.create_role(RoleCreate(
            name="admin",
            description="Administrator role"
        ))
        print(f" Created role: {admin_role.name}")
        
        beta_role = service.create_role(RoleCreate(
            name="beta_tester",
            description="Beta tester role"
        ))
        print(f" Created role: {beta_role.name}")
        
        # Create role-based flag
        print("\nCreating role-based feature flag...")
        flag_data = FeatureFlagCreate(
            key="admin.advanced_settings",
            name="Advanced Admin Settings",
            description="Advanced settings for administrators",
            enabled=True,
            flag_type=FeatureFlagType.ROLE,
            role_ids=[admin_role.id]
        )
        
        flag = service.create_feature_flag(flag_data)
        print(f" Created flag: {flag.key}")
        print(f"   Allowed roles: {[role.name for role in flag.roles]}")
        
    finally:
        db.close()


def demo_bulk_check():
    """Demonstrate bulk feature flag checking"""
    print_section("4. Bulk Feature Flag Checking")
    
    db = SessionLocal()
    service = FeatureFlagService(db)
    
    try:
        # Create multiple flags
        print("Creating multiple feature flags...")
        flags_to_create = [
            ("pdf.new_templates", "New PDF Templates", True),
            ("crm.forecasting", "CRM Forecasting", True),
            ("3d.advanced_rendering", "Advanced 3D Rendering", False),
        ]
        
        for key, name, enabled in flags_to_create:
            flag_data = FeatureFlagCreate(
                key=key,
                name=name,
                enabled=enabled,
                flag_type=FeatureFlagType.GLOBAL
            )
            service.create_feature_flag(flag_data)
            print(f" Created: {key} (enabled={enabled})")
        
        # Check all flags at once
        print("\nChecking all flags at once...")
        keys = [key for key, _, _ in flags_to_create]
        results = service.check_multiple_features(keys)
        
        print("\nResults:")
        for key, enabled in results.items():
            status = " Enabled" if enabled else " Disabled"
            print(f"   {key}: {status}")
        
    finally:
        db.close()


def demo_caching():
    """Demonstrate caching behavior"""
    print_section("5. Caching Behavior")
    
    db = SessionLocal()
    service = FeatureFlagService(db)
    
    try:
        # Create a flag
        print("Creating feature flag...")
        flag_data = FeatureFlagCreate(
            key="cache.test",
            name="Cache Test",
            enabled=True,
            flag_type=FeatureFlagType.GLOBAL
        )
        
        flag = service.create_feature_flag(flag_data)
        print(f" Created flag: {flag.key}")
        
        # Check multiple times (should use cache)
        print("\nChecking flag 5 times (should use cache)...")
        import time
        for i in range(5):
            start = time.time()
            result = service.is_feature_enabled("cache.test")
            elapsed = (time.time() - start) * 1000
            print(f"   Check {i+1}: {elapsed:.2f}ms - Enabled: {result.enabled}")
        
        # Update flag (should clear cache)
        print("\nUpdating flag (clears cache)...")
        update_data = FeatureFlagUpdate(enabled=False)
        service.update_feature_flag(flag.id, update_data)
        
        # Check again
        result = service.is_feature_enabled("cache.test")
        print(f" After update - Enabled: {result.enabled}")
        
    finally:
        db.close()


def demo_list_and_search():
    """Demonstrate listing and searching flags"""
    print_section("6. Listing and Searching Flags")
    
    db = SessionLocal()
    service = FeatureFlagService(db)
    
    try:
        # List all flags
        print("Listing all feature flags...")
        flags = service.list_feature_flags()
        
        print(f"\n Total flags: {len(flags)}\n")
        
        for flag in flags:
            status = "" if flag.enabled else ""
            print(f"{status} {flag.key}")
            print(f"   Name: {flag.name}")
            print(f"   Type: {flag.flag_type}")
            if flag.flag_type == "percentage":
                print(f"   Rollout: {flag.rollout_percentage}%")
            print()
        
    finally:
        db.close()


def cleanup():
    """Clean up demo database"""
    print_section("Cleanup")
    
    print("Removing demo database...")
    if os.path.exists("demo_feature_flags.db"):
        os.remove("demo_feature_flags.db")
        print(" Demo database removed")
    else:
        print("ℹ  No demo database to remove")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("  FEATURE FLAG SYSTEM DEMO")
    print("=" * 60)
    
    try:
        demo_global_flags()
        demo_percentage_rollout()
        demo_role_based_flags()
        demo_bulk_check()
        demo_caching()
        demo_list_and_search()
        
        print("\n" + "=" * 60)
        print("  DEMO COMPLETE!")
        print("=" * 60)
        print("\n All demos completed successfully!")
        print("\n For more information, see:")
        print("   - backend/docs/FEATURE_FLAGS_GUIDE.md")
        print("   - backend/docs/FEATURE_FLAGS_QUICK_REFERENCE.md")
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ask if user wants to clean up
        print("\n" + "-" * 60)
        response = input("Remove demo database? (y/n): ")
        if response.lower() == 'y':
            cleanup()
        else:
            print("ℹ  Demo database kept at: demo_feature_flags.db")


if __name__ == '__main__':
    main()
