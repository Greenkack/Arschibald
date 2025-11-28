"""
Product and Component Management API

Provides REST API for product and component management:
- Product CRUD operations
- CSV/Excel product import
- Product category management
- Mounting component database (per roof type)
- Product image management

Requirements: funktionen.txt - "Produkt- und Komponentenverwaltung"
Task: 274. Product and Component Management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/admin/products", tags=["Product Management"])


# ==================== Enums ====================

class ProductCategory(str, Enum):
    PV_MODULE = "pv_module"
    INVERTER = "inverter"
    BATTERY = "battery"
    MOUNTING = "mounting"
    CABLE = "cable"
    CONNECTOR = "connector"
    HEATPUMP = "heatpump"
    ACCESSORY = "accessory"


class RoofType(str, Enum):
    PITCHED = "pitched"
    FLAT = "flat"
    METAL = "metal"
    TILE = "tile"
    SLATE = "slate"
    FACADE = "facade"


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"
