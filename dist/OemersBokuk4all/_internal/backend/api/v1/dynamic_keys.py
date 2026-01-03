"""
Dynamic Keys API Endpoints

This module provides REST API endpoints for managing dynamic keys,
including generation, storage, search, and usage tracking.

Requirements: 4.1, 6.1
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from backend.services.dynamic_key_service import get_dynamic_key_service
from backend.core.dynamic_keys import KeyPrefix, KeyType


router = APIRouter(prefix="/dynamic-keys", tags=["dynamic-keys"])
service = get_dynamic_key_service()


# Request/Response Models

class KeyGenerationRequest(BaseModel):
    """Request model for key generation"""
    prefix: KeyPrefix
    include_timestamp: bool = True
    include_uuid: bool = True
    custom_suffix: Optional[str] = None


class KeyGenerationResponse(BaseModel):
    """Response model for key generation"""
    key: str
    prefix: str
    created_at: str


class KeyValueSetRequest(BaseModel):
    """Request model for setting a key-value pair"""
    key: str
    value: Any
    key_type: Optional[KeyType] = None
    namespace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class KeyValueGetResponse(BaseModel):
    """Response model for getting a value"""
    key: str
    value: Any
    key_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    exists: bool


class KeySearchRequest(BaseModel):
    """Request model for key search"""
    pattern: Optional[str] = None
    namespace: Optional[str] = None
    key_type: Optional[KeyType] = None
    metadata_filter: Optional[Dict[str, Any]] = None
    prefix: Optional[KeyPrefix] = None


class KeySearchResponse(BaseModel):
    """Response model for key search"""
    keys: List[str]
    count: int


class NamespaceCreateRequest(BaseModel):
    """Request model for namespace creation"""
    path: str


class NamespaceResponse(BaseModel):
    """Response model for namespace"""
    name: str
    full_path: str
    key_count: int
    children: Dict[str, Any]


class UsageStatisticsResponse(BaseModel):
    """Response model for usage statistics"""
    statistics: Dict[str, Any]


class BulkSetRequest(BaseModel):
    """Request model for bulk set operation"""
    items: Dict[str, Any]
    key_type: Optional[KeyType] = None
    namespace: Optional[str] = None


class BulkGetRequest(BaseModel):
    """Request model for bulk get operation"""
    keys: List[str]


class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete operation"""
    keys: List[str]


# API Endpoints

@router.post("/generate", response_model=KeyGenerationResponse)
async def generate_key(request: KeyGenerationRequest):
    """
    Generate a new dynamic key.
    
    Args:
        request: Key generation parameters
        
    Returns:
        Generated key information
    """
    try:
        key = service.generate_key(
            prefix=request.prefix,
            include_timestamp=request.include_timestamp,
            include_uuid=request.include_uuid,
            custom_suffix=request.custom_suffix
        )
        
        from datetime import datetime
        return KeyGenerationResponse(
            key=key,
            prefix=request.prefix.value,
            created_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-hash")
async def generate_hash_key(
    data: str = Body(..., embed=True),
    prefix: KeyPrefix = Body(KeyPrefix.DATA, embed=True)
):
    """
    Generate a hash-based key from data.
    
    Args:
        data: Data to hash
        prefix: Key prefix
        
    Returns:
        Generated hash key
    """
    try:
        key = service.generate_hash_key_from_data(data, prefix)
        return {"key": key, "prefix": prefix.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set")
async def set_value(request: KeyValueSetRequest):
    """
    Store a key-value pair.
    
    Args:
        request: Key-value data
        
    Returns:
        Success confirmation
    """
    try:
        service.set_value(
            key=request.key,
            value=request.value,
            key_type=request.key_type,
            namespace=request.namespace,
            metadata=request.metadata
        )
        return {"success": True, "key": request.key}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{key}", response_model=KeyValueGetResponse)
async def get_value(
    key: str,
    validate_type: bool = Query(True)
):
    """
    Retrieve a value by key.
    
    Args:
        key: Key to retrieve
        validate_type: Whether to validate type
        
    Returns:
        Value and metadata
    """
    try:
        exists = service.value_exists(key)
        
        if not exists:
            return KeyValueGetResponse(
                key=key,
                value=None,
                exists=False
            )
        
        value = service.get_value(key, validate_type=validate_type)
        key_type = service.get_key_type(key)
        metadata = service.get_key_metadata(key)
        
        return KeyValueGetResponse(
            key=key,
            value=value,
            key_type=key_type.value if key_type else None,
            metadata=metadata,
            exists=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{key}")
async def delete_value(key: str):
    """
    Delete a key-value pair.
    
    Args:
        key: Key to delete
        
    Returns:
        Success confirmation
    """
    try:
        deleted = service.delete_value(key)
        return {"success": deleted, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exists/{key}")
async def check_exists(key: str):
    """
    Check if a key exists.
    
    Args:
        key: Key to check
        
    Returns:
        Existence status
    """
    try:
        exists = service.value_exists(key)
        return {"key": key, "exists": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=KeySearchResponse)
async def search_keys(request: KeySearchRequest):
    """
    Search for keys matching criteria.
    
    Args:
        request: Search parameters
        
    Returns:
        List of matching keys
    """
    try:
        keys = service.search_keys(
            pattern=request.pattern,
            namespace=request.namespace,
            key_type=request.key_type,
            metadata_filter=request.metadata_filter,
            prefix=request.prefix
        )
        
        return KeySearchResponse(
            keys=keys,
            count=len(keys)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter/prefix/{prefix}")
async def filter_by_prefix(prefix: KeyPrefix):
    """
    Get all keys with a specific prefix.
    
    Args:
        prefix: Key prefix to filter by
        
    Returns:
        List of matching keys
    """
    try:
        keys = service.filter_by_prefix(prefix)
        return {"prefix": prefix.value, "keys": keys, "count": len(keys)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter/type/{key_type}")
async def filter_by_type(key_type: KeyType):
    """
    Get all keys of a specific type.
    
    Args:
        key_type: Key type to filter by
        
    Returns:
        List of matching keys
    """
    try:
        keys = service.filter_by_type(key_type)
        return {"key_type": key_type.value, "keys": keys, "count": len(keys)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter/namespace/{namespace}")
async def filter_by_namespace(
    namespace: str,
    recursive: bool = Query(False)
):
    """
    Get all keys in a namespace.
    
    Args:
        namespace: Namespace path
        recursive: Whether to include child namespaces
        
    Returns:
        List of keys
    """
    try:
        keys = service.filter_by_namespace(namespace, recursive)
        return {
            "namespace": namespace,
            "recursive": recursive,
            "keys": keys,
            "count": len(keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/namespace/create", response_model=NamespaceResponse)
async def create_namespace(request: NamespaceCreateRequest):
    """
    Create a namespace.
    
    Args:
        request: Namespace creation parameters
        
    Returns:
        Created namespace information
    """
    try:
        namespace = service.create_namespace(request.path)
        return NamespaceResponse(
            name=namespace.name,
            full_path=namespace.get_full_path(),
            key_count=namespace.count_keys(),
            children={
                name: child.to_dict()
                for name, child in namespace.children.items()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespace/{path}", response_model=NamespaceResponse)
async def get_namespace(path: str):
    """
    Get a namespace by path.
    
    Args:
        path: Namespace path
        
    Returns:
        Namespace information
    """
    try:
        namespace = service.get_namespace(path)
        
        if not namespace:
            raise HTTPException(status_code=404, detail="Namespace not found")
        
        return NamespaceResponse(
            name=namespace.name,
            full_path=namespace.get_full_path(),
            key_count=namespace.count_keys(),
            children={
                name: child.to_dict()
                for name, child in namespace.children.items()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespaces")
async def list_namespaces():
    """
    List all namespace paths.
    
    Returns:
        List of namespace paths
    """
    try:
        namespaces = service.list_namespaces()
        return {"namespaces": namespaces, "count": len(namespaces)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/statistics", response_model=UsageStatisticsResponse)
async def get_usage_statistics(key: Optional[str] = Query(None)):
    """
    Get usage statistics for a key or all keys.
    
    Args:
        key: Optional specific key to get stats for
        
    Returns:
        Usage statistics
    """
    try:
        stats = service.get_usage_statistics(key)
        return UsageStatisticsResponse(statistics=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/most-accessed")
async def get_most_accessed(limit: int = Query(10, ge=1, le=100)):
    """
    Get the most frequently accessed keys.
    
    Args:
        limit: Number of keys to return
        
    Returns:
        List of most accessed keys
    """
    try:
        keys = service.get_most_accessed_keys(limit)
        return {
            "keys": [{"key": k, "count": c} for k, c in keys],
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/recently-accessed")
async def get_recently_accessed(limit: int = Query(10, ge=1, le=100)):
    """
    Get the most recently accessed keys.
    
    Args:
        limit: Number of keys to return
        
    Returns:
        List of recently accessed keys
    """
    try:
        keys = service.get_recently_accessed_keys(limit)
        return {
            "keys": [
                {"key": k, "last_access": v.isoformat()}
                for k, v in keys
            ],
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/unused")
async def get_unused_keys():
    """
    Get keys that have never been accessed.
    
    Returns:
        List of unused keys
    """
    try:
        keys = service.get_unused_keys()
        return {"keys": keys, "count": len(keys)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usage/reset")
async def reset_usage_tracking(key: Optional[str] = Body(None, embed=True)):
    """
    Reset usage statistics.
    
    Args:
        key: Optional specific key to reset, or all if None
        
    Returns:
        Success confirmation
    """
    try:
        service.reset_usage_tracking(key)
        return {"success": True, "key": key or "all"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/set")
async def bulk_set(request: BulkSetRequest):
    """
    Set multiple key-value pairs at once.
    
    Args:
        request: Bulk set parameters
        
    Returns:
        Success confirmation
    """
    try:
        service.bulk_set(
            items=request.items,
            key_type=request.key_type,
            namespace=request.namespace
        )
        return {
            "success": True,
            "count": len(request.items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/get")
async def bulk_get(request: BulkGetRequest):
    """
    Get multiple values at once.
    
    Args:
        request: Bulk get parameters
        
    Returns:
        Dictionary of key-value pairs
    """
    try:
        values = service.bulk_get(request.keys)
        return {
            "values": values,
            "count": len(values)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/delete")
async def bulk_delete(request: BulkDeleteRequest):
    """
    Delete multiple keys at once.
    
    Args:
        request: Bulk delete parameters
        
    Returns:
        Number of keys deleted
    """
    try:
        count = service.bulk_delete(request.keys)
        return {
            "success": True,
            "deleted_count": count,
            "requested_count": len(request.keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_configuration(namespace: Optional[str] = Query(None)):
    """
    Export configuration to dictionary.
    
    Args:
        namespace: Optional namespace to export
        
    Returns:
        Configuration data
    """
    try:
        data = service.export_configuration(namespace)
        return {
            "namespace": namespace or "all",
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_configuration(
    data: Dict[str, Any] = Body(...),
    namespace: Optional[str] = Body(None, embed=True)
):
    """
    Import configuration from dictionary.
    
    Args:
        data: Configuration data
        namespace: Optional namespace to import into
        
    Returns:
        Success confirmation
    """
    try:
        service.import_configuration(data, namespace)
        return {
            "success": True,
            "namespace": namespace or "all",
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics():
    """
    Get comprehensive statistics about the key system.
    
    Returns:
        System statistics
    """
    try:
        stats = service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_all(namespace: Optional[str] = Query(None)):
    """
    Clear all data, optionally in a specific namespace.
    
    Args:
        namespace: Optional namespace to clear
        
    Returns:
        Success confirmation
    """
    try:
        service.clear_all(namespace)
        return {
            "success": True,
            "namespace": namespace or "all"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
