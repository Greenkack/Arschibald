"""
Pydantic schemas for API Integration
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntegrationType(str, Enum):
    """Types of API integrations"""
    REST = "rest"
    GRAPHQL = "graphql"
    SOAP = "soap"
    WEBHOOK = "webhook"


class AuthType(str, Enum):
    """Authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH2 = "oauth2"


class OAuthConfigSchema(BaseModel):
    """OAuth 2.0 configuration"""
    client_id: str
    client_secret: str
    authorization_url: HttpUrl
    token_url: HttpUrl
    redirect_uri: HttpUrl
    scope: List[str] = []
    token_type: str = "Bearer"


class WebhookConfigSchema(BaseModel):
    """Webhook configuration"""
    url: HttpUrl
    secret: str
    events: List[str] = []
    retry_attempts: int = Field(default=3, ge=1, le=10)
    timeout: int = Field(default=10, ge=1, le=60)


class RateLimitConfigSchema(BaseModel):
    """Rate limiting configuration"""
    calls: int = Field(default=100, ge=1)
    period: int = Field(default=60, ge=1)  # seconds


class CacheConfigSchema(BaseModel):
    """Cache configuration"""
    enabled: bool = True
    ttl: int = Field(default=300, ge=0)  # seconds


class APIIntegrationBase(BaseModel):
    """Base schema for API integration"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    integration_type: IntegrationType
    base_url: HttpUrl
    auth_type: AuthType
    enabled: bool = True
    timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=1, ge=0, le=60)


class APIIntegrationCreate(APIIntegrationBase):
    """Schema for creating API integration"""
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bearer_token: Optional[str] = None
    oauth_config: Optional[OAuthConfigSchema] = None
    webhook_config: Optional[WebhookConfigSchema] = None
    rate_limit_config: Optional[RateLimitConfigSchema] = None
    cache_config: Optional[CacheConfigSchema] = None
    custom_headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class APIIntegrationUpdate(BaseModel):
    """Schema for updating API integration"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    enabled: Optional[bool] = None
    timeout: Optional[int] = Field(None, ge=1, le=300)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay: Optional[int] = Field(None, ge=0, le=60)
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bearer_token: Optional[str] = None
    oauth_config: Optional[OAuthConfigSchema] = None
    webhook_config: Optional[WebhookConfigSchema] = None
    rate_limit_config: Optional[RateLimitConfigSchema] = None
    cache_config: Optional[CacheConfigSchema] = None
    custom_headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class APIIntegrationResponse(APIIntegrationBase):
    """Schema for API integration response"""
    id: int
    api_key: Optional[str] = None
    username: Optional[str] = None
    oauth_config: Optional[OAuthConfigSchema] = None
    webhook_config: Optional[WebhookConfigSchema] = None
    rate_limit_config: Optional[RateLimitConfigSchema] = None
    cache_config: Optional[CacheConfigSchema] = None
    custom_headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    has_valid_token: bool = False
    token_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OAuthAuthorizationRequest(BaseModel):
    """Request for OAuth authorization URL"""
    state: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request"""
    code: str
    state: Optional[str] = None


class WebhookTestRequest(BaseModel):
    """Request to test webhook"""
    event: str
    data: Dict[str, Any] = {}


class APIMetricsResponse(BaseModel):
    """API metrics response"""
    integration_id: int
    total_calls: int
    successful_calls: int
    failed_calls: int
    average_duration: float
    success_rate: float
    total_duration: float
    errors: List[Dict[str, Any]]
    last_call_at: Optional[datetime] = None


class WebhookDeliveryStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery history response"""
    id: int
    integration_id: int
    event: str
    payload: Dict[str, Any]
    status: WebhookDeliveryStatus
    attempts: int
    last_attempt_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class APITestResult(BaseModel):
    """API integration test result"""
    success: bool
    message: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
