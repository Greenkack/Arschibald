"""
Data API Endpoints for Dynamic Keys and PDF

This module provides REST API endpoints for managing universal data
with dynamic keys and PDF byte generation capabilities.

Task: 231 - API Endpoints for Dynamic Keys and PDF
Requirements: 14.4, 14.5, 14.10
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path as PathParam
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import io
import base64

from backend.core.database import get_db
from backend.core.dynamic_keys import KeyPrefix, DynamicKeyValidator
from backend.core.pdf_bytes import PDFMetadata
from backend.services.universal_data_service import UniversalDataService, BulkPDFGenerator
from backend.models.database_models import UniversalDatabaseModel


router = APIRouter()


# Pydantic models for request/response

class DynamicKeyRequest(BaseModel):
    """Request model for generating dynamic keys"""
    prefix: str = Field(..., description="Key prefix (e.g., 'SOL', 'PRJ', 'CUS')")
    include_timestamp: bool = Field(True, description="Include timestamp in key")
    include_uuid: bool = Field(True, description="Include UUID in key")
    custom_suffix: Optional[str] = Field(None, description="Optional custom suffix")


class DynamicKeyResponse(BaseModel):
    """Response model for dynamic key operations"""
    key: str = Field(..., description="Generated dynamic key")
    metadata: Dict[str, Any] = Field(..., description="Key metadata")
    created_at: str = Field(..., description="Creation timestamp")


class PDFGenerationRequest(BaseModel):
    """Request model for PDF generation"""
    title: Optional[str] = Field(None, description="PDF title")
    author: Optional[str] = Field(None, description="PDF author")
    subject: Optional[str] = Field(None, description="PDF subject")
    keywords: Optional[List[str]] = Field(None, description="PDF keywords")
    include_base64: bool = Field(False, description="Include base64 encoded PDF in response")


class PDFGenerationResponse(BaseModel):
    """Response model for PDF generation"""
    success: bool = Field(..., description="Whether PDF was generated successfully")
    size_bytes: int = Field(..., description="Size of generated PDF in bytes")
    pdf_base64: Optional[str] = Field(None, description="Base64 encoded PDF (if requested)")
    message: str = Field(..., description="Status message")


class BulkPDFRequest(BaseModel):
    """Request model for bulk PDF generation"""
    record_ids: List[int] = Field(..., description="List of record IDs to process")
    batch_size: int = Field(100, description="Number of records per batch", ge=1, le=1000)
    metadata: Optional[PDFGenerationRequest] = Field(None, description="PDF metadata for all records")


class BulkPDFResponse(BaseModel):
    """Response model for bulk PDF generation"""
    total_records: int = Field(..., description="Total number of records processed")
    generated: int = Field(..., description="Number of PDFs successfully generated")
    failed: int = Field(..., description="Number of failed generations")
    success_rate: float = Field(..., description="Success rate percentage")
    errors: List[str] = Field(..., description="List of error messages")


class KeySearchRequest(BaseModel):
    """Request model for key search"""
    prefix: Optional[str] = Field(None, description="Filter by key prefix")
    pattern: Optional[str] = Field(None, description="Search pattern (supports wildcards)")
    limit: int = Field(100, description="Maximum number of results", ge=1, le=1000)
    offset: int = Field(0, description="Offset for pagination", ge=0)


class KeySearchResponse(BaseModel):
    """Response model for key search"""
    keys: List[str] = Field(..., description="List of matching keys")
    total: int = Field(..., description="Total number of matches")
    limit: int = Field(..., description="Limit applied")
    offset: int = Field(..., description="Offset applied")


# API Endpoints

@router.get("/pdf/{dynamic_key}", response_class=Response)
async def get_pdf_by_dynamic_key(
    dynamic_key: str = PathParam(..., description="Dynamic key of the record"),
    db: Session = Depends(get_db)
):
    """
    Get PDF bytes for a record by its dynamic key.
    
    **Endpoint:** GET /api/v1/data/pdf/{dynamic_key}
    
    **Requirements:** 14.4, 14.5
    
    **Returns:** PDF file as binary response
    
    **Example:**
    ```
    GET /api/v1/data/pdf/SOL_20231116_143052_a1b2c3d4
    ```
    """
    service = UniversalDataService(db)
    
    # Validate key format
    validator = DynamicKeyValidator()
    is_valid, error_msg = validator.validate(dynamic_key, strict=False)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid dynamic key: {error_msg}")
    
    # Get record by key
    record = service.get_by_dynamic_key(UniversalDatabaseModel, dynamic_key)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record not found for key: {dynamic_key}")
    
    # Check if PDF exists
    if not record.has_pdf():
        raise HTTPException(status_code=404, detail="PDF not generated for this record")
    
    # Return PDF bytes
    return Response(
        content=record.pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={dynamic_key}.pdf"
        }
    )


@router.post("/generate-pdf", response_model=PDFGenerationResponse)
async def generate_pdf(
    record_id: int = Query(..., description="ID of the record to generate PDF for"),
    request: PDFGenerationRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Generate PDF bytes for a specific record.
    
    **Endpoint:** POST /api/v1/data/generate-pdf
    
    **Requirements:** 14.5, 14.8
    
    **Request Body:**
    ```json
    {
        "title": "Solar Calculation Report",
        "author": "Solar Calculator Pro",
        "subject": "PV System Analysis",
        "keywords": ["solar", "pv", "calculation"],
        "include_base64": false
    }
    ```
    
    **Returns:** PDF generation status and optionally base64 encoded PDF
    """
    service = UniversalDataService(db)
    
    # Get record
    record = db.query(UniversalDatabaseModel).filter(
        UniversalDatabaseModel.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Record not found: {record_id}")
    
    # Create PDF metadata
    metadata = None
    if any([request.title, request.author, request.subject, request.keywords]):
        metadata = PDFMetadata(
            title=request.title or "",
            author=request.author or "",
            subject=request.subject or "",
            keywords=request.keywords or []
        )
    
    # Generate PDF
    try:
        pdf_bytes = service.generate_pdf_for_record(record, metadata, commit=True)
        
        response_data = {
            "success": True,
            "size_bytes": len(pdf_bytes),
            "message": "PDF generated successfully"
        }
        
        # Include base64 if requested
        if request.include_base64:
            response_data["pdf_base64"] = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/by-key/{key}", response_model=Dict[str, Any])
async def get_data_by_key(
    key: str = PathParam(..., description="Dynamic key to lookup"),
    include_pdf: bool = Query(False, description="Include PDF bytes in response"),
    formatted: bool = Query(True, description="Return formatted data"),
    locale: str = Query("de-DE", description="Locale for formatting"),
    db: Session = Depends(get_db)
):
    """
    Get record data by its dynamic key.
    
    **Endpoint:** GET /api/v1/data/by-key/{key}
    
    **Requirements:** 14.4, 14.10
    
    **Query Parameters:**
    - include_pdf: Include PDF bytes (base64 encoded) in response
    - formatted: Return formatted data (e.g., German number format)
    - locale: Locale for formatting (default: de-DE)
    
    **Returns:** Record data with optional PDF bytes
    
    **Example:**
    ```
    GET /api/v1/data/by-key/SOL_20231116_143052_a1b2c3d4?include_pdf=true&formatted=true
    ```
    """
    service = UniversalDataService(db)
    
    # Validate key
    validator = DynamicKeyValidator()
    is_valid, error_msg = validator.validate(key, strict=False)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid dynamic key: {error_msg}")
    
    # Get record
    record = service.get_by_dynamic_key(UniversalDatabaseModel, key)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record not found for key: {key}")
    
    # Get formatted data
    data = service.get_formatted_data(
        record,
        locale=locale,
        include_keys=True
    ) if formatted else record.to_dict(include_keys=True)
    
    # Include PDF if requested
    if include_pdf and record.has_pdf():
        data["pdf_bytes"] = base64.b64encode(record.pdf_bytes).decode('utf-8')
        data["pdf_size_bytes"] = len(record.pdf_bytes)
    
    return data


@router.post("/bulk-pdf", response_model=BulkPDFResponse)
async def bulk_generate_pdf(
    request: BulkPDFRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Generate PDF bytes for multiple records in bulk.
    
    **Endpoint:** POST /api/v1/data/bulk-pdf
    
    **Requirements:** 14.5, 14.8
    
    **Request Body:**
    ```json
    {
        "record_ids": [1, 2, 3, 4, 5],
        "batch_size": 100,
        "metadata": {
            "title": "Bulk Report",
            "author": "Solar Calculator Pro"
        }
    }
    ```
    
    **Returns:** Bulk generation statistics
    """
    generator = BulkPDFGenerator(db)
    
    # Get records
    records = db.query(UniversalDatabaseModel).filter(
        UniversalDatabaseModel.id.in_(request.record_ids)
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No records found for provided IDs")
    
    # Create metadata if provided
    metadata = None
    if request.metadata:
        metadata = PDFMetadata(
            title=request.metadata.title or "",
            author=request.metadata.author or "",
            subject=request.metadata.subject or "",
            keywords=request.metadata.keywords or []
        )
    
    # Generate PDFs in batches
    try:
        result = generator.generate_pdfs_batch(
            records,
            batch_size=request.batch_size,
            metadata=metadata
        )
        
        return BulkPDFResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk PDF generation failed: {str(e)}")


@router.get("/keys/search", response_model=KeySearchResponse)
async def search_keys(
    prefix: Optional[str] = Query(None, description="Filter by key prefix"),
    pattern: Optional[str] = Query(None, description="Search pattern"),
    limit: int = Query(100, description="Maximum results", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0),
    db: Session = Depends(get_db)
):
    """
    Search for dynamic keys with filtering and pagination.
    
    **Endpoint:** GET /api/v1/data/keys/search
    
    **Requirements:** 14.4, 14.10
    
    **Query Parameters:**
    - prefix: Filter by key prefix (e.g., 'SOL', 'PRJ')
    - pattern: Search pattern (supports SQL LIKE wildcards)
    - limit: Maximum number of results (1-1000)
    - offset: Offset for pagination
    
    **Returns:** List of matching keys with pagination info
    
    **Examples:**
    ```
    GET /api/v1/data/keys/search?prefix=SOL&limit=50
    GET /api/v1/data/keys/search?pattern=%2023%&limit=100
    ```
    """
    service = UniversalDataService(db)
    
    # Build query
    query = db.query(UniversalDatabaseModel.dynamic_key).filter(
        UniversalDatabaseModel.dynamic_key.isnot(None)
    )
    
    # Apply prefix filter
    if prefix:
        # Validate prefix
        try:
            KeyPrefix(prefix)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid key prefix: {prefix}")
        
        query = query.filter(UniversalDatabaseModel.dynamic_key.like(f"{prefix}_%"))
    
    # Apply pattern filter
    if pattern:
        query = query.filter(UniversalDatabaseModel.dynamic_key.like(pattern))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    keys = query.offset(offset).limit(limit).all()
    key_list = [key[0] for key in keys]
    
    return KeySearchResponse(
        keys=key_list,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/keys/statistics", response_model=Dict[str, Any])
async def get_key_statistics(
    db: Session = Depends(get_db)
):
    """
    Get statistics about dynamic key usage.
    
    **Endpoint:** GET /api/v1/data/keys/statistics
    
    **Requirements:** 14.4
    
    **Returns:** Statistics about key usage by prefix
    
    **Example Response:**
    ```json
    {
        "total_keys": 1250,
        "keys_by_prefix": {
            "SOL": 450,
            "PRJ": 300,
            "CUS": 200,
            "HP": 150,
            "PDF": 150
        },
        "records_with_keys": 1250,
        "records_without_keys": 50
    }
    ```
    """
    service = UniversalDataService(db)
    
    # Get statistics
    stats = service.get_statistics(UniversalDatabaseModel)
    
    # Get breakdown by prefix
    prefix_stats = {}
    for prefix in KeyPrefix:
        count = db.query(UniversalDatabaseModel).filter(
            UniversalDatabaseModel.dynamic_key.like(f"{prefix.value}_%")
        ).count()
        if count > 0:
            prefix_stats[prefix.value] = count
    
    return {
        **stats,
        "keys_by_prefix": prefix_stats
    }


@router.get("/pdf/statistics", response_model=Dict[str, Any])
async def get_pdf_statistics(
    db: Session = Depends(get_db)
):
    """
    Get statistics about PDF generation.
    
    **Endpoint:** GET /api/v1/data/pdf/statistics
    
    **Requirements:** 14.5
    
    **Returns:** Statistics about PDF generation
    
    **Example Response:**
    ```json
    {
        "total_records": 1300,
        "records_with_pdfs": 1100,
        "records_without_pdfs": 200,
        "pdf_coverage_percent": 84.6,
        "total_pdf_size_bytes": 52428800,
        "average_pdf_size_bytes": 47662
    }
    ```
    """
    service = UniversalDataService(db)
    
    # Get basic statistics
    stats = service.get_statistics(UniversalDatabaseModel)
    
    # Calculate PDF size statistics
    records_with_pdf = service.get_records_with_pdf(UniversalDatabaseModel)
    total_size = sum(len(r.pdf_bytes) for r in records_with_pdf if r.pdf_bytes)
    avg_size = total_size / len(records_with_pdf) if records_with_pdf else 0
    
    return {
        "total_records": stats["total_records"],
        "records_with_pdfs": stats["records_with_pdfs"],
        "records_without_pdfs": stats["records_without_pdfs"],
        "pdf_coverage_percent": stats["pdf_coverage_percent"],
        "total_pdf_size_bytes": total_size,
        "average_pdf_size_bytes": int(avg_size)
    }


@router.delete("/pdf/{dynamic_key}")
async def delete_pdf_by_key(
    dynamic_key: str = PathParam(..., description="Dynamic key of the record"),
    db: Session = Depends(get_db)
):
    """
    Delete PDF bytes for a record by its dynamic key.
    
    **Endpoint:** DELETE /api/v1/data/pdf/{dynamic_key}
    
    **Requirements:** 14.5
    
    **Returns:** Deletion status
    """
    service = UniversalDataService(db)
    
    # Validate key
    validator = DynamicKeyValidator()
    is_valid, error_msg = validator.validate(dynamic_key, strict=False)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid dynamic key: {error_msg}")
    
    # Get record
    record = service.get_by_dynamic_key(UniversalDatabaseModel, dynamic_key)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record not found for key: {dynamic_key}")
    
    # Delete PDF
    deleted = service.delete_pdf(record, commit=True)
    
    if deleted:
        return {"success": True, "message": "PDF deleted successfully"}
    else:
        return {"success": False, "message": "No PDF found to delete"}


@router.post("/pdf/{dynamic_key}/regenerate", response_model=PDFGenerationResponse)
async def regenerate_pdf_by_key(
    dynamic_key: str = PathParam(..., description="Dynamic key of the record"),
    request: PDFGenerationRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Regenerate PDF bytes for a record by its dynamic key.
    
    **Endpoint:** POST /api/v1/data/pdf/{dynamic_key}/regenerate
    
    **Requirements:** 14.5
    
    **Returns:** PDF regeneration status
    """
    service = UniversalDataService(db)
    
    # Validate key
    validator = DynamicKeyValidator()
    is_valid, error_msg = validator.validate(dynamic_key, strict=False)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid dynamic key: {error_msg}")
    
    # Get record
    record = service.get_by_dynamic_key(UniversalDatabaseModel, dynamic_key)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record not found for key: {dynamic_key}")
    
    # Create metadata
    metadata = None
    if any([request.title, request.author, request.subject, request.keywords]):
        metadata = PDFMetadata(
            title=request.title or "",
            author=request.author or "",
            subject=request.subject or "",
            keywords=request.keywords or []
        )
    
    # Regenerate PDF
    try:
        pdf_bytes = service.regenerate_pdf(record, metadata, commit=True)
        
        response_data = {
            "success": True,
            "size_bytes": len(pdf_bytes),
            "message": "PDF regenerated successfully"
        }
        
        if request.include_base64:
            response_data["pdf_base64"] = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF regeneration failed: {str(e)}")
