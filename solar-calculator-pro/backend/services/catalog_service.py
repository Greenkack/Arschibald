"""
Product Catalog Service

This module provides business logic for managing the product catalog,
including categories, products, variants, bundles, relationships, and tags.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any, Tuple
from backend.models.catalog_models import (
    Category, Attribute, AttributeValue, Product, ProductVariant,
    ProductBundle, ProductRelationship, Tag, product_tags, product_attributes, bundle_products
)
from backend.models.catalog_schemas import (
    CategoryCreate, CategoryUpdate, AttributeCreate, AttributeUpdate,
    ProductCreate, ProductUpdate, ProductVariantCreate, ProductVariantUpdate,
    ProductBundleCreate, ProductBundleUpdate, ProductRelationshipCreate,
    TagCreate, TagUpdate, ProductSearchRequest, RelationshipType
)


class CatalogService:
    """Service for managing product catalog"""

    # ==================== Category Management ====================

    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        # Calculate level and path
        level = 0
        path = ""
        if category_data.parent_id:
            parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
            if parent:
                level = parent.level + 1
                path = f"{parent.path}/{parent.id}" if parent.path else f"/{parent.id}"

        category = Category(
            **category_data.model_dump(),
            level=level,
            path=path
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_category(db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
        """Get category by slug"""
        return db.query(Category).filter(Category.slug == slug).first()

    @staticmethod
    def get_categories(db: Session, parent_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[Category]:
        """Get categories with optional filtering"""
        query = db.query(Category)
        
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        
        return query.order_by(Category.sort_order, Category.name).all()

    @staticmethod
    def get_category_tree(db: Session) -> List[Category]:
        """Get hierarchical category tree"""
        categories = db.query(Category).filter(Category.is_active == True).order_by(Category.sort_order, Category.name).all()
        
        # Build tree structure
        category_map = {cat.id: cat for cat in categories}
        root_categories = []
        
        for category in categories:
            if category.parent_id is None:
                root_categories.append(category)
            elif category.parent_id in category_map:
                parent = category_map[category.parent_id]
                if not hasattr(parent, '_children'):
                    parent._children = []
                parent._children.append(category)
        
        return root_categories

    @staticmethod
    def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """Update category"""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        
        # Recalculate level and path if parent changed
        if 'parent_id' in update_data:
            if update_data['parent_id']:
                parent = db.query(Category).filter(Category.id == update_data['parent_id']).first()
                if parent:
                    update_data['level'] = parent.level + 1
                    update_data['path'] = f"{parent.path}/{parent.id}" if parent.path else f"/{parent.id}"
            else:
                update_data['level'] = 0
                update_data['path'] = ""

        for key, value in update_data.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """Delete category"""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False

        db.delete(category)
        db.commit()
        return True

    # ==================== Attribute Management ====================

    @staticmethod
    def create_attribute(db: Session, attribute_data: AttributeCreate) -> Attribute:
        """Create a new attribute"""
        attribute = Attribute(**attribute_data.model_dump())
        db.add(attribute)
        db.commit()
        db.refresh(attribute)
        return attribute

    @staticmethod
    def get_attribute(db: Session, attribute_id: int) -> Optional[Attribute]:
        """Get attribute by ID with values"""
        return db.query(Attribute).options(joinedload(Attribute.values)).filter(Attribute.id == attribute_id).first()

    @staticmethod
    def get_attributes(db: Session) -> List[Attribute]:
        """Get all attributes"""
        return db.query(Attribute).options(joinedload(Attribute.values)).order_by(Attribute.sort_order, Attribute.name).all()

    @staticmethod
    def update_attribute(db: Session, attribute_id: int, attribute_data: AttributeUpdate) -> Optional[Attribute]:
        """Update attribute"""
        attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
        if not attribute:
            return None

        update_data = attribute_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute, key, value)

        db.commit()
        db.refresh(attribute)
        return attribute

    @staticmethod
    def delete_attribute(db: Session, attribute_id: int) -> bool:
        """Delete attribute"""
        attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
        if not attribute:
            return False

        db.delete(attribute)
        db.commit()
        return True

    # ==================== Product Management ====================

    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """Create a new product"""
        # Extract relationships
        tag_ids = product_data.tag_ids if hasattr(product_data, 'tag_ids') else []
        attribute_value_ids = product_data.attribute_value_ids if hasattr(product_data, 'attribute_value_ids') else []
        
        # Create product
        product_dict = product_data.model_dump(exclude={'tag_ids', 'attribute_value_ids'})
        product = Product(**product_dict)
        
        # Add tags
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            product.tags = tags
        
        # Add attribute values
        if attribute_value_ids:
            attr_values = db.query(AttributeValue).filter(AttributeValue.id.in_(attribute_value_ids)).all()
            product.attribute_values = attr_values
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID with relationships"""
        return db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.attribute_values)
        ).filter(Product.id == product_id).first()

    @staticmethod
    def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return db.query(Product).filter(Product.sku == sku).first()

    @staticmethod
    def search_products(db: Session, search_params: ProductSearchRequest) -> Tuple[List[Product], int]:
        """Search products with filters and pagination"""
        query = db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.tags)
        )

        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.manufacturer.ilike(search_term)
                )
            )

        if search_params.category_id:
            query = query.filter(Product.category_id == search_params.category_id)

        if search_params.manufacturer:
            query = query.filter(Product.manufacturer == search_params.manufacturer)

        if search_params.min_price is not None:
            query = query.filter(Product.base_price >= search_params.min_price)

        if search_params.max_price is not None:
            query = query.filter(Product.base_price <= search_params.max_price)

        if search_params.is_active is not None:
            query = query.filter(Product.is_active == search_params.is_active)

        if search_params.is_featured is not None:
            query = query.filter(Product.is_featured == search_params.is_featured)

        if search_params.in_stock:
            query = query.filter(Product.stock_quantity > 0)

        if search_params.tags:
            query = query.join(Product.tags).filter(Tag.id.in_(search_params.tags))

        # Get total count
        total = query.count()

        # Apply sorting
        if search_params.sort_by == "name":
            query = query.order_by(Product.name.asc() if search_params.sort_order == "asc" else Product.name.desc())
        elif search_params.sort_by == "price":
            query = query.order_by(Product.base_price.asc() if search_params.sort_order == "asc" else Product.base_price.desc())
        elif search_params.sort_by == "created_at":
            query = query.order_by(Product.created_at.desc() if search_params.sort_order == "desc" else Product.created_at.asc())

        # Apply pagination
        offset = (search_params.page - 1) * search_params.page_size
        products = query.offset(offset).limit(search_params.page_size).all()

        return products, total

    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True, exclude={'tag_ids', 'attribute_value_ids'})
        
        for key, value in update_data.items():
            setattr(product, key, value)

        # Update tags if provided
        if hasattr(product_data, 'tag_ids') and product_data.tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(product_data.tag_ids)).all()
            product.tags = tags

        # Update attribute values if provided
        if hasattr(product_data, 'attribute_value_ids') and product_data.attribute_value_ids is not None:
            attr_values = db.query(AttributeValue).filter(AttributeValue.id.in_(product_data.attribute_value_ids)).all()
            product.attribute_values = attr_values

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Delete product"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False

        db.delete(product)
        db.commit()
        return True

    # ==================== Product Variant Management ====================

    @staticmethod
    def create_variant(db: Session, variant_data: ProductVariantCreate) -> ProductVariant:
        """Create a new product variant"""
        variant = ProductVariant(**variant_data.model_dump())
        db.add(variant)
        db.commit()
        db.refresh(variant)
        return variant

    @staticmethod
    def get_variant(db: Session, variant_id: int) -> Optional[ProductVariant]:
        """Get variant by ID"""
        return db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

    @staticmethod
    def get_product_variants(db: Session, product_id: int) -> List[ProductVariant]:
        """Get all variants for a product"""
        return db.query(ProductVariant).filter(ProductVariant.parent_product_id == product_id).all()

    @staticmethod
    def update_variant(db: Session, variant_id: int, variant_data: ProductVariantUpdate) -> Optional[ProductVariant]:
        """Update variant"""
        variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if not variant:
            return None

        update_data = variant_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(variant, key, value)

        db.commit()
        db.refresh(variant)
        return variant

    @staticmethod
    def delete_variant(db: Session, variant_id: int) -> bool:
        """Delete variant"""
        variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if not variant:
            return False

        db.delete(variant)
        db.commit()
        return True

    # ==================== Product Bundle Management ====================

    @staticmethod
    def create_bundle(db: Session, bundle_data: ProductBundleCreate) -> ProductBundle:
        """Create a new product bundle"""
        # Extract product items
        product_items = bundle_data.product_items
        bundle_dict = bundle_data.model_dump(exclude={'product_items'})
        
        bundle = ProductBundle(**bundle_dict)
        
        # Add products to bundle
        if product_items:
            product_ids = [item.product_id for item in product_items]
            products = db.query(Product).filter(Product.id.in_(product_ids)).all()
            bundle.products = products
        
        db.add(bundle)
        db.commit()
        db.refresh(bundle)
        return bundle

    @staticmethod
    def get_bundle(db: Session, bundle_id: int) -> Optional[ProductBundle]:
        """Get bundle by ID"""
        return db.query(ProductBundle).options(joinedload(ProductBundle.products)).filter(ProductBundle.id == bundle_id).first()

    @staticmethod
    def get_bundles(db: Session, is_active: Optional[bool] = None) -> List[ProductBundle]:
        """Get all bundles"""
        query = db.query(ProductBundle).options(joinedload(ProductBundle.products))
        
        if is_active is not None:
            query = query.filter(ProductBundle.is_active == is_active)
        
        return query.all()

    @staticmethod
    def update_bundle(db: Session, bundle_id: int, bundle_data: ProductBundleUpdate) -> Optional[ProductBundle]:
        """Update bundle"""
        bundle = db.query(ProductBundle).filter(ProductBundle.id == bundle_id).first()
        if not bundle:
            return None

        update_data = bundle_data.model_dump(exclude_unset=True, exclude={'product_items'})
        
        for key, value in update_data.items():
            setattr(bundle, key, value)

        # Update products if provided
        if hasattr(bundle_data, 'product_items') and bundle_data.product_items is not None:
            product_ids = [item.product_id for item in bundle_data.product_items]
            products = db.query(Product).filter(Product.id.in_(product_ids)).all()
            bundle.products = products

        db.commit()
        db.refresh(bundle)
        return bundle

    @staticmethod
    def delete_bundle(db: Session, bundle_id: int) -> bool:
        """Delete bundle"""
        bundle = db.query(ProductBundle).filter(ProductBundle.id == bundle_id).first()
        if not bundle:
            return False

        db.delete(bundle)
        db.commit()
        return True

    # ==================== Product Relationship Management ====================

    @staticmethod
    def create_relationship(db: Session, relationship_data: ProductRelationshipCreate) -> ProductRelationship:
        """Create a product relationship"""
        relationship = ProductRelationship(**relationship_data.model_dump())
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        return relationship

    @staticmethod
    def get_related_products(db: Session, product_id: int, relationship_type: Optional[RelationshipType] = None) -> List[Product]:
        """Get related products"""
        query = db.query(Product).join(
            ProductRelationship,
            ProductRelationship.related_product_id == Product.id
        ).filter(ProductRelationship.product_id == product_id)

        if relationship_type:
            query = query.filter(ProductRelationship.relationship_type == relationship_type.value)

        return query.order_by(ProductRelationship.sort_order).all()

    @staticmethod
    def delete_relationship(db: Session, relationship_id: int) -> bool:
        """Delete relationship"""
        relationship = db.query(ProductRelationship).filter(ProductRelationship.id == relationship_id).first()
        if not relationship:
            return False

        db.delete(relationship)
        db.commit()
        return True

    # ==================== Tag Management ====================

    @staticmethod
    def create_tag(db: Session, tag_data: TagCreate) -> Tag:
        """Create a new tag"""
        tag = Tag(**tag_data.model_dump())
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    @staticmethod
    def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
        """Get tag by ID"""
        return db.query(Tag).filter(Tag.id == tag_id).first()

    @staticmethod
    def get_tags(db: Session, is_active: Optional[bool] = None) -> List[Tag]:
        """Get all tags"""
        query = db.query(Tag)
        
        if is_active is not None:
            query = query.filter(Tag.is_active == is_active)
        
        return query.order_by(Tag.name).all()

    @staticmethod
    def update_tag(db: Session, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
        """Update tag"""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return None

        update_data = tag_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tag, key, value)

        db.commit()
        db.refresh(tag)
        return tag

    @staticmethod
    def delete_tag(db: Session, tag_id: int) -> bool:
        """Delete tag"""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return False

        db.delete(tag)
        db.commit()
        return True
