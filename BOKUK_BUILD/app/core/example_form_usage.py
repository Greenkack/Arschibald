"""Example usage of Form State Management with Undo/Redo

This file demonstrates how to use the form management system in various scenarios.
"""


from .database import init_database
from .form_manager import (
    create_form,
    get_form_manager,
    get_form_validator,
    init_form_tables,
    redo_form,
    reset_form,
    save_form_now,
    undo_form,
    update_form_field,
    validate_form,
)


def example_basic_usage():
    """Example: Basic form usage"""
    print("\n=== Basic Form Usage ===\n")

    # Create a form
    form_state = create_form(
        form_id="user_profile",
        session_id="session_123",
        user_id="user_456",
        initial_data={
            "name": "",
            "email": "",
            "age": 0
        }
    )

    print(f"Created form: {form_state.form_id}")
    print(f"Initial data: {form_state.data}")

    # Update fields
    update_form_field("user_profile", "session_123", "name", "John Doe")
    update_form_field(
        "user_profile",
        "session_123",
        "email",
        "john@example.com")
    update_form_field("user_profile", "session_123", "age", 30)

    # Get updated form
    manager = get_form_manager()
    form_state = manager.get_form("user_profile", "session_123")
    print(f"\nUpdated data: {form_state.data}")

    # Save form
    if save_form_now("user_profile", "session_123"):
        print("Form saved successfully!")


def example_undo_redo():
    """Example: Undo/Redo functionality"""
    print("\n=== Undo/Redo Example ===\n")

    manager = get_form_manager()

    # Create form
    create_form("document", "session_123", initial_data={"content": ""})

    # Make several changes
    changes = [
        "Hello",
        "Hello World",
        "Hello World!",
        "Hello World! This is a test.",
        "Hello World! This is a test. Final version."
    ]

    for i, content in enumerate(changes):
        update_form_field("document", "session_123", "content", content)
        print(f"Change {i + 1}: {content}")

    # Undo changes
    print("\n--- Undoing changes ---")
    for i in range(3):
        if manager.can_undo("document", "session_123"):
            undo_form("document", "session_123")
            form_state = manager.get_form("document", "session_123")
            print(f"After undo {i + 1}: {form_state.data['content']}")

    # Redo changes
    print("\n--- Redoing changes ---")
    for i in range(2):
        if manager.can_redo("document", "session_123"):
            redo_form("document", "session_123")
            form_state = manager.get_form("document", "session_123")
            print(f"After redo {i + 1}: {form_state.data['content']}")


def example_validation():
    """Example: Form validation"""
    print("\n=== Validation Example ===\n")

    validator = get_form_validator()

    # Register validators
    def validate_email(value):
        if not value:
            return False, "Email is required"
        if "@" not in value or "." not in value:
            return False, "Invalid email format"
        return True, None

    def validate_age(value):
        if not isinstance(value, (int, float)):
            return False, "Age must be a number"
        if value < 0:
            return False, "Age cannot be negative"
        if value > 150:
            return False, "Age seems unrealistic"
        return True, None

    def validate_name(value):
        if not value or not value.strip():
            return False, "Name is required"
        if len(value) < 2:
            return False, "Name must be at least 2 characters"
        return True, None

    # Register field validators
    validator.register_validator("registration", "email", validate_email)
    validator.register_validator("registration", "age", validate_age)
    validator.register_validator("registration", "name", validate_name)

    # Register form-level validator
    def validate_terms_accepted(data):
        if not data.get("terms_accepted"):
            return False, {"terms_accepted": ["You must accept the terms"]}
        return True, {}

    validator.register_form_validator("registration", validate_terms_accepted)

    # Test with invalid data
    print("Testing with invalid data:")
    create_form("registration", "session_123", initial_data={
        "name": "J",  # Too short
        "email": "invalid",  # Invalid format
        "age": -5,  # Negative
        "terms_accepted": False
    })

    result = validate_form("registration", "session_123")
    if not result.is_valid:
        print("Validation failed:")
        for field, errors in result.errors.items():
            for error in errors:
                print(f"  - {field}: {error}")

    # Test with valid data
    print("\nTesting with valid data:")
    manager = get_form_manager()
    manager.update_multiple("registration", "session_123", {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "terms_accepted": True
    })

    result = validate_form("registration", "session_123")
    if result.is_valid:
        print("Validation passed!")


def example_snapshots():
    """Example: Manual snapshots"""
    print("\n=== Snapshots Example ===\n")

    manager = get_form_manager()

    # Create form
    create_form("project", "session_123", initial_data={
        "title": "My Project",
        "description": "",
        "status": "draft"
    })

    # Create checkpoint before major changes
    snapshot1 = manager.create_snapshot(
        form_id="project",
        session_id="session_123",
        description="Initial version",
        snapshot_type="checkpoint"
    )
    print(f"Created checkpoint: {snapshot1.description}")

    # Make changes
    manager.update_field(
        "project",
        "session_123",
        "description",
        "A great project")
    manager.update_field("project", "session_123", "status", "in_progress")

    # Create another checkpoint
    snapshot2 = manager.create_snapshot(
        form_id="project",
        session_id="session_123",
        description="After initial edits",
        snapshot_type="checkpoint"
    )
    print(f"Created checkpoint: {snapshot2.description}")

    # Make more changes
    manager.update_field(
        "project",
        "session_123",
        "description",
        "An amazing project!")
    manager.update_field("project", "session_123", "status", "completed")

    # View snapshot history
    print("\nSnapshot history:")
    history = manager.get_snapshot_history("project", "session_123")
    for i, snap in enumerate(history):
        print(
            f"  {i + 1}. {snap.timestamp.strftime('%H:%M:%S')} - {snap.description}")
        print(f"     Data: {snap.data}")

    # Restore first checkpoint
    print(f"\nRestoring snapshot: {snapshot1.description}")
    manager.restore_snapshot("project", "session_123", snapshot1.snapshot_id)

    form_state = manager.get_form("project", "session_123")
    print(f"Restored data: {form_state.data}")


def example_auto_save():
    """Example: Auto-save functionality"""
    print("\n=== Auto-Save Example ===\n")

    import time

    manager = get_form_manager()

    # Create form with auto-save enabled
    form_state = manager.get_form(
        form_id="notes",
        session_id="session_123",
        auto_save_enabled=True
    )

    print("Auto-save is enabled")
    print("Making changes...")

    # Make changes (will be auto-saved)
    manager.update_field("notes", "session_123", "title", "My Notes")

    # Check save status
    status = manager.get_save_status("notes")
    if status:
        print(f"Save status: {status['status']}")

    # Wait for auto-save to complete
    time.sleep(0.6)  # Wait for debounce

    status = manager.get_save_status("notes")
    if status:
        print(f"Save status after debounce: {status['status']}")

    # Make more changes
    manager.update_field(
        "notes",
        "session_123",
        "content",
        "This is my note content")

    # Force immediate save
    print("\nForcing immediate save...")
    manager.save("notes", "session_123", immediate=True)
    print("Saved immediately!")


def example_form_dependencies():
    """Example: Form dependencies"""
    print("\n=== Form Dependencies Example ===\n")

    manager = get_form_manager()

    # Create parent form
    parent = manager.get_form("order", "session_123")
    parent.data = {
        "order_id": "ORD-001",
        "customer": "John Doe",
        "total": 0
    }

    # Create child forms (order items)
    item1 = manager.get_form("order_item_1", "session_123")
    item1.data = {"product": "Widget", "price": 10.00, "quantity": 2}
    item1.add_dependency("order")

    item2 = manager.get_form("order_item_2", "session_123")
    item2.data = {"product": "Gadget", "price": 15.00, "quantity": 1}
    item2.add_dependency("order")

    # Add dependents to parent
    parent.add_dependent("order_item_1")
    parent.add_dependent("order_item_2")

    print(f"Parent form: {parent.form_id}")
    print(f"Dependents: {parent.dependents}")

    # Calculate total from items
    total = sum([
        item1.data["price"] * item1.data["quantity"],
        item2.data["price"] * item2.data["quantity"]
    ])

    parent.data["total"] = total
    print(f"\nOrder total: ${total:.2f}")

    # When parent changes, update dependents
    print("\nUpdating customer name...")
    parent.data["customer"] = "Jane Smith"

    # Notify dependents (in real app, you'd implement this logic)
    print(f"Notifying {len(parent.dependents)} dependent forms")


def example_reset_form():
    """Example: Resetting form"""
    print("\n=== Reset Form Example ===\n")

    manager = get_form_manager()

    # Create form with data
    create_form("settings", "session_123", initial_data={
        "theme": "dark",
        "language": "en",
        "notifications": True
    })

    form_state = manager.get_form("settings", "session_123")
    print(f"Initial data: {form_state.data}")

    # Make changes
    manager.update_field("settings", "session_123", "theme", "light")
    manager.update_field("settings", "session_123", "language", "es")

    form_state = manager.get_form("settings", "session_123")
    print(f"Modified data: {form_state.data}")

    # Reset form
    print("\nResetting form...")
    reset_form("settings", "session_123")

    form_state = manager.get_form("settings", "session_123")
    print(f"After reset: {form_state.data}")


def example_complex_workflow():
    """Example: Complex workflow with all features"""
    print("\n=== Complex Workflow Example ===\n")

    manager = get_form_manager()
    validator = get_form_validator()

    # Set up validation
    def validate_required(value):
        if not value:
            return False, "This field is required"
        return True, None

    def validate_positive(value):
        if value <= 0:
            return False, "Must be positive"
        return True, None

    validator.register_validator("invoice", "client_name", validate_required)
    validator.register_validator("invoice", "amount", validate_required)
    validator.register_validator("invoice", "amount", validate_positive)

    # Create invoice form
    print("1. Creating invoice form...")
    create_form("invoice", "session_123", initial_data={
        "invoice_number": "INV-001",
        "client_name": "",
        "amount": 0,
        "status": "draft"
    })

    # Create checkpoint
    print("2. Creating initial checkpoint...")
    manager.create_snapshot(
        "invoice", "session_123",
        "Initial state",
        "checkpoint"
    )

    # Fill in form
    print("3. Filling in form data...")
    manager.update_field("invoice", "session_123", "client_name", "Acme Corp")
    manager.update_field("invoice", "session_123", "amount", 1500.00)

    # Validate
    print("4. Validating form...")
    result = validate_form("invoice", "session_123")
    if result.is_valid:
        print("   ✓ Validation passed")
    else:
        print("   ✗ Validation failed:", result.errors)

    # Create checkpoint before finalizing
    print("5. Creating checkpoint before finalizing...")
    manager.create_snapshot(
        "invoice", "session_123",
        "Before finalization",
        "checkpoint"
    )

    # Finalize
    print("6. Finalizing invoice...")
    manager.update_field("invoice", "session_123", "status", "finalized")

    # Save
    print("7. Saving invoice...")
    if manager.save("invoice", "session_123", immediate=True):
        print("   ✓ Saved successfully")

    # Show final state
    form_state = manager.get_form("invoice", "session_123")
    print("\n8. Final invoice state:")
    for key, value in form_state.data.items():
        print(f"   {key}: {value}")

    # Show snapshot history
    print("\n9. Snapshot history:")
    history = manager.get_snapshot_history("invoice", "session_123")
    for i, snap in enumerate(history):
        print(f"   {i + 1}. {snap.description} ({snap.snapshot_type})")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Form State Management Examples")
    print("=" * 60)

    # Initialize database
    init_database(auto_migrate=False)
    init_form_tables()

    # Run examples
    try:
        example_basic_usage()
        example_undo_redo()
        example_validation()
        example_snapshots()
        example_auto_save()
        example_form_dependencies()
        example_reset_form()
        example_complex_workflow()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
