"""
API Integration endpoints for managing external API connections
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.core.database import get_db
from backend.core.api_client import (
    APIClient,
    APIClientConfig,
    OAuthConfig,
    WebhookConfig
)
from backend.services.api_integration_service import APIIntegrationService
from backend.models.api_integration_schemas import (
    APIIntegrationCreate,
    APIIntegrationUpdate,
    APIIntegrationResponse,
    OAuthAuthorizationRequest,
    OAuthCallbackRequest,
    WebhookTestRequest,
    APIMetricsResponse
)

router = APIRouter(prefix="/api-integration", tags=["API Integration"])


@router.post("/", response_model=APIIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_api_integration(
    integration: APIIntegrationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new API integration configuration
    """
    service = APIIntegrationService(db)
    return await service.create_integration(integration)


@router.get("/", response_model=List[APIIntegrationResponse])
async def list_api_integrations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all API integrations
    """
    service = APIIntegrationService(db)
    return await service.list_integrations(skip, limit)


@router.get("/{integration_id}", response_model=APIIntegrationResponse)
async def get_api_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific API integration by ID
    """
    service = APIIntegrationService(db)
    integration = await service.get_integration(integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API integration not found"
        )
    return integration


@router.put("/{integration_id}", response_model=APIIntegrationResponse)
async def update_api_integration(
    integration_id: int,
    integration: APIIntegrationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update API integration configuration
    """
    service = APIIntegrationService(db)
    updated = await service.update_integration(integration_id, integration)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API integration not found"
        )
    return updated


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete API integration
    """
    service = APIIntegrationService(db)
    success = await service.delete_integration(integration_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API integration not found"
        )


@router.post("/{integration_id}/oauth/authorize")
async def get_oauth_authorization_url(
    integration_id: int,
    request: OAuthAuthorizationRequest,
    db: Session = Depends(get_db)
):
    """
    Get OAuth authorization URL for user to authorize the integration
    """
    service = APIIntegrationService(db)
    url = await service.get_oauth_authorization_url(integration_id, request.state)
    return {"authorization_url": url}


@router.post("/{integration_id}/oauth/callback")
async def handle_oauth_callback(
    integration_id: int,
    callback: OAuthCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback and exchange code for tokens
    """
    service = APIIntegrationService(db)
    tokens = await service.handle_oauth_callback(integration_id, callback.code)
    return tokens


@router.post("/{integration_id}/oauth/refresh")
async def refresh_oauth_token(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """
    Refresh OAuth access token
    """
    service = APIIntegrationService(db)
    tokens = await service.refresh_oauth_token(integration_id)
    return tokens


@router.post("/{integration_id}/test")
async def test_api_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """
    Test API integration connection
    """
    service = APIIntegrationService(db)
    result = await service.test_integration(integration_id)
    return result


@router.post("/{integration_id}/webhook/test")
async def test_webhook(
    integration_id: int,
    test_request: WebhookTestRequest,
    db: Session = Depends(get_db)
):
    """
    Test webhook delivery
    """
    service = APIIntegrationService(db)
    success = await service.test_webhook(integration_id, test_request.event, test_request.data)
    return {"success": success}


@router.get("/{integration_id}/metrics", response_model=APIMetricsResponse)
async def get_api_metrics(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """
    Get API integration metrics
    """
    service = APIIntegrationService(db)
    metrics = await service.get_metrics(integration_id)
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics available for this integration"
        )
    return metrics


@router.post("/{integration_id}/cache/clear")
async def clear_api_cache(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """
    Clear API cache for this integration
    """
    service = APIIntegrationService(db)
    await service.clear_cache(integration_id)
    return {"message": "Cache cleared successfully"}


@router.post("/{integration_id}/rate-limit/reset")
async def reset_rate_limit(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """
    Reset rate limiter for this integration
    """
    service = APIIntegrationService(db)
    await service.reset_rate_limit(integration_id)
    return {"message": "Rate limit reset successfully"}


@router.get("/{integration_id}/webhooks")
async def list_webhooks(
    integration_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List webhook delivery history
    """
    service = APIIntegrationService(db)
    webhooks = await service.list_webhook_history(integration_id, skip, limit)
    return webhooks


@router.post("/{integration_id}/webhooks/{webhook_id}/retry")
async def retry_webhook(
    integration_id: int,
    webhook_id: int,
    db: Session = Depends(get_db)
):
    """
    Retry failed webhook delivery
    """
    service = APIIntegrationService(db)
    success = await service.retry_webhook(integration_id, webhook_id)
    return {"success": success}
