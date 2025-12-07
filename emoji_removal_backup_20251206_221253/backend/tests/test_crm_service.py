"""
Tests for CRM Service

This file contains tests for the CRM service functionality.
"""

import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.crm_service import get_crm_service


def test_service_initialization():
    """Test that the CRM service initializes correctly"""
    print("\n=== Testing Service Initialization ===")
    
    service = get_crm_service()
    assert service is not None, "Service should not be None"
    assert service.is_initialized, "Service should be initialized"
    
    health = service.health_check()
    print(f"Service health: {health.status}")
    print(f"Message: {health.message}")
    
    print("✓ Service initialization test passed")


def test_customer_management():
    """Test customer CRUD operations"""
    print("\n=== Testing Customer Management ===")
    
    service = get_crm_service()
    
    # Create customer
    customer_data = {
        "first_name": "Test",
        "last_name": "Customer",
        "email": "test@example.com",
        "company_name": "Test Company"
    }
    
    try:
        customer = service.create_customer(customer_data)
        print(f"✓ Created customer ID: {customer['id']}")
        customer_id = customer['id']
        
        # Get customer
        retrieved = service.get_customer(customer_id)
        assert retrieved is not None, "Customer should be retrieved"
        assert retrieved['first_name'] == "Test", "First name should match"
        print(f"✓ Retrieved customer: {retrieved['first_name']} {retrieved['last_name']}")
        
        # Update customer
        update_data = {"email": "updated@example.com"}
        updated = service.update_customer(customer_id, update_data)
        assert updated['email'] == "updated@example.com", "Email should be updated"
        print(f"✓ Updated customer email to: {updated['email']}")
        
        # List customers
        customers = service.list_customers(limit=10)
        assert len(customers) > 0, "Should have at least one customer"
        print(f"✓ Listed {len(customers)} customers")
        
        # Search customers
        search_results = service.list_customers(search="Test")
        assert len(search_results) > 0, "Should find test customer"
        print(f"✓ Search found {len(search_results)} customers")
        
        # Delete customer
        success = service.delete_customer(customer_id)
        assert success, "Customer should be deleted"
        print(f"✓ Deleted customer ID: {customer_id}")
        
    except Exception as e:
        print(f"✗ Customer management test failed: {e}")
        raise


def test_task_management():
    """Test task CRUD operations"""
    print("\n=== Testing Task Management ===")
    
    service = get_crm_service()
    
    # Create task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "open",
        "priority": "high",
        "due_date": date.today() + timedelta(days=7)
    }
    
    try:
        task_id = service.create_task(task_data)
        assert task_id is not None, "Task ID should not be None"
        print(f"✓ Created task ID: {task_id}")
        
        # Get task
        task = service.get_task(task_id)
        assert task is not None, "Task should be retrieved"
        assert task['title'] == "Test Task", "Title should match"
        print(f"✓ Retrieved task: {task['title']}")
        
        # Update task
        update_data = {"status": "in_progress", "priority": "medium"}
        success = service.update_task(task_id, update_data)
        assert success, "Task should be updated"
        
        updated_task = service.get_task(task_id)
        assert updated_task['status'] == "in_progress", "Status should be updated"
        print(f"✓ Updated task status to: {updated_task['status']}")
        
        # List tasks
        tasks = service.list_tasks()
        assert len(tasks) > 0, "Should have at least one task"
        print(f"✓ Listed {len(tasks)} tasks")
        
        # Mark as completed
        success = service.mark_task_completed(task_id)
        assert success, "Task should be marked as completed"
        
        completed_task = service.get_task(task_id)
        assert completed_task['status'] == "completed", "Status should be completed"
        print(f"✓ Marked task as completed")
        
        # Get statistics
        stats = service.get_task_statistics()
        print(f"✓ Task statistics: {stats['total']} total, {stats['overdue']} overdue")
        
        # Delete task
        success = service.delete_task(task_id)
        assert success, "Task should be deleted"
        print(f"✓ Deleted task ID: {task_id}")
        
    except Exception as e:
        print(f"✗ Task management test failed: {e}")
        raise


def test_activity_management():
    """Test activity/note CRUD operations"""
    print("\n=== Testing Activity Management ===")
    
    service = get_crm_service()
    
    # First create a customer for the activity
    customer_data = {
        "first_name": "Activity",
        "last_name": "Test",
        "email": "activity@example.com"
    }
    
    try:
        customer = service.create_customer(customer_data)
        customer_id = customer['id']
        print(f"✓ Created test customer ID: {customer_id}")
        
        # Create activity
        activity_data = {
            "customer_id": customer_id,
            "activity_type": "note",
            "title": "Test Note",
            "content": "This is a test note",
            "is_important": True
        }
        
        activity_id = service.create_activity(activity_data)
        assert activity_id is not None, "Activity ID should not be None"
        print(f"✓ Created activity ID: {activity_id}")
        
        # Get activity
        activity = service.get_activity(activity_id)
        assert activity is not None, "Activity should be retrieved"
        assert activity['title'] == "Test Note", "Title should match"
        print(f"✓ Retrieved activity: {activity['title']}")
        
        # Update activity
        update_data = {"is_important": False, "content": "Updated content"}
        success = service.update_activity(activity_id, update_data)
        assert success, "Activity should be updated"
        
        updated_activity = service.get_activity(activity_id)
        assert updated_activity['is_important'] == False, "Important flag should be updated"
        print(f"✓ Updated activity")
        
        # Get customer activities
        activities = service.get_customer_activities(customer_id)
        assert len(activities) > 0, "Should have at least one activity"
        print(f"✓ Listed {len(activities)} activities for customer")
        
        # Search activities
        search_results = service.search_activities("Test", customer_id=customer_id)
        assert len(search_results) > 0, "Should find test activity"
        print(f"✓ Search found {len(search_results)} activities")
        
        # Get statistics
        stats = service.get_activity_statistics(customer_id)
        print(f"✓ Activity statistics: {stats['total']} total")
        
        # Delete activity
        success = service.delete_activity(activity_id)
        assert success, "Activity should be deleted"
        print(f"✓ Deleted activity ID: {activity_id}")
        
        # Clean up customer
        service.delete_customer(customer_id)
        print(f"✓ Cleaned up test customer")
        
    except Exception as e:
        print(f"✗ Activity management test failed: {e}")
        raise


def test_offer_tracking():
    """Test offer tracking functionality"""
    print("\n=== Testing Offer Tracking ===")
    
    service = get_crm_service()
    
    try:
        # Get offer statistics
        stats = service.get_offer_statistics()
        print(f"✓ Offer statistics: {stats['total_offers']} total offers")
        print(f"  - Draft: {stats['draft']}")
        print(f"  - Sent: {stats['sent']}")
        print(f"  - Accepted: {stats['accepted']}")
        print(f"  - Rejected: {stats['rejected']}")
        print(f"  - Conversion rate: {stats['conversion_rate']:.2f}%")
        
        # List all offers
        offers = service.list_offers()
        print(f"✓ Listed {len(offers)} offers")
        
        # Get pending follow-ups
        follow_ups = service.get_pending_follow_ups()
        print(f"✓ Found {len(follow_ups)} pending follow-ups")
        
    except Exception as e:
        print(f"✗ Offer tracking test failed: {e}")
        raise


def run_all_tests():
    """Run all CRM service tests"""
    print("=" * 60)
    print("CRM Service Test Suite")
    print("=" * 60)
    
    try:
        test_service_initialization()
        test_customer_management()
        test_task_management()
        test_activity_management()
        test_offer_tracking()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Test suite failed: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    run_all_tests()
