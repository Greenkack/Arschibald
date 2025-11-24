"""
Product Pricing Service
Handles all pricing logic including tiered pricing, volume discounts, and promotional pricing
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status

from backend.models.pricing_models import (
    PriceList, ProductPrice, PriceHistory, VolumeDiscount,
    PromotionalPricing, PromotionalUsage, CustomerSpecificPrice,
    CustomerPriceList, PricingType, DiscountType
)
from backend.models.pricing_schemas import (
    PriceListCreate, PriceListUpdate, ProductPriceCreate, ProductPriceUpdate,
    VolumeDiscountCreate, VolumeDiscountUpdate, PromotionalPricingCreate,
    PromotionalPricingUpdate, CustomerSpecificPriceCreate, CustomerSpecificPriceUpdate,
    PriceCalculationRequest, PriceCalculationResponse, PriceBreakdown
)
from backend.core.german_formatter import GermanNumberFormatter


class PricingService:
    """Service for managing product pricing"""

    def __init__(self, db: Session):
        self.db = db
        self.formatter = GermanNumberFormatter()

    # Price List Management
    def create_price_list(self, price_list: PriceListCreate) -> PriceList:
        """Create a new price list"""
        # If setting as default, unset other defaults
        if price_list.is_default:
            self.db.query(PriceList).update({"is_default": False})

        db_price_list = PriceList(**price_list.dict())
        self.db.add(db_price_list)
        self.db.commit()
        self.db.refresh(db_price_list)
        return db_price_list

    def get_price_list(self, price_list_id: int) -> Optional[PriceList]:
        """Get price list by ID"""
        return self.db.query(PriceList).filter(PriceList.id == price_list_id).first()

    def get_price_lists(self, active_only: bool = False) -> List[PriceList]:
        """Get all price lists"""
        query = self.db.query(PriceList)
        if active_only:
            query = query.filter(PriceList.is_active == True)
        return query.all()

    def update_price_list(self, price_list_id: int, update_data: PriceListUpdate) -> PriceList:
        """Update price list"""
        db_price_list = self.get_price_list(price_list_id)
        if not db_price_list:
            raise HTTPException(status_code=404, detail="Price list not found")

        # If setting as default, unset other defaults
        if update_data.is_default:
            self.db.query(PriceList).filter(PriceList.id != price_list_id).update({"is_default": False})

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(db_price_list, key, value)

        self.db.commit()
        self.db.refresh(db_price_list)
        return db_price_list

    def delete_price_list(self, price_list_id: int) -> bool:
        """Delete price list"""
        db_price_list = self.get_price_list(price_list_id)
        if not db_price_list:
            raise HTTPException(status_code=404, detail="Price list not found")

        if db_price_list.is_default:
            raise HTTPException(status_code=400, detail="Cannot delete default price list")

        self.db.delete(db_price_list)
        self.db.commit()
        return True

    # Product Price Management
    def create_product_price(self, product_price: ProductPriceCreate, changed_by: str = None) -> ProductPrice:
        """Create product price in a price list"""
        # Check if price already exists
        existing = self.db.query(ProductPrice).filter(
            and_(
                ProductPrice.price_list_id == product_price.price_list_id,
                ProductPrice.product_id == product_price.product_id
            )
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Price already exists for this product in this price list")

        db_product_price = ProductPrice(**product_price.dict())
        self.db.add(db_product_price)
        self.db.commit()
        self.db.refresh(db_product_price)
        return db_product_price

    def update_product_price(self, product_price_id: int, update_data: ProductPriceUpdate, changed_by: str = None) -> ProductPrice:
        """Update product price and track history"""
        db_product_price = self.db.query(ProductPrice).filter(ProductPrice.id == product_price_id).first()
        if not db_product_price:
            raise HTTPException(status_code=404, detail="Product price not found")

        # Track price change
        if update_data.base_price and update_data.base_price != db_product_price.base_price:
            old_price = db_product_price.base_price
            new_price = update_data.base_price
            change_percentage = ((new_price - old_price) / old_price) * 100

            price_history = PriceHistory(
                product_price_id=product_price_id,
                old_price=old_price,
                new_price=new_price,
                change_percentage=change_percentage,
                changed_by=changed_by
            )
            self.db.add(price_history)

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(db_product_price, key, value)

        self.db.commit()
        self.db.refresh(db_product_price)
        return db_product_price

    def get_product_price_history(self, product_price_id: int) -> List[PriceHistory]:
        """Get price change history"""
        return self.db.query(PriceHistory).filter(
            PriceHistory.product_price_id == product_price_id
        ).order_by(PriceHistory.changed_at.desc()).all()

    # Volume Discount Management
    def create_volume_discount(self, discount: VolumeDiscountCreate) -> VolumeDiscount:
        """Create volume discount rule"""
        db_discount = VolumeDiscount(**discount.dict())
        self.db.add(db_discount)
        self.db.commit()
        self.db.refresh(db_discount)
        return db_discount

    def get_volume_discounts(self, product_id: Optional[int] = None, active_only: bool = True) -> List[VolumeDiscount]:
        """Get volume discounts"""
        query = self.db.query(VolumeDiscount)
        
        if active_only:
            now = datetime.utcnow()
            query = query.filter(
                and_(
                    VolumeDiscount.is_active == True,
                    VolumeDiscount.valid_from <= now,
                    or_(VolumeDiscount.valid_until == None, VolumeDiscount.valid_until >= now)
                )
            )
        
        if product_id:
            query = query.filter(
                or_(
                    VolumeDiscount.product_id == product_id,
                    VolumeDiscount.product_id == None
                )
            )
        
        return query.all()

    def update_volume_discount(self, discount_id: int, update_data: VolumeDiscountUpdate) -> VolumeDiscount:
        """Update volume discount"""
        db_discount = self.db.query(VolumeDiscount).filter(VolumeDiscount.id == discount_id).first()
        if not db_discount:
            raise HTTPException(status_code=404, detail="Volume discount not found")

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(db_discount, key, value)

        self.db.commit()
        self.db.refresh(db_discount)
        return db_discount

    # Promotional Pricing Management
    def create_promotional_pricing(self, promo: PromotionalPricingCreate) -> PromotionalPricing:
        """Create promotional pricing campaign"""
        # Check if promo code is unique
        if promo.promo_code:
            existing = self.db.query(PromotionalPricing).filter(
                PromotionalPricing.promo_code == promo.promo_code
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Promo code already exists")

        db_promo = PromotionalPricing(**promo.dict())
        self.db.add(db_promo)
        self.db.commit()
        self.db.refresh(db_promo)
        return db_promo

    def get_promotional_pricing(self, promo_code: str) -> Optional[PromotionalPricing]:
        """Get promotional pricing by code"""
        now = datetime.utcnow()
        return self.db.query(PromotionalPricing).filter(
            and_(
                PromotionalPricing.promo_code == promo_code,
                PromotionalPricing.is_active == True,
                PromotionalPricing.valid_from <= now,
                PromotionalPricing.valid_until >= now
            )
        ).first()

    def validate_promo_code(self, promo_code: str, customer_id: int, product_id: int) -> tuple[bool, Optional[str]]:
        """Validate if promo code can be used"""
        promo = self.get_promotional_pricing(promo_code)
        
        if not promo:
            return False, "Invalid or expired promo code"

        # Check usage limits
        if promo.max_uses_total and promo.current_uses >= promo.max_uses_total:
            return False, "Promo code usage limit reached"

        if promo.max_uses_per_customer:
            customer_uses = self.db.query(PromotionalUsage).filter(
                and_(
                    PromotionalUsage.promotion_id == promo.id,
                    PromotionalUsage.customer_id == customer_id
                )
            ).count()
            if customer_uses >= promo.max_uses_per_customer:
                return False, "You have reached the usage limit for this promo code"

        # Check product applicability
        if promo.product_ids and product_id not in promo.product_ids:
            return False, "Promo code not applicable to this product"

        # Check customer applicability
        if promo.customer_ids and customer_id not in promo.customer_ids:
            return False, "Promo code not applicable to your account"

        return True, None

    # Customer-Specific Pricing
    def create_customer_specific_price(self, price: CustomerSpecificPriceCreate) -> CustomerSpecificPrice:
        """Create customer-specific price"""
        db_price = CustomerSpecificPrice(**price.dict())
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price

    def get_customer_specific_price(self, customer_id: int, product_id: int) -> Optional[CustomerSpecificPrice]:
        """Get customer-specific price"""
        now = datetime.utcnow()
        return self.db.query(CustomerSpecificPrice).filter(
            and_(
                CustomerSpecificPrice.customer_id == customer_id,
                CustomerSpecificPrice.product_id == product_id,
                CustomerSpecificPrice.is_active == True,
                CustomerSpecificPrice.valid_from <= now,
                or_(CustomerSpecificPrice.valid_until == None, CustomerSpecificPrice.valid_until >= now)
            )
        ).first()

    # Price Calculation
    def calculate_price(self, request: PriceCalculationRequest) -> PriceCalculationResponse:
        """Calculate final price with all applicable discounts"""
        # Get base price
        base_price = self._get_base_price(request.product_id, request.price_list_id, request.customer_id)
        
        if not base_price:
            raise HTTPException(status_code=404, detail="Price not found for product")

        # Initialize breakdown
        breakdown = PriceBreakdown(
            base_price=base_price,
            unit_price=base_price,
            subtotal=base_price * request.quantity,
            pricing_type="standard",
            currency="EUR"
        )

        applied_discounts = []

        # Check for customer-specific pricing
        if request.customer_id:
            customer_price = self.get_customer_specific_price(request.customer_id, request.product_id)
            if customer_price:
                breakdown.unit_price = customer_price.special_price
                breakdown.subtotal = customer_price.special_price * request.quantity
                breakdown.customer_discount = (base_price - customer_price.special_price) * request.quantity
                breakdown.pricing_type = "customer_specific"
                applied_discounts.append({
                    "type": "customer_specific",
                    "amount": breakdown.customer_discount,
                    "description": customer_price.reason or "Customer-specific pricing"
                })

        # Apply volume discounts
        volume_discounts = self.get_volume_discounts(request.product_id, active_only=True)
        for discount in volume_discounts:
            if discount.min_quantity <= request.quantity:
                if not discount.max_quantity or request.quantity <= discount.max_quantity:
                    discount_amount = self._calculate_discount(
                        breakdown.subtotal,
                        discount.discount_type.value,
                        discount.discount_value
                    )
                    breakdown.volume_discount += discount_amount
                    applied_discounts.append({
                        "type": "volume_discount",
                        "amount": discount_amount,
                        "description": discount.name
                    })

        # Apply promotional pricing
        if request.promo_code:
            is_valid, error_msg = self.validate_promo_code(
                request.promo_code,
                request.customer_id or 0,
                request.product_id
            )
            if is_valid:
                promo = self.get_promotional_pricing(request.promo_code)
                discount_amount = self._calculate_discount(
                    breakdown.subtotal,
                    promo.discount_type.value,
                    promo.discount_value
                )
                if promo.max_discount_amount:
                    discount_amount = min(discount_amount, promo.max_discount_amount)
                
                breakdown.promotional_discount = discount_amount
                applied_discounts.append({
                    "type": "promotional",
                    "amount": discount_amount,
                    "description": promo.name,
                    "code": promo.promo_code
                })

        # Calculate final price
        breakdown.total_discount = (
            breakdown.volume_discount +
            breakdown.promotional_discount +
            breakdown.customer_discount
        )
        breakdown.final_price = breakdown.subtotal - breakdown.total_discount
        breakdown.applied_discounts = applied_discounts

        # Calculate savings
        savings = breakdown.subtotal - breakdown.final_price
        savings_percentage = (savings / breakdown.subtotal * 100) if breakdown.subtotal > 0 else 0

        # Format price in German
        formatted_price = self.formatter.format_currency(breakdown.final_price)

        return PriceCalculationResponse(
            product_id=request.product_id,
            quantity=request.quantity,
            breakdown=breakdown,
            formatted_price=formatted_price,
            savings=savings if savings > 0 else None,
            savings_percentage=savings_percentage if savings > 0 else None
        )

    def _get_base_price(self, product_id: int, price_list_id: Optional[int], customer_id: Optional[int]) -> Optional[float]:
        """Get base price for product"""
        # Try customer-specific price list first
        if customer_id:
            customer_price_list = self.db.query(CustomerPriceList).filter(
                CustomerPriceList.customer_id == customer_id
            ).order_by(CustomerPriceList.priority.desc()).first()
            
            if customer_price_list:
                price_list_id = customer_price_list.price_list_id

        # Use specified or default price list
        if not price_list_id:
            default_list = self.db.query(PriceList).filter(PriceList.is_default == True).first()
            if default_list:
                price_list_id = default_list.id

        if not price_list_id:
            return None

        # Get product price
        product_price = self.db.query(ProductPrice).filter(
            and_(
                ProductPrice.price_list_id == price_list_id,
                ProductPrice.product_id == product_id
            )
        ).first()

        return product_price.base_price if product_price else None

    def _calculate_discount(self, amount: float, discount_type: str, discount_value: float) -> float:
        """Calculate discount amount"""
        if discount_type == "percentage":
            return amount * (discount_value / 100)
        elif discount_type == "fixed_amount":
            return min(discount_value, amount)
        return 0.0
