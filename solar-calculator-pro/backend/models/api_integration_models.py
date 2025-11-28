"""
Database models for API Integration
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from backend.core.database import Base


class IntegrationType(str, enum.Enum):
    """Types of API integrations"""
    REST = "rest"
    GRAPHQL = "graphql"
    SOAP = "soap"
    WEBHOOK = "webhook"


class AuthType(str, enum.Enum):
    """Authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH2 = "oauth2"


class WebhookDeliveryStatus(str, enum.Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class APIIntegration(Base):
    """API Integration configuration"""
    __tablename__ = "api_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    integration_type = Column(SQLEnum(IntegrationType), nullable=False)
    base_url = Column(String(500), nullable=False)
    auth_type = Column(SQLEnum(AuthType), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    
    # Connection settings
    timeout = Column(Integer, default=30, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delay = Column(Integer, default=1, nullable=False)
    
    # Authentication credentials (encrypted in production)
    api_key = Column(String(500), nullable=True)
    username = Column(String(100), nullable=True)
    password = Column(String(500), nullable=True)
    bearer_token = Column(Text, nullable=True)
    
    # OAuth configuration
    oauth_config = Column(JSON, nullable=True)
    oauth_access_token = Column(Text, nullable=True)
    oauth_refresh_token = Column(Text, nullable=True)
    oauth_token_expires_at = Column(DateTime, nullable=True)
    
    # Webhook configuration
    webhook_config = Column(JSON, nullable=True)
    
    # Rate limiting configuration
    rate_limit_config = Column(JSON, nullable=True)
    
    # Cache configuration
    cache_config = Column(JSON, nullable=True)
    
    # Custom headers
    custom_headers = Column(JSON, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime, nullable=True)


class WebhookDelivery(Base):
    """Webhook delivery history"""
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, nullable=False, index=True)
    event = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(SQLEnum(WebhookDeliveryStatus), default=WebhookDeliveryStatus.PENDING, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class APICallLog(Base):
    """API call logging for monitoring"""
    __tablename__ = "api_call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, nullable=False, index=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=False)  # milliseconds
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    request_params = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
