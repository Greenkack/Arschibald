"""Example Usage of Enhanced Database Layer"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from core.database import (
    Base,
    Repository,
    UnitOfWork,
    get_audit_logs,
    get_db_manager,
    init_database,
    run_tx,
)


# Define your models
class Product(Base):
    """Product model with soft delete support"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # For soft delete


class Order(Base):
    """Order model"""
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


def example_basic_crud():
    """Example: Basic CRUD operations"""
    print("\n=== Basic CRUD Operations ===")

    # Initialize database
    init_database(auto_migrate=False)

    # Get database manager
    db_manager = get_db_manager()

    # Create repository
    product_repo = Repository(Product, db_manager, enable_audit=True)

    # Set audit context
    product_repo.set_context(
        user_id="user123",
        session_id="session456",
        correlation_id="req789"
    )

    # CREATE
    product = product_repo.create(
        name="Laptop",
        price=999.99,
        category="Electronics"
    )
    print(f"Created product: {product.id} - {product.name}")

    # READ
    retrieved = product_repo.get_by_id(product.id)
    print(f"Retrieved product: {retrieved.name} - ${retrieved.price}")

    # UPDATE
    updated = product_repo.update(product.id, price=899.99)
    print(f"Updated price: ${updated.price}")

    # SOFT DELETE
    product_repo.delete(product.id, soft=True)
    print(f"Soft deleted product: {product.id}")

    # RESTORE
    restored = product_repo.restore(product.id)
    print(f"Restored product: {restored.name}")

    # HARD DELETE
    product_repo.delete(product.id, soft=False)
    print(f"Hard deleted product: {product.id}")


def example_bulk_operations():
    """Example: Bulk operations for performance"""
    print("\n=== Bulk Operations ===")

    db_manager = get_db_manager()
    product_repo = Repository(Product, db_manager)

    # BULK CREATE
    products_data = [
        {"name": f"Product {i}", "price": 10.0 * i, "category": "Test"}
        for i in range(1, 11)
    ]

    products = product_repo.bulk_create(products_data)
    print(f"Bulk created {len(products)} products")

    # BULK UPDATE
    updates = [
        {"id": product.id, "price": product.price * 1.1}
        for product in products[:5]
    ]

    count = product_repo.bulk_update(updates)
    print(f"Bulk updated {count} products")

    # BULK DELETE
    ids = [product.id for product in products[5:]]
    count = product_repo.bulk_delete(ids, soft=True)
    print(f"Bulk deleted {count} products")


def example_unit_of_work():
    """Example: Using Unit of Work for transactions"""
    print("\n=== Unit of Work Pattern ===")

    db_manager = get_db_manager()

    # Simple transaction
    with UnitOfWork(db_manager, user_id="user123") as uow:
        product_repo = uow.get_repository(Product, enable_audit=True)
        order_repo = uow.get_repository(Order, enable_audit=True)

        # Create product
        product = product_repo.create(
            name="Mouse",
            price=29.99,
            category="Electronics"
        )

        # Create order
        order = order_repo.create(
            product_id=product.id,
            quantity=2,
            total=product.price * 2
        )

        print(f"Created product {product.id} and order {order.id}")

        # Transaction commits automatically on exit


def example_transaction_rollback():
    """Example: Transaction rollback on error"""
    print("\n=== Transaction Rollback ===")

    db_manager = get_db_manager()

    try:
        with UnitOfWork(db_manager) as uow:
            product_repo = uow.get_repository(Product)

            # Create product
            product = product_repo.create(
                name="Will Rollback",
                price=99.99,
                category="Test"
            )
            print(f"Created product: {product.id}")

            # Simulate error
            raise Exception("Something went wrong!")

    except Exception as e:
        print(f"Error occurred: {e}")
        print("Transaction rolled back - product not saved")


def example_nested_transactions():
    """Example: Nested transactions with savepoints"""
    print("\n=== Nested Transactions ===")

    db_manager = get_db_manager()

    with UnitOfWork(db_manager) as uow1:
        product_repo = uow1.get_repository(Product)

        # Outer transaction
        product1 = product_repo.create(
            name="Outer Product",
            price=100.0,
            category="Test"
        )
        print(f"Created outer product: {product1.id}")

        try:
            with UnitOfWork(db_manager) as uow2:
                # Inner transaction (uses savepoint)
                product2 = product_repo.create(
                    name="Inner Product",
                    price=200.0,
                    category="Test"
                )
                print(f"Created inner product: {product2.id}")

                # Simulate error in inner transaction
                raise Exception("Inner transaction error")

        except Exception as e:
            print(f"Inner transaction failed: {e}")
            print("Inner transaction rolled back, outer continues")

        # Outer transaction continues
        print(f"Outer product {product1.id} still exists")


def example_run_tx_helper():
    """Example: Using run_tx helper function"""
    print("\n=== run_tx Helper Function ===")

    def create_product_and_order(uow: UnitOfWork):
        """Business logic function"""
        product_repo = uow.get_repository(Product)
        order_repo = uow.get_repository(Order)

        # Create product
        product = product_repo.create(
            name="Keyboard",
            price=79.99,
            category="Electronics"
        )

        # Create order
        order = order_repo.create(
            product_id=product.id,
            quantity=1,
            total=product.price
        )

        return {"product": product, "order": order}

    # Run in transaction with audit context
    result = run_tx(
        create_product_and_order,
        user_id="user123",
        session_id="session456",
        correlation_id="req789"
    )

    print(
        f"Created product {
            result['product'].id} and order {
            result['order'].id}")


def example_pagination():
    """Example: Pagination"""
    print("\n=== Pagination ===")

    db_manager = get_db_manager()
    product_repo = Repository(Product, db_manager)

    # Create test data
    product_repo.bulk_create([
        {"name": f"Product {i}", "price": 10.0 * i, "category": "Test"}
        for i in range(1, 26)
    ])

    # Get first page
    page1 = product_repo.paginate(page=1, page_size=10)
    print(f"Page 1: {len(page1['items'])} items")
    print(f"Total: {page1['total']} items, {page1['total_pages']} pages")

    # Get second page
    page2 = product_repo.paginate(page=2, page_size=10)
    print(f"Page 2: {len(page2['items'])} items")

    # Filter by category
    page3 = product_repo.paginate(page=1, page_size=10, category="Test")
    print(f"Filtered page: {len(page3['items'])} items")


def example_audit_logs():
    """Example: Querying audit logs"""
    print("\n=== Audit Logs ===")

    db_manager = get_db_manager()
    product_repo = Repository(Product, db_manager, enable_audit=True)

    # Set audit context
    product_repo.set_context(user_id="user123", session_id="session456")

    # Perform operations
    product = product_repo.create(
        name="Audited Product",
        price=50.0,
        category="Test")
    product_repo.update(product.id, price=55.0)
    product_repo.delete(product.id, soft=True)

    # Query audit logs
    logs = get_audit_logs(
        resource_type="products",
        resource_id=str(product.id)
    )

    print(f"Found {len(logs)} audit log entries:")
    for log in logs:
        print(f"  {log.timestamp}: {log.action} by {log.user_id}")


def example_caching():
    """Example: Repository caching"""
    print("\n=== Repository Caching ===")

    db_manager = get_db_manager()

    # Create repository with caching enabled
    product_repo = Repository(Product, db_manager, enable_cache=True)

    # Create product
    product = product_repo.create(
        name="Cached Product",
        price=100.0,
        category="Test"
    )
    print(f"Created product: {product.id}")

    # First get - from database
    product1 = product_repo.get_by_id(product.id)
    print(f"First get: {product1.name}")

    # Second get - from cache (faster)
    product2 = product_repo.get_by_id(product.id)
    print(f"Second get (cached): {product2.name}")

    # Update invalidates cache
    product_repo.update(product.id, price=110.0)
    print("Updated product - cache invalidated")

    # Next get - from database again
    product3 = product_repo.get_by_id(product.id)
    print(f"After update: ${product3.price}")


def example_health_check():
    """Example: Database health check"""
    print("\n=== Database Health Check ===")

    db_manager = get_db_manager()

    # Perform health check
    health = db_manager.health_check()

    print(f"Database healthy: {health['healthy']}")
    print(f"Database type: {health['database_type']}")
    print(f"Connection test: {health['connection_test']}")
    print(f"Table count: {health['table_count']}")

    # Get metrics
    metrics = health['metrics']
    print("\nMetrics:")
    print(f"  Query count: {metrics['query_count']}")
    print(f"  Slow queries: {metrics['slow_query_count']}")
    print(f"  Error count: {metrics['error_count']}")
    print(f"  Avg query time: {metrics['avg_query_time']:.4f}s")


def example_find_operations():
    """Example: Find operations"""
    print("\n=== Find Operations ===")

    db_manager = get_db_manager()
    product_repo = Repository(Product, db_manager)

    # Create test data
    product_repo.bulk_create([
        {"name": "Laptop", "price": 999.99, "category": "Electronics"},
        {"name": "Mouse", "price": 29.99, "category": "Electronics"},
        {"name": "Desk", "price": 299.99, "category": "Furniture"},
    ])

    # Find by category
    electronics = product_repo.find_by(category="Electronics")
    print(f"Found {len(electronics)} electronics")

    # Count
    total = product_repo.count()
    print(f"Total products: {total}")

    # Exists
    exists = product_repo.exists(1)
    print(f"Product 1 exists: {exists}")


if __name__ == "__main__":
    print("Enhanced Database Layer Examples")
    print("=" * 50)

    # Run examples
    example_basic_crud()
    example_bulk_operations()
    example_unit_of_work()
    example_transaction_rollback()
    example_nested_transactions()
    example_run_tx_helper()
    example_pagination()
    example_audit_logs()
    example_caching()
    example_health_check()
    example_find_operations()

    print("\n" + "=" * 50)
    print("All examples completed!")
