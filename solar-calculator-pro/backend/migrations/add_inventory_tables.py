"""
Add Inventory Management Tables

This migration creates all tables required for the inventory management system.
"""

import sqlalchemy as sa
from alembic import op
from datetime import datetime


def upgrade():
    """Create inventory management tables"""
    
    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('contact_person', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('payment_terms', sa.String(100), nullable=True),
        sa.Column('currency', sa.String(3), nullable=True, server_default='EUR'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('rating', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_suppliers_id', 'suppliers', ['id'])
    op.create_index('ix_suppliers_name', 'suppliers', ['name'])
    op.create_index('ix_suppliers_code', 'suppliers', ['code'])
    
    # Create product_suppliers table
    op.create_table(
        'product_suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('supplier_sku', sa.String(100), nullable=True),
        sa.Column('cost_price', sa.Float(), nullable=False),
        sa.Column('minimum_order_quantity', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('lead_time_days', sa.Integer(), nullable=True, server_default='14'),
        sa.Column('is_preferred', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'])
    )
    op.create_index('ix_product_suppliers_id', 'product_suppliers', ['id'])
    
    # Create inventory_stock table
    op.create_table(
        'inventory_stock',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('quantity_reserved', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('quantity_available', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('reorder_point', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('reorder_quantity', sa.Integer(), nullable=True, server_default='50'),
        sa.Column('minimum_stock_level', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('maximum_stock_level', sa.Integer(), nullable=True, server_default='1000'),
        sa.Column('warehouse_location', sa.String(100), nullable=True),
        sa.Column('bin_location', sa.String(50), nullable=True),
        sa.Column('stock_status', sa.Enum('in_stock', 'low_stock', 'out_of_stock', 'discontinued', name='stockstatus'), nullable=True, server_default='in_stock'),
        sa.Column('last_counted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_restock_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id')
    )
    op.create_index('ix_inventory_stock_id', 'inventory_stock', ['id'])
    op.create_index('ix_inventory_stock_product_id', 'inventory_stock', ['product_id'])
    
    # Create inventory_transactions table
    op.create_table(
        'inventory_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.Enum('purchase', 'sale', 'adjustment', 'return', 'transfer', 'damage', name='transactiontype'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('quantity_before', sa.Integer(), nullable=False),
        sa.Column('quantity_after', sa.Integer(), nullable=False),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('unit_cost', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('performed_by', sa.String(255), nullable=True),
        sa.Column('transaction_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['stock_id'], ['inventory_stock.id'])
    )
    op.create_index('ix_inventory_transactions_id', 'inventory_transactions', ['id'])
    
    # Create purchase_orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'pending', 'approved', 'ordered', 'received', 'cancelled', name='purchaseorderstatus'), nullable=True, server_default='draft'),
        sa.Column('order_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('subtotal', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('tax_amount', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('shipping_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_amount', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('currency', sa.String(3), nullable=True, server_default='EUR'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('shipping_address', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('approved_by', sa.String(255), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number'),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'])
    )
    op.create_index('ix_purchase_orders_id', 'purchase_orders', ['id'])
    op.create_index('ix_purchase_orders_order_number', 'purchase_orders', ['order_number'])
    
    # Create purchase_order_items table
    op.create_table(
        'purchase_order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity_ordered', sa.Integer(), nullable=False),
        sa.Column('quantity_received', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('unit_cost', sa.Float(), nullable=False),
        sa.Column('total_cost', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'])
    )
    op.create_index('ix_purchase_order_items_id', 'purchase_order_items', ['id'])
    
    # Create stock_alerts table
    op.create_table(
        'stock_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=True, server_default='warning'),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('acknowledged_by', sa.String(255), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['stock_id'], ['inventory_stock.id'])
    )
    op.create_index('ix_stock_alerts_id', 'stock_alerts', ['id'])


def downgrade():
    """Drop inventory management tables"""
    op.drop_table('stock_alerts')
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('inventory_transactions')
    op.drop_table('inventory_stock')
    op.drop_table('product_suppliers')
    op.drop_table('suppliers')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS stockstatus')
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS purchaseorderstatus')
