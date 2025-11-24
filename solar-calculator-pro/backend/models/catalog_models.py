"""
Product Catalog Database Models

This module defines the database models for the product catalog management system,
including categories, attributes, variants, bundles, relationships, and tags.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


# Association tables for many-to-many relationships
product_tags = Table(
    'product_tags',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

product_attributes = Table(
    'product_attributes',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE')),
    Column('attribute_value_id', Integer, ForeignKey('attribute_values.id', ondelete='CASCADE'))
)

bundle_products = Table(
    'bundle_products',
    Base.metadata,
    Column('bundle_id', Integer, ForeignKey('product_bundles.id', ondelete='CASCADE')),
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE')),
    Column('quantity', Integer, default=1)
)


class Category(Base):
    """Hierarchical product category model"""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=True)
    level = Column(Integer, default=0)  # Hierarchy level
    path = Column(String(500))  # Full path for efficient queries (e.g., "/1/5/12")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(500))
    metadata = Column(JSON)  # Additional flexible data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship('Category', remote_side=[id], backref='children')
    products = relationship('Product', back_populates='category')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', level={self.level})>"


class Attribute(Base):
    """Product attribute definition (e.g., Color, Size, Power)"""
    __tablename__ = 'attributes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    type = Column(String(50), nullable=False)  # text, number, boolean, select, multiselect
    unit = Column(String(50))  # e.g., "W", "kg", "cm"
    is_required = Column(Boolean, default=False)
    is_filterable = Column(Boolean, default=True)
    is_searchable = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    validation_rules = Column(JSON)  # e.g., {"min": 0, "max": 1000}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    values = relationship('AttributeValue', back_populates='attribute', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Attribute(id={self.id}, name='{self.name}', type='{self.type}')>"


class AttributeValue(Base):
    """Possible values for select/multiselect attributes"""
    __tablename__ = 'attribute_values'

    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey('attributes.id', ondelete='CASCADE'), nullable=False)
    value = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attribute = relationship('Attribute', back_populates='values')

    def __repr__(self):
        return f"<AttributeValue(id={self.id}, value='{self.value}', label='{self.label}')>"


class Product(Base):
    """Base product model"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    description = Column(Text)
    short_description = Column(String(500))
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'))
    manufacturer = Column(String(255), index=True)
    model = Column(String(255))
    base_price = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), default='EUR')
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    stock_quantity = Column(Integer, default=0)
    weight = Column(Float)  # in kg
    dimensions = Column(JSON)  # {"length": 100, "width": 50, "height": 30}
    images = Column(JSON)  # Array of image URLs
    specifications = Column(JSON)  # Technical specifications
    metadata = Column(JSON)  # Additional flexible data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship('Category', back_populates='products')
    variants = relationship('ProductVariant', back_populates='parent_product', cascade='all, delete-orphan')
    tags = relationship('Tag', secondary=product_tags, back_populates='products')
    attribute_values = relationship('AttributeValue', secondary=product_attributes)
    related_from = relationship('ProductRelationship', foreign_keys='ProductRelationship.product_id', back_populates='product')
    related_to = relationship('ProductRelationship', foreign_keys='ProductRelationship.related_product_id', back_populates='related_product')

    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"


class ProductVariant(Base):
    """Product variant model (e.g., different colors, sizes)"""
    __tablename__ = 'product_variants'

    id = Column(Integer, primary_key=True, index=True)
    parent_product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    price_adjustment = Column(Float, default=0.0)  # Difference from base price
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    variant_attributes = Column(JSON)  # {"color": "red", "size": "large"}
    images = Column(JSON)  # Variant-specific images
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_product = relationship('Product', back_populates='variants')

    def __repr__(self):
        return f"<ProductVariant(id={self.id}, sku='{self.sku}', name='{self.name}')>"


class ProductBundle(Base):
    """Product bundle model (multiple products sold together)"""
    __tablename__ = 'product_bundles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    description = Column(Text)
    bundle_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    images = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship('Product', secondary=bundle_products)

    def __repr__(self):
        return f"<ProductBundle(id={self.id}, name='{self.name}')>"


class ProductRelationship(Base):
    """Product relationships (related, cross-sell, upsell)"""
    __tablename__ = 'product_relationships'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    related_product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # related, cross_sell, upsell, accessory
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship('Product', foreign_keys=[product_id], back_populates='related_from')
    related_product = relationship('Product', foreign_keys=[related_product_id], back_populates='related_to')

    def __repr__(self):
        return f"<ProductRelationship(product_id={self.product_id}, related_id={self.related_product_id}, type='{self.relationship_type}')>"


class Tag(Base):
    """Product tag model"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship('Product', secondary=product_tags, back_populates='tags')

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
