"""
Third-Party Integrations API Endpoints

Provides REST API endpoints for all third-party service integrations.

Requirements: 6.1
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from ...services.third_party_integration_service import (
    ThirdPartyIntegrationService,
    IntegrationError
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# Request/Response Models

class WeatherRequest(BaseModel):
    """Weather data request"""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")


class ForecastRequest(WeatherRequest):
    """Weather forecast request"""
    days: int = Field(7, ge=1, le=14, description="Number of days")


class HistoricalWeatherRequest(WeatherRequest):
    """Historical weather data request"""
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")


class GeocodeRequest(BaseModel):
    """Geocoding request"""
    address: str = Field(..., description="Address to geocode")


class ReverseGeocodeRequest(BaseModel):
    """Reverse geocoding request"""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")


class DistanceRequest(BaseModel):
    """Distance calculation request"""
    origin: Dict[str, float] = Field(..., description="Origin coordinates")
    destination: Dict[str, float] = Field(..., description="Destination coordinates")


class PaymentIntentRequest(BaseModel):
    """Payment intent creation request"""
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field("EUR", description="Currency code")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PaymentConfirmRequest(BaseModel):
    """Payment confirmation request"""
    payment_intent_id: str = Field(..., description="Payment intent ID")


class RefundRequest(BaseModel):
    """Refund request"""
    payment_intent_id: str = Field(..., description="Payment intent ID")
    amount: Optional[float] = Field(None, description="Refund amount")


class EmailRequest(BaseModel):
    """Email send request"""
    to_email: str = Field(..., description="Recipient email")
    subject: str = Field(..., description="Email subject")
    html_content: str = Field(..., description="HTML content")
    text_content: Optional[str] = Field(None, description="Plain text content")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Attachments")


class TemplateEmailRequest(BaseModel):
    """Template email request"""
    to_email: str = Field(..., description="Recipient email")
    template_id: str = Field(..., description="Template ID")
    template_data: Dict[str, Any] = Field(..., description="Template data")


class FileUploadRequest(BaseModel):
    """File upload request"""
    file_path: str = Field(..., description="File path in storage")
    file_data: str = Field(..., description="Base64 encoded file data")
    content_type: Optional[str] = Field(None, description="MIME type")
    metadata: Optional[Dict[str, str]] = Field(None, description="File metadata")


class FileDownloadRequest(BaseModel):
    """File download request"""
    file_path: str = Field(..., description="File path in storage")


class FileDeleteRequest(BaseModel):
    """File delete request"""
    file_path: str = Field(..., description="File path in storage")


class FileListRequest(BaseModel):
    """File list request"""
    prefix: Optional[str] = Field(None, description="Path prefix")


class AnalyticsEventRequest(BaseModel):
    """Analytics event tracking request"""
    category: str = Field(..., description="Event category")
    action: str = Field(..., description="Event action")
    label: Optional[str] = Field(None, description="Event label")
    value: Optional[int] = Field(None, description="Event value")
    user_id: Optional[str] = Field(None, description="User ID")


class PageViewRequest(BaseModel):
    """Page view tracking request"""
    page_path: str = Field(..., description="Page path")
    page_title: Optional[str] = Field(None, description="Page title")
    user_id: Optional[str] = Field(None, description="User ID")


class UserTrackingRequest(BaseModel):
    """User tracking request"""
    user_id: str = Field(..., description="User ID")
    properties: Optional[Dict[str, Any]] = Field(None, description="User properties")


# Dependency to get integration service
async def get_integration_service() -> ThirdPartyIntegrationService:
    """Get integration service instance"""
    # In production, this would load config from database or environment
    config = {
        'weather': {'enabled': True, 'provider': 'openweathermap'},
        'mapping': {'enabled': True, 'provider': 'google_maps'},
        'payment': {'enabled': True, 'provider': 'stripe'},
        'email': {'enabled': True, 'provider': 'sendgrid'},
        'cloud_storage': {'enabled': True, 'provider': 's3'},
        'analytics': {'enabled': True, 'provider': 'google_analytics'}
    }
    return ThirdPartyIntegrationService(config)


# Status Endpoints

@router.get("/status")
async def get_all_integration_status(
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Get status of all integrations"""
    try:
        return await service.get_all_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_all_integrations(
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Test all integration connections"""
    try:
        return await service.test_all_connections()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Weather API Endpoints

@router.post("/weather/current")
async def get_current_weather(
    request: WeatherRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Get current weather data"""
    try:
        result = await service.weather.get_current_weather(
            lat=request.lat,
            lon=request.lon
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Weather service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather/forecast")
async def get_weather_forecast(
    request: ForecastRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Get weather forecast"""
    try:
        result = await service.weather.get_forecast(
            lat=request.lat,
            lon=request.lon,
            days=request.days
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Weather service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather/historical")
async def get_historical_weather(
    request: HistoricalWeatherRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Get historical weather data"""
    try:
        result = await service.weather.get_historical_data(
            lat=request.lat,
            lon=request.lon,
            start_date=request.start_date,
            end_date=request.end_date
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Weather service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mapping API Endpoints

@router.post("/mapping/geocode")
async def geocode_address(
    request: GeocodeRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Convert address to coordinates"""
    try:
        result = await service.mapping.geocode(request.address)
        if result is None:
            raise HTTPException(status_code=503, detail="Mapping service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mapping/reverse-geocode")
async def reverse_geocode_coordinates(
    request: ReverseGeocodeRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Convert coordinates to address"""
    try:
        result = await service.mapping.reverse_geocode(
            lat=request.lat,
            lon=request.lon
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Mapping service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mapping/distance")
async def calculate_distance(
    request: DistanceRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Calculate distance between two points"""
    try:
        result = await service.mapping.get_distance(
            origin=request.origin,
            destination=request.destination
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Mapping service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Payment API Endpoints

@router.post("/payment/create-intent")
async def create_payment_intent(
    request: PaymentIntentRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Create a payment intent"""
    try:
        result = await service.payment.create_payment_intent(
            amount=request.amount,
            currency=request.currency,
            metadata=request.metadata
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Payment service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment/confirm")
async def confirm_payment(
    request: PaymentConfirmRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Confirm a payment"""
    try:
        result = await service.payment.confirm_payment(request.payment_intent_id)
        if result is None:
            raise HTTPException(status_code=503, detail="Payment service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment/refund")
async def refund_payment(
    request: RefundRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Refund a payment"""
    try:
        result = await service.payment.refund_payment(
            payment_intent_id=request.payment_intent_id,
            amount=request.amount
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Payment service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Email API Endpoints

@router.post("/email/send")
async def send_email(
    request: EmailRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Send an email"""
    try:
        result = await service.email.send_email(
            to_email=request.to_email,
            subject=request.subject,
            html_content=request.html_content,
            text_content=request.text_content,
            attachments=request.attachments
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Email service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/send-template")
async def send_template_email(
    request: TemplateEmailRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Send an email using a template"""
    try:
        result = await service.email.send_template_email(
            to_email=request.to_email,
            template_id=request.template_id,
            template_data=request.template_data
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Email service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Cloud Storage API Endpoints

@router.post("/storage/upload")
async def upload_file(
    request: FileUploadRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Upload a file to cloud storage"""
    try:
        import base64
        file_data = base64.b64decode(request.file_data)
        
        result = await service.cloud_storage.upload_file(
            file_path=request.file_path,
            file_data=file_data,
            content_type=request.content_type,
            metadata=request.metadata
        )
        if result is None:
            raise HTTPException(status_code=503, detail="Storage service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/storage/download")
async def download_file(
    request: FileDownloadRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Download a file from cloud storage"""
    try:
        result = await service.cloud_storage.download_file(request.file_path)
        if result is None:
            raise HTTPException(status_code=503, detail="Storage service not available")
        
        import base64
        return {
            'file_path': request.file_path,
            'file_data': base64.b64encode(result).decode('utf-8')
        }
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/storage/delete")
async def delete_file(
    request: FileDeleteRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Delete a file from cloud storage"""
    try:
        result = await service.cloud_storage.delete_file(request.file_path)
        return {'success': result, 'file_path': request.file_path}
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/storage/list")
async def list_files(
    request: FileListRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """List files in cloud storage"""
    try:
        result = await service.cloud_storage.list_files(prefix=request.prefix)
        if result is None:
            raise HTTPException(status_code=503, detail="Storage service not available")
        return result
    except IntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analytics API Endpoints

@router.post("/analytics/event")
async def track_event(
    request: AnalyticsEventRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Track an analytics event"""
    try:
        result = await service.analytics.track_event(
            category=request.category,
            action=request.action,
            label=request.label,
            value=request.value,
            user_id=request.user_id
        )
        return {'success': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/page-view")
async def track_page_view(
    request: PageViewRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Track a page view"""
    try:
        result = await service.analytics.track_page_view(
            page_path=request.page_path,
            page_title=request.page_title,
            user_id=request.user_id
        )
        return {'success': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/user")
async def track_user(
    request: UserTrackingRequest,
    service: ThirdPartyIntegrationService = Depends(get_integration_service)
):
    """Track user properties"""
    try:
        result = await service.analytics.track_user(
            user_id=request.user_id,
            properties=request.properties
        )
        return {'success': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
