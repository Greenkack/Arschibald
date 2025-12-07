"""
Result History System - Demo Script

Demonstrates all features of the result history and comparison system.
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.services.result_history_service import ResultHistoryService
from backend.models.result_history_schemas import (
    ResultHistoryCreate, ResultHistoryUpdate, ResultSearchRequest,
    ResultComparisonCreate, ResultShareCreate, ResultType, ComparisonType
)


def demo_create_results(service: ResultHistoryService, user_id: int):
    """Demo: Create sample results"""
    print("\n" + "="*80)
    print("DEMO 1: Creating Sample Results")
    print("="*80)
    
    # Create solar result
    solar_data = ResultHistoryCreate(
        result_type=ResultType.SOLAR,
        result_name="Residential Solar System - 10kW",
        description="Initial calculation for Smith residence",
        input_data={
            "roof_area": 50,
            "roof_type": "flat",
            "roof_angle": 30,
            "orientation": "south",
            "module_type": "premium",
            "annual_consumption": 4000
        },
        output_data={
            "system_size": 10.5,
            "module_count": 30,
            "annual_production": 12000,
            "self_consumption_rate": 0.75,
            "payback_period": 8.5,
            "total_cost": 25000,
            "savings_25_years": 45000,
            "co2_savings": 150
        },
        tags=["residential", "10kw", "smith", "premium"]
    )
    
    result1 = service.create_result(user_id, solar_data)
    print(f"✓ Created solar result: {result1.result_name} (ID: {result1.id})")
    
    # Create heat pump result
    heatpump_data = ResultHistoryCreate(
        result_type=ResultType.HEATPUMP,
        result_name="Heat Pump System - 12kW",
        description="Heat pump calculation for Johnson residence",
        input_data={
            "building_area": 150,
            "insulation_quality": "good",
            "heating_demand": 12000,
            "climate_zone": "temperate"
        },
        output_data={
            "heat_pump_size": 12,
            "cop": 4.2,
            "annual_heating_cost": 800,
            "savings_vs_gas": 1200,
            "payback_period": 7.5,
            "total_cost": 18000
        },
        tags=["residential", "heatpump", "johnson", "12kw"]
    )
    
    result2 = service.create_result(user_id, heatpump_data)
    print(f"✓ Created heat pump result: {result2.result_name} (ID: {result2.id})")
    
    # Create combined result
    combined_data = ResultHistoryCreate(
        result_type=ResultType.COMBINED,
        result_name="Combined Solar + Heat Pump - Williams",
        description="Combined system for maximum efficiency",
        input_data={
            "solar_system_size": 15,
            "heat_pump_size": 10,
            "building_area": 200
        },
        output_data={
            "total_system_size": 25,
            "combined_savings": 3500,
            "synergy_bonus": 500,
            "payback_period": 6.8,
            "total_cost": 40000
        },
        tags=["residential", "combined", "williams", "premium"]
    )
    
    result3 = service.create_result(user_id, combined_data)
    print(f"✓ Created combined result: {result3.result_name} (ID: {result3.id})")
    
    return [result1.id, result2.id, result3.id]


def demo_search_and_filter(service: ResultHistoryService, user_id: int):
    """Demo: Search and filter results"""
    print("\n" + "="*80)
    print("DEMO 2: Searching and Filtering Results")
    print("="*80)
    
    # Search by query
    search1 = ResultSearchRequest(
        query="residential",
        page=1,
        page_size=10
    )
    results1, total1 = service.search_results(user_id, search1)
    print(f"\n✓ Search 'residential': Found {total1} results")
    for r in results1:
        print(f"  - {r.result_name} ({r.result_type})")
    
    # Filter by type
    search2 = ResultSearchRequest(
        result_type=ResultType.SOLAR,
        page=1,
        page_size=10
    )
    results2, total2 = service.search_results(user_id, search2)
    print(f"\n✓ Filter by type 'solar': Found {total2} results")
    
    # Filter by tags
    search3 = ResultSearchRequest(
        tags=["premium"],
        page=1,
        page_size=10
    )
    results3, total3 = service.search_results(user_id, search3)
    print(f"\n✓ Filter by tag 'premium': Found {total3} results")
    
    # Get favorites
    favorites = service.get_favorites(user_id, limit=10)
    print(f"\n✓ Favorites: {len(favorites)} results")
    
    # Get recent
    recent = service.get_recent_results(user_id, limit=5)
    print(f"\n✓ Recent results: {len(recent)} results")
    for r in recent:
        print(f"  - {r.result_name} (created: {r.created_at})")


def demo_update_and_organize(service: ResultHistoryService, user_id: int, result_id: int):
    """Demo: Update and organize results"""
    print("\n" + "="*80)
    print("DEMO 3: Updating and Organizing Results")
    print("="*80)
    
    # Mark as favorite
    update1 = ResultHistoryUpdate(
        is_favorite=True
    )
    result = service.update_result(result_id, user_id, update1)
    print(f"✓ Marked as favorite: {result.result_name}")
    
    # Add more tags
    update2 = ResultHistoryUpdate(
        tags=["residential", "10kw", "smith", "premium", "approved", "2024"]
    )
    result = service.update_result(result_id, user_id, update2)
    print(f"✓ Updated tags: {[tag.tag_name for tag in result.tags]}")
    
    # Update description
    update3 = ResultHistoryUpdate(
        description="Updated calculation with final approval from customer"
    )
    result = service.update_result(result_id, user_id, update3)
    print(f"✓ Updated description: {result.description}")


def demo_versioning(service: ResultHistoryService, user_id: int, result_id: int):
    """Demo: Result versioning"""
    print("\n" + "="*80)
    print("DEMO 4: Result Versioning")
    print("="*80)
    
    # Get original result
    original = service.get_result(result_id, user_id)
    print(f"\n✓ Original result: {original.result_name} (v{original.version})")
    
    # Create version 2
    version2_data = ResultHistoryCreate(
        result_type=ResultType.SOLAR,
        result_name="Residential Solar System - 10kW (v2)",
        description="Updated with new premium modules",
        input_data=original.input_data,
        output_data={
            **original.output_data,
            "system_size": 11.0,
            "total_cost": 27000,
            "module_count": 32
        },
        tags=["residential", "10kw", "smith", "premium", "v2"]
    )
    
    version2 = service.create_version(result_id, user_id, version2_data)
    print(f"✓ Created version 2: {version2.result_name} (v{version2.version})")
    
    # Create version 3
    version3_data = ResultHistoryCreate(
        result_type=ResultType.SOLAR,
        result_name="Residential Solar System - 10kW (v3)",
        description="Final version with battery storage",
        input_data=original.input_data,
        output_data={
            **version2.output_data,
            "system_size": 11.5,
            "total_cost": 32000,
            "battery_included": True
        },
        tags=["residential", "10kw", "smith", "premium", "v3", "battery"]
    )
    
    version3 = service.create_version(version2.id, user_id, version3_data)
    print(f"✓ Created version 3: {version3.result_name} (v{version3.version})")
    
    # Get version tree
    tree = service.get_version_tree(version2.id, user_id)
    print(f"\n✓ Version tree:")
    print(f"  - Root: {tree['current'].result_name} (v{tree['current'].version})")
    if tree['parent']:
        print(f"  - Parent: {tree['parent'].result_name} (v{tree['parent'].version})")
    print(f"  - Children: {len(tree['children'])} versions")
    print(f"  - All versions: {len(tree['all_versions'])} total")


def demo_comparison(service: ResultHistoryService, user_id: int, result_ids: list):
    """Demo: Result comparison"""
    print("\n" + "="*80)
    print("DEMO 5: Result Comparison")
    print("="*80)
    
    # Temporary comparison
    comparison_data = service.compare_results(
        result_ids=result_ids[:2],
        user_id=user_id,
        metrics=["total_cost", "payback_period"]
    )
    
    print(f"\n✓ Comparing {len(comparison_data['results'])} results:")
    for r in comparison_data['results']:
        print(f"  - {r.result_name}")
    
    print(f"\n✓ Differences:")
    for metric, data in comparison_data['differences'].items():
        print(f"  - {metric}:")
        print(f"    Values: {data['values']}")
        if data['min'] is not None:
            print(f"    Range: {data['min']} - {data['max']} (avg: {data['avg']:.2f})")
    
    print(f"\n✓ Summary:")
    print(f"  - Result count: {comparison_data['summary']['result_count']}")
    print(f"  - Result types: {comparison_data['summary']['result_types']}")
    print(f"  - Metrics compared: {comparison_data['summary']['metrics_compared']}")
    print(f"  - Significant differences: {comparison_data['summary']['significant_differences']}")
    
    # Save comparison
    saved_comparison_data = ResultComparisonCreate(
        comparison_name="Solar vs Heat Pump Cost Analysis",
        description="Comparing costs and payback periods",
        result_ids=result_ids[:2],
        comparison_type=ComparisonType.SIDE_BY_SIDE,
        metrics_to_compare=["total_cost", "payback_period"]
    )
    
    saved_comparison = service.create_comparison(user_id, saved_comparison_data)
    print(f"\n✓ Saved comparison: {saved_comparison.comparison_name} (ID: {saved_comparison.id})")
    
    # Get all comparisons
    comparisons = service.get_comparisons(user_id)
    print(f"\n✓ Total saved comparisons: {len(comparisons)}")


def demo_sharing(service: ResultHistoryService, user_id: int, result_id: int):
    """Demo: Result sharing"""
    print("\n" + "="*80)
    print("DEMO 6: Result Sharing")
    print("="*80)
    
    # Create public share
    share1_data = ResultShareCreate(
        result_id=result_id,
        is_public=True,
        can_edit=False,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    share1 = service.create_share(user_id, share1_data)
    print(f"\n✓ Created public share:")
    print(f"  - Token: {share1.share_token}")
    print(f"  - URL: https://app.example.com/shared/{share1.share_token}")
    print(f"  - Expires: {share1.expires_at}")
    
    # Create private share
    share2_data = ResultShareCreate(
        result_id=result_id,
        shared_with_user_id=2,  # Share with specific user
        is_public=False,
        can_edit=True,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    share2 = service.create_share(user_id, share2_data)
    print(f"\n✓ Created private share:")
    print(f"  - Shared with user ID: {share2.shared_with_user_id}")
    print(f"  - Can edit: {share2.can_edit}")
    print(f"  - Expires: {share2.expires_at}")
    
    # Get all shares for result
    shares = service.get_shares_for_result(result_id, user_id)
    print(f"\n✓ Total shares for this result: {len(shares)}")


def demo_statistics(service: ResultHistoryService, user_id: int):
    """Demo: Statistics"""
    print("\n" + "="*80)
    print("DEMO 7: Statistics and Analytics")
    print("="*80)
    
    stats = service.get_statistics(user_id)
    
    print(f"\n✓ Overall Statistics:")
    print(f"  - Total results: {stats['total_results']}")
    print(f"  - Favorites: {stats['favorite_count']}")
    print(f"  - Archived: {stats['archived_count']}")
    
    print(f"\n✓ Results by Type:")
    for result_type, count in stats['results_by_type'].items():
        print(f"  - {result_type}: {count}")
    
    print(f"\n✓ Recent Results:")
    for r in stats['recent_results'][:3]:
        print(f"  - {r.result_name} ({r.created_at})")
    
    print(f"\n✓ Tag Usage:")
    for tag, count in sorted(stats['tags_usage'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {tag}: {count} results")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("RESULT HISTORY AND COMPARISON SYSTEM - COMPLETE DEMO")
    print("="*80)
    
    # Create database session
    db = SessionLocal()
    service = ResultHistoryService(db)
    
    # Use test user ID
    user_id = 1
    
    try:
        # Demo 1: Create results
        result_ids = demo_create_results(service, user_id)
        
        # Demo 2: Search and filter
        demo_search_and_filter(service, user_id)
        
        # Demo 3: Update and organize
        demo_update_and_organize(service, user_id, result_ids[0])
        
        # Demo 4: Versioning
        demo_versioning(service, user_id, result_ids[0])
        
        # Demo 5: Comparison
        demo_comparison(service, user_id, result_ids)
        
        # Demo 6: Sharing
        demo_sharing(service, user_id, result_ids[0])
        
        # Demo 7: Statistics
        demo_statistics(service, user_id)
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nAll features demonstrated:")
        print("✓ Result creation and storage")
        print("✓ Search and filtering")
        print("✓ Update and organization")
        print("✓ Version tracking")
        print("✓ Result comparison")
        print("✓ Secure sharing")
        print("✓ Statistics and analytics")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
