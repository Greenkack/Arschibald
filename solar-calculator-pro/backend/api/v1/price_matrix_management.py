"""
Price Matrix Management API

Provides REST API for price matrix management:
- Price matrix upload (Excel/CSV)
- Matrix editor UI
- Matrix validation
- Matrix versioning
- Convert matrix to JSON internally
- Module count × storage capacity lookup

Requirements: funktionen.txt - "Preis-Matrix"
Task: 276. Price Matrix Management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid
import json

router = APIRouter(prefix="/admin/price-matrix", tags=["Price Matrix Management"])


# ==================== Enums ====================

class MatrixStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class MatrixType(str, Enum):
    PV_STORAGE = "pv_storage"
    HEATPUMP = "heatpump"
    EXTRAS = "extras"
    SERVICES = "services"


# ==================== Pydantic Models ====================

class MatrixCell(BaseModel):
    """Single matrix cell"""
    row_index: int
    col_index: int
    value: float
    formatted: str


class MatrixRow(BaseModel):
    """Matrix row (module count)"""
    module_count: int
    values: Dict[str, float]  # storage_model -> price


class PriceMatrix(BaseModel):
    """Complete price matrix"""
    id: str
    name: str
    matrix_type: MatrixType
    status: MatrixStatus = MatrixStatus.DRAFT
    version: int = 1
    description: Optional[str] = None
    row_header: str = "Modulanzahl"
    col_header: str = "Speichermodell"
    row_labels: List[int]  # Module counts
    col_labels: List[str]  # Storage models
    data: List[List[float]]  # 2D price data
    currency: str = "EUR"
    includes_vat: bool = True
    vat_rate: float = 19.0
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: str = "system"


class MatrixUploadRequest(BaseModel):
    """Request for matrix upload"""
    name: str
    matrix_type: MatrixType = MatrixType.PV_STORAGE
    description: Optional[str] = None
    activate_immediately: bool = False


class MatrixLookupRequest(BaseModel):
    """Request for price lookup"""
    matrix_id: str
    module_count: int
    storage_model: str


class MatrixLookupResult(BaseModel):
    """Result of price lookup"""
    price_eur: float
    price_formatted: str
    module_count: int
    storage_model: str
    includes_vat: bool
    matrix_version: int


class MatrixValidationResult(BaseModel):
    """Matrix validation result"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    row_count: int
    col_count: int
    min_price: float
    max_price: float
    empty_cells: int


class MatrixVersion(BaseModel):
    """Matrix version info"""
    version: int
    created_at: datetime
    created_by: str
    changes: str
    is_current: bool


# ==================== Mock Data Store ====================

_matrices_store: Dict[str, PriceMatrix] = {}
_matrix_versions: Dict[str, List[MatrixVersion]] = {}


def generate_matrix_id() -> str:
    return f"mtx_{uuid.uuid4().hex[:8]}"


def create_sample_matrix() -> PriceMatrix:
    """Create sample PV+Storage price matrix"""
    module_counts = list(range(10, 51, 2))  # 10, 12, 14, ..., 50
    storage_models = ["kein Speicher", "BYD 5.1", "BYD 7.7", "BYD 10.2", "BYD 12.8", "BYD 15.4"]
    
    # Generate prices: base + per module + per storage
    data = []
    for modules in module_counts:
        row = []
        for i, storage in enumerate(storage_models):
            base_price = 5000
            module_price = modules * 350
            storage_price = [0, 3500, 5000, 6500, 8000, 9500][i]
            total = base_price + module_price + storage_price
            row.append(total)
        data.append(row)
    
    return PriceMatrix(
        id=generate_matrix_id(),
        name="Standard PV+Speicher Matrix 2024",
        matrix_type=MatrixType.PV_STORAGE,
        status=MatrixStatus.ACTIVE,
        version=1,
        description="Standardpreismatrix für PV-Anlagen mit Batteriespeicher",
        row_labels=module_counts,
        col_labels=storage_models,
        data=data,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


# Initialize with sample data
_sample = create_sample_matrix()
_matrices_store[_sample.id] = _sample


# ==================== Helper Functions ====================

def validate_matrix_data(row_labels: List[int], col_labels: List[str], data: List[List[float]]) -> MatrixValidationResult:
    """Validate matrix data"""
    errors = []
    warnings = []
    empty_cells = 0
    
    # Check dimensions
    if len(data) != len(row_labels):
        errors.append(f"Zeilenanzahl ({len(data)}) stimmt nicht mit Labels ({len(row_labels)}) überein")
    
    for i, row in enumerate(data):
        if len(row) != len(col_labels):
            errors.append(f"Zeile {i+1}: Spaltenanzahl ({len(row)}) stimmt nicht mit Labels ({len(col_labels)}) überein")
        for j, val in enumerate(row):
            if val is None or val == 0:
                empty_cells += 1
                warnings.append(f"Leere Zelle bei Zeile {i+1}, Spalte {j+1}")
    
    # Check for duplicates in labels
    if len(row_labels) != len(set(row_labels)):
        errors.append("Doppelte Werte in Zeilenlabels")
    if len(col_labels) != len(set(col_labels)):
        errors.append("Doppelte Werte in Spaltenlabels")
    
    # Calculate stats
    all_values = [v for row in data for v in row if v is not None and v > 0]
    min_price = min(all_values) if all_values else 0
    max_price = max(all_values) if all_values else 0
    
    return MatrixValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings[:10],  # Limit warnings
        row_count=len(row_labels),
        col_count=len(col_labels),
        min_price=min_price,
        max_price=max_price,
        empty_cells=empty_cells
    )


def lookup_price(matrix: PriceMatrix, module_count: int, storage_model: str) -> Optional[float]:
    """Lookup price in matrix"""
    try:
        row_idx = matrix.row_labels.index(module_count)
        col_idx = matrix.col_labels.index(storage_model)
        return matrix.data[row_idx][col_idx]
    except (ValueError, IndexError):
        return None


def format_price(price: float, currency: str = "EUR") -> str:
    """Format price with German formatting"""
    return f"{price:,.2f} {currency}".replace(",", "X").replace(".", ",").replace("X", ".")


# ==================== API Endpoints ====================

@router.get("/")
async def get_matrices(
    matrix_type: Optional[MatrixType] = None,
    status: Optional[MatrixStatus] = None
):
    """Get all price matrices."""
    matrices = list(_matrices_store.values())
    
    if matrix_type:
        matrices = [m for m in matrices if m.matrix_type == matrix_type]
    if status:
        matrices = [m for m in matrices if m.status == status]
    
    return {
        "matrices": matrices,
        "total": len(matrices),
        "active_count": len([m for m in matrices if m.status == MatrixStatus.ACTIVE])
    }


@router.post("/")
async def create_matrix(
    name: str,
    matrix_type: MatrixType,
    row_labels: List[int],
    col_labels: List[str],
    data: List[List[float]],
    description: Optional[str] = None
):
    """Create new price matrix."""
    # Validate
    validation = validate_matrix_data(row_labels, col_labels, data)
    if not validation.valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    matrix_id = generate_matrix_id()
    now = datetime.now()
    
    matrix = PriceMatrix(
        id=matrix_id,
        name=name,
        matrix_type=matrix_type,
        status=MatrixStatus.DRAFT,
        description=description,
        row_labels=row_labels,
        col_labels=col_labels,
        data=data,
        created_at=now,
        updated_at=now
    )
    
    _matrices_store[matrix_id] = matrix
    
    return {
        "matrix": matrix,
        "validation": validation,
        "message": "Matrix erfolgreich erstellt"
    }


@router.get("/{matrix_id}")
async def get_matrix(matrix_id: str):
    """Get specific matrix."""
    if matrix_id not in _matrices_store:
        raise HTTPException(status_code=404, detail="Matrix nicht gefunden")
    
    return {"matrix": _matrices_store[matrix_id]}


@router.put("/{matrix_id}")
async def update_matrix(
    matrix_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    data: Optional[List[List[float]]] = None
):
    """Update matrix."""
    if matrix_id not in _matrices_store:
        raise HTTPException(status_code=404, detail="Matrix nicht gefunden")
    
    matrix = _matrices_store[matrix_id]
    
    if name:
        matrix.name = name
    if description:
        matrix.description = description
    if data:
        validation = validate_matrix_data(matrix.row_labels, matrix.col_labels, data)
        if not validation.valid:
            raise HTTPException(status_code=400, detail={"errors": validation.errors})
        matrix.data = data
        matrix.version += 1
    
    matrix.updated_at = datetime.now()
    
    return {"matrix": matrix, "updated": True}


@router.put("/{matrix_id}/status")
async def update_matrix_status(matrix_id: str, status: MatrixStatus):
    """Update matrix status."""
    if matrix_id not in _matrices_store:
        raise HTTPException(status_code=404, detail="Matrix nicht gefunden")
    
    matrix = _matrices_store[matrix_id]
    
    # If activating, deactivate other matrices of same type
    if status == MatrixStatus.ACTIVE:
        for m in _matrices_store.values():
            if m.matrix_type == matrix.matrix_type and m.id != matrix_id:
                m.status = MatrixStatus.ARCHIVED
    
    matrix.status = status
    matrix.updated_at = datetime.now()
    
    return {"matrix": matrix, "updated": True}


@router.post("/{matrix_id}/lookup")
async def lookup_matrix_price(matrix_id: str, request: MatrixLookupRequest):
    """Lookup price in matrix."""
    if matrix_id not in _matrices_store:
        raise HTTPException(status_code=404, detail="Matrix nicht gefunden")
    
    matrix = _matrices_store[matrix_id]
    price = lookup_price(matrix, request.module_count, request.storage_model)
    
    if price is None:
        raise HTTPException(status_code=404, detail="Preis nicht gefunden für diese Kombination")
    
    return MatrixLookupResult(
        price_eur=price,
        price_formatted=format_price(price),
        module_count=request.module_count,
        storage_model=request.storage_model,
        includes_vat=matrix.includes_vat,
        matrix_version=matrix.version
    )


@router.post("/validate")
async def validate_matrix(
    row_labels: List[int],
    col_labels: List[str],
    data: List[List[float]]
):
    """Validate matrix data without saving."""
    validation = validate_matrix_data(row_labels, col_labels, data)
    return {"validation": validation}


@router.get("/{matrix_id}/export")
async def export_matrix(matrix_id: str, format: str = "json"):
    """Export matrix in various formats."""
    if matrix_id not in _matrices_store:
        raise HTTPException(status_code=404, detail="Matrix nicht gefunden")
    
    matrix = _matrices_store[matrix_id]
    
    if format == "json":
        return {"data": matrix.dict(), "format": "json"}
    elif format == "csv":
        # Generate CSV content
        lines = [",".join([""] + matrix.col_labels)]
        for i, row in enumerate(matrix.data):
            lines.append(",".join([str(matrix.row_labels[i])] + [str(v) for v in row]))
        return {"data": "\n".join(lines), "format": "csv"}
    
    raise HTTPException(status_code=400, detail="Unbekanntes Format")


@router.delete("/{matrix_id}")
async def delete_matrix(matrix_id: str):
    """Delete matrix."""
    if matrix_id not in _matrices_store:
        raise HTTPException(status_code=404, detail="Matrix nicht gefunden")
    
    del _matrices_store[matrix_id]
    return {"deleted": True, "matrix_id": matrix_id}


@router.get("/active/{matrix_type}")
async def get_active_matrix(matrix_type: MatrixType):
    """Get active matrix for type."""
    for matrix in _matrices_store.values():
        if matrix.matrix_type == matrix_type and matrix.status == MatrixStatus.ACTIVE:
            return {"matrix": matrix}
    
    raise HTTPException(status_code=404, detail="Keine aktive Matrix gefunden")


@router.get("/health/check")
async def health_check():
    """Health check for price matrix service."""
    return {
        "status": "healthy",
        "service": "price-matrix-management",
        "matrices_count": len(_matrices_store),
        "active_matrices": len([m for m in _matrices_store.values() if m.status == MatrixStatus.ACTIVE]),
        "timestamp": datetime.now().isoformat()
    }
