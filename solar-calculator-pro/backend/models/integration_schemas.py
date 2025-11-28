"""
Integration Configuration Schemas

Pydantic models for third-party integration configurations.

Requirements: 6.1
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class IntegrationConfigBase(BaseModel):
    """Base configuration for all integrations"""
    enabled: bool = Field(True, description="Whether integration is enabled")
    api_key: Optional[str] = Field(None, description="API key")
    base_url: Optional[str] = Field(None, description="Base URL for API")


class WeatherConfig(IntegrationConfigBase):
    """Weather API configuration"""
    provider: str = Field("openweathermap", description="Weather provider")
    units: str = Field("metric", description="Units (metric/imperial)")
    language: str = Field("de", description="Language code")
    cache_duration: int = Field(3600, description="Cache duration in seconds")


class MappingConfig(IntegrationConfigBase):
    """Mapping API configuration"""
    provider: str = Field("google_maps", description="Mapping provider")
    region: str = Field("DE", description="Region code")
    language: str = Field("de", description="Language code")


class PaymentConfig(IntegrationConfigBase):
    """Payment gateway configuration"""
    provider: str = Field("stripe", description="Payment provider")
    secret_key: Optional[str] = Field(None, description="Secret key")
    publishable_key: Optional[str] = Field(None, description="Publishable key")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret")
    currency: str = Field("EUR", description="Default currency")
    test_mode: bool = Field(True, description="Test mode enabled")


class EmailConfig(IntegrationConfigBase):
    """Email service configuration"""
    provider: str = Field("sendgrid", description="Email provider")
    from_email: str = Field(..., description="From email address")
    from_name: str = Field(..., description="From name")
    reply_to: Optional[str] = Field(None, description="Reply-to email")
    smtp_host: Optional[str] = Field(None, description="SMTP host")
    smtp_port: Optional[int] = Field(None, description="SMTP port")
    smtp_username: Optional[str] = Field(None, description="SMTP username")
    smtp_password: Optional[str] = Field(None, description="SMTP password")
    use_tls: bool = Field(True, description="Use TLS")


class CloudStorageConfig(IntegrationConfigBase):
    """Cloud storage configuration"""
    provider: str = Field("s3", description="Storage provider")
    bucket: str = Field(..., description="Bucket name")
    region: str = Field("eu-central-1", description="Region")
    access_key_id: Optional[str] = Field(None, description="Access key ID")
    secret_access_key: Optional[str] = Field(None, description="Secret access key")
    endpoint_url: Optional[str] = Field(None, description="Custom endpoint URL")
    public_url: Optional[str] = Field(None, description="Public URL base")


class AnalyticsConfig(IntegrationConfigBase):
    """Analytics configuration"""
    provider: str = Field("google_analytics", description="Analytics provider")
    tracking_id: str = Field(..., description="Tracking ID")
    measurement_id: Optional[str] = Field(None, description="Measurement ID (GA4)")
    api_secret: Optional[str] = Field(None, description="API secret (GA4)")
    anonymize_ip: bool = Field(True, description="Anonymize IP addresses")
    track_user_id: bool = Field(True, description="Track user IDs")


class IntegrationSettings(BaseModel):
    """Complete integration settings"""
    weather: WeatherConfig
    mapping: MappingConfig
    payment: PaymentConfig
    email: EmailConfig
    cloud_storage: CloudStorageConfig
    analytics: AnalyticsConfig
    
    class Config:
        schema_extra = {
            "example": {
                "weather": {
                    "enabled": True,
                    "provider": "openweathermap",
                    "api_key": "your_api_key",
                    "units": "metric",
                    "language": "de"
                },
                "mapping": {
                    "enabled": True,
                    "provider": "google_maps",
                    "api_key": "your_api_key",
                    "region": "DE"
                },
                "payment": {
                    "enabled": True,
                    "provider": "stripe",
                    "secret_key": "sk_test_...",
                    "publishable_key": "pk_test_...",
                    "test_mode": True
                },
                "email": {
                    "enabled": True,
                    "provider": "sendgrid",
                    "api_key": "your_api_key",
                    "from_email": "noreply@example.com",
                    "from_name": "Solar Calculator Pro"
                },
                "cloud_storage": {
                    "enabled": True,
                    "provider": "s3",
                    "bucket": "solar-calculator-files",
                    "region": "eu-central-1"
                },
                "analytics": {
                    "enabled": True,
                    "provider": "google_analytics",
                    "tracking_id": "UA-XXXXXXXXX-X"
                }
            }
        }


class IntegrationStatus(BaseModel):
    """Integration status response"""
    provider: str
    enabled: bool
    connected: bool
    last_check: datetime
    additional_info: Optional[Dict[str, Any]] = None


class IntegrationTestResult(BaseModel):
    """Integration connection test result"""
    integration: str
    success: bool
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class IntegrationHealthCheck(BaseModel):
    """Health check for all integrations"""
    weather: IntegrationStatus
    mapping: IntegrationStatus
    payment: IntegrationStatus
    email: IntegrationStatus
    cloud_storage: IntegrationStatus
    analytics: IntegrationStatus
    overall_status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime = Field(default_factory=datetime.now)
