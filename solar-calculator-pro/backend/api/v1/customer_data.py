"""
Customer Data API Endpoints

Provides REST API for customer data management with CRM integration.
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import io

from ...services.customer_data_service import CustomerDataService

router = APIRouter(prefix="/customer-data", tags=["Customer Data"])

# Initialize service
customer_service = CustomerDataService()


# ==================== Pydantic Models ====================

class CustomerCreate(BaseModel):
    salutation: Optional[str] = ""
    title: Optional[str] = ""
    first_name: str
    last_name: str
    company: Optional[str] = ""
    street: Optional[str] = ""
    house_number: Optional[str] = ""
    postal_code: Optional[str] = ""
    city: Optional[str] = ""
    bundesland: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    mobile: Optional[str] = ""
    notes: Optional[str] = ""
    tags: Optional[List[str]] = []
    source: Optional[str] = "api"


class CustomerUpdate(BaseModel):
    salutation: Optional[str] = None
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    bundesland: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class CustomerResponse(BaseModel):
    id: int
    salutation: str
    title: str
    first_name: str
    last_name: str
    company: str
    street: str
    house_number: str
    postal_code: str
    city: str
    bundesland: str
    email: str
    phone: str
    mobile: str
    notes: str
    tags: List[str]
    source: str
    created_at: Optional[str]
    updated_at: Optional[str]


class CustomerSearchFilters(BaseModel):
    postal_code: Optional[str] = None
    city: Optional[str] = None
    bundesland: Optional[str] = None


class PlaceholderInfo(BaseModel):
    key: str
    placeholder: str
    description: str


class ImportResult(BaseModel):
    imported: int
    errors: List[str]


# ==================== CRUD Endpoints ====================

@router.post("/", response_model=Dict[str, int])
async def create_customer(customer: CustomerCreate):
    """Create a new customer."""
    try:
        customer_id = customer_service.create_customer(customer.dict())
        return {"id": customer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int):
    """Get customer by ID."""
    customer = customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}")
async def update_customer(customer_id: int, updates: CustomerUpdate):
    """Update customer data."""
    existing = customer_service.get_customer(customer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    customer_service.update_customer(customer_id, update_data)
    return {"success": True}


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int):
    """Delete customer."""
    existing = customer_service.get_customer(customer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_service.delete_customer(customer_id)
    return {"success": True}


# ==================== Search & List Endpoints ====================

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List all customers with pagination."""
    return customer_service.get_all_customers(limit=limit, offset=offset)


@router.get("/search/", response_model=List[CustomerResponse])
async def search_customers(
    q: str = Query("", description="Search query"),
    postal_code: Optional[str] = None,
    city: Optional[str] = None,
    bundesland: Optional[str] = None
):
    """Search customers by name, email, address, etc."""
    filters = {}
    if postal_code:
        filters['postal_code'] = postal_code
    if city:
        filters['city'] = city
    if bundesland:
        filters['bundesland'] = bundesland
    
    return customer_service.search_customers(q, filters if filters else None)


# ==================== PDF Placeholder Endpoints ====================

@router.get("/{customer_id}/placeholders", response_model=Dict[str, str])
async def get_customer_placeholders(customer_id: int):
    """Get PDF placeholders for a customer."""
    customer = customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer_service.get_pdf_placeholders(customer_id)


@router.get("/placeholders/list", response_model=List[PlaceholderInfo])
async def list_placeholders():
    """Get list of available PDF placeholders."""
    return customer_service.get_placeholder_list()


# ==================== Export Endpoints ====================

@router.get("/export/csv")
async def export_customers_csv(
    customer_ids: Optional[str] = Query(None, description="Comma-separated customer IDs")
):
    """Export customers to CSV."""
    ids = None
    if customer_ids:
        ids = [int(id.strip()) for id in customer_ids.split(",")]
    
    csv_content = customer_service.export_customers_csv(ids)
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers.csv"}
    )


@router.get("/export/json")
async def export_customers_json(
    customer_ids: Optional[str] = Query(None, description="Comma-separated customer IDs")
):
    """Export customers to JSON."""
    ids = None
    if customer_ids:
        ids = [int(id.strip()) for id in customer_ids.split(",")]
    
    json_content = customer_service.export_customers_json(ids)
    
    return StreamingResponse(
        io.StringIO(json_content),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=customers.json"}
    )


# ==================== Import Endpoints ====================

@router.post("/import/csv", response_model=ImportResult)
async def import_customers_csv(file: UploadFile = File(...)):
    """Import customers from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    result = customer_service.import_customers_csv(csv_content, source=f"csv_import_{file.filename}")
    return result


@router.post("/import/json", response_model=ImportResult)
async def import_customers_json(file: UploadFile = File(...)):
    """Import customers from JSON file."""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must be JSON")
    
    content = await file.read()
    json_content = content.decode('utf-8')
    
    result = customer_service.import_customers_json(json_content, source=f"json_import_{file.filename}")
    return result


# ==================== Health Check ====================

@router.get("/health/check")
async def health_check():
    """Check customer data service health."""
    return customer_service.health_check()
