"""
Service for managing API integrations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.models.api_integration_models import (
    APIIntegration,
    WebhookDelivery,
    APICallLog,
    WebhookDeliveryStatus
)
from backend.models.api_integration_schemas import (
    APIIntegrationCreate,
    APIIntegrationUpdate,
    APIIntegrationResponse,
    APIMetricsResponse,
    WebhookDeliveryResponse,
    APITestResult
)
from backend.core.api_client import (
    APIClient,
    APIClientConfig,
    OAuthConfig,
    WebhookConfig
)

logger = logging.getLogger(__name__)


class APIIntegrationService:
    """Service for managing API integrations"""
    
    def __init__(self, db: Session):
        self.db = db
        self._clients: Dict[int, APIClient] = {}
    
    def _get_client(self, integration: APIIntegration) -> APIClient:
        """Get or create API client for integration"""
        if integration.id in self._clients:
            return self._clients[integration.id]
        
        # Create client config
        config = APIClientConfig(
            base_url=str(integration.base_url),
            timeout=integration.timeout,
            max_retries=integration.max_retries,
            retry_delay=integration.retry_delay,
            rate_limit_calls=integration.rate_limit_config.get('calls', 100) if integration.rate_limit_config else 100,
            rate_limit_period=integration.rate_limit_config.get('period', 60) if integration.rate_limit_config else 60,
            cache_ttl=integration.cache_config.get('ttl', 300) if integration.cache_config else 300,
            enable_monitoring=True
        )
        
        # Create OAuth config if applicable
        oauth_config = None
        if integration.auth_type.value == 'oauth2' and integration.oauth_config:
            oauth_config = OAuthConfig(**integration.oauth_config)
            # Restore tokens if available
            if integration.oauth_access_token:
                oauth_config.access_token = integration.oauth_access_token
                oauth_config.refresh_token = integration.oauth_refresh_token
                oauth_config.token_expires_at = integration.oauth_token_expires_at
        
        # Create webhook config if applicable
        webhook_config = None
        if integration.webhook_config:
            webhook_config = WebhookConfig(**integration.webhook_config)
        
        # Create and cache client
        client = APIClient(config, oauth_config, webhook_config)
        self._clients[integration.id] = client
        
        return client
    
    async def create_integration(self, data: APIIntegrationCreate) -> APIIntegrationResponse:
        """Create new API integration"""
        integration = APIIntegration(
            name=data.name,
            description=data.description,
            integration_type=data.integration_type,
            base_url=str(data.base_url),
            auth_type=data.auth_type,
            enabled=data.enabled,
            timeout=data.timeout,
            max_retries=data.max_retries,
            retry_delay=data.retry_delay,
            api_key=data.api_key,
            username=data.username,
            password=data.password,
            bearer_token=data.bearer_token,
            oauth_config=data.oauth_config.dict() if data.oauth_config else None,
            webhook_config=data.webhook_config.dict() if data.webhook_config else None,
            rate_limit_config=data.rate_limit_config.dict() if data.rate_limit_config else None,
            cache_config=data.cache_config.dict() if data.cache_config else None,
            custom_headers=data.custom_headers,
            metadata=data.metadata
        )
        
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        
        logger.info(f"Created API integration: {integration.name} (ID: {integration.id})")
        
        return APIIntegrationResponse.from_orm(integration)
    
    async def list_integrations(self, skip: int = 0, limit: int = 100) -> List[APIIntegrationResponse]:
        """List all API integrations"""
        integrations = self.db.query(APIIntegration).offset(skip).limit(limit).all()
        return [APIIntegrationResponse.from_orm(i) for i in integrations]
    
    async def get_integration(self, integration_id: int) -> Optional[APIIntegrationResponse]:
        """Get specific API integration"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if integration:
            return APIIntegrationResponse.from_orm(integration)
        return None
    
    async def update_integration(
        self,
        integration_id: int,
        data: APIIntegrationUpdate
    ) -> Optional[APIIntegrationResponse]:
        """Update API integration"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(integration, field):
                if field in ['oauth_config', 'webhook_config', 'rate_limit_config', 'cache_config']:
                    setattr(integration, field, value.dict() if value else None)
                else:
                    setattr(integration, field, value)
        
        self.db.commit()
        self.db.refresh(integration)
        
        # Clear cached client
        if integration_id in self._clients:
            del self._clients[integration_id]
        
        logger.info(f"Updated API integration: {integration.name} (ID: {integration.id})")
        
        return APIIntegrationResponse.from_orm(integration)
    
    async def delete_integration(self, integration_id: int) -> bool:
        """Delete API integration"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            return False
        
        self.db.delete(integration)
        self.db.commit()
        
        # Clear cached client
        if integration_id in self._clients:
            del self._clients[integration_id]
        
        logger.info(f"Deleted API integration ID: {integration_id}")
        
        return True
    
    async def get_oauth_authorization_url(self, integration_id: int, state: Optional[str] = None) -> str:
        """Get OAuth authorization URL"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration or integration.auth_type.value != 'oauth2':
            raise ValueError("Integration not found or not OAuth2 type")
        
        client = self._get_client(integration)
        if not client.oauth_client:
            raise ValueError("OAuth not configured for this integration")
        
        return client.oauth_client.get_authorization_url(state)
    
    async def handle_oauth_callback(self, integration_id: int, code: str) -> Dict[str, Any]:
        """Handle OAuth callback and store tokens"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            raise ValueError("Integration not found")
        
        client = self._get_client(integration)
        if not client.oauth_client:
            raise ValueError("OAuth not configured for this integration")
        
        # Exchange code for tokens
        tokens = await client.oauth_client.exchange_code(code)
        
        # Store tokens in database
        integration.oauth_access_token = tokens.get('access_token')
        integration.oauth_refresh_token = tokens.get('refresh_token')
        if 'expires_in' in tokens:
            from datetime import timedelta
            integration.oauth_token_expires_at = datetime.now() + timedelta(seconds=tokens['expires_in'])
        
        self.db.commit()
        
        logger.info(f"OAuth tokens stored for integration ID: {integration_id}")
        
        return tokens
    
    async def refresh_oauth_token(self, integration_id: int) -> Dict[str, Any]:
        """Refresh OAuth access token"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            raise ValueError("Integration not found")
        
        client = self._get_client(integration)
        if not client.oauth_client:
            raise ValueError("OAuth not configured for this integration")
        
        # Refresh token
        tokens = await client.oauth_client.refresh_access_token()
        
        # Update tokens in database
        integration.oauth_access_token = tokens.get('access_token')
        if 'refresh_token' in tokens:
            integration.oauth_refresh_token = tokens['refresh_token']
        if 'expires_in' in tokens:
            from datetime import timedelta
            integration.oauth_token_expires_at = datetime.now() + timedelta(seconds=tokens['expires_in'])
        
        self.db.commit()
        
        logger.info(f"OAuth token refreshed for integration ID: {integration_id}")
        
        return tokens
    
    async def test_integration(self, integration_id: int) -> APITestResult:
        """Test API integration connection"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            return APITestResult(success=False, message="Integration not found")
        
        try:
            client = self._get_client(integration)
            
            # Try a simple GET request to test connection
            import time
            start_time = time.time()
            
            # Most APIs have a health or status endpoint
            response = await client.get("/health", use_cache=False)
            
            response_time = time.time() - start_time
            
            # Update last used timestamp
            integration.last_used_at = datetime.now()
            self.db.commit()
            
            return APITestResult(
                success=True,
                message="Connection successful",
                response_time=response_time,
                status_code=200
            )
        
        except Exception as e:
            logger.error(f"Integration test failed for ID {integration_id}: {str(e)}")
            return APITestResult(
                success=False,
                message="Connection failed",
                error=str(e)
            )
    
    async def test_webhook(self, integration_id: int, event: str, data: Dict[str, Any]) -> bool:
        """Test webhook delivery"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            return False
        
        client = self._get_client(integration)
        success = await client.send_webhook(event, data)
        
        # Log webhook delivery
        delivery = WebhookDelivery(
            integration_id=integration_id,
            event=event,
            payload=data,
            status=WebhookDeliveryStatus.DELIVERED if success else WebhookDeliveryStatus.FAILED,
            attempts=1,
            last_attempt_at=datetime.now(),
            delivered_at=datetime.now() if success else None
        )
        self.db.add(delivery)
        self.db.commit()
        
        return success
    
    async def get_metrics(self, integration_id: int) -> Optional[APIMetricsResponse]:
        """Get API integration metrics"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            return None
        
        client = self._get_client(integration)
        metrics = await client.get_metrics()
        
        if not metrics:
            return None
        
        return APIMetricsResponse(
            integration_id=integration_id,
            **metrics,
            last_call_at=integration.last_used_at
        )
    
    async def clear_cache(self, integration_id: int):
        """Clear API cache"""
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if integration:
            client = self._get_client(integration)
            await client.clear_cache()
            logger.info(f"Cache cleared for integration ID: {integration_id}")
    
    async def reset_rate_limit(self, integration_id: int):
        """Reset rate limiter"""
        if integration_id in self._clients:
            del self._clients[integration_id]
            logger.info(f"Rate limiter reset for integration ID: {integration_id}")
    
    async def list_webhook_history(
        self,
        integration_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[WebhookDeliveryResponse]:
        """List webhook delivery history"""
        deliveries = (
            self.db.query(WebhookDelivery)
            .filter(WebhookDelivery.integration_id == integration_id)
            .order_by(desc(WebhookDelivery.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [WebhookDeliveryResponse.from_orm(d) for d in deliveries]
    
    async def retry_webhook(self, integration_id: int, webhook_id: int) -> bool:
        """Retry failed webhook delivery"""
        delivery = (
            self.db.query(WebhookDelivery)
            .filter(
                WebhookDelivery.id == webhook_id,
                WebhookDelivery.integration_id == integration_id
            )
            .first()
        )
        
        if not delivery:
            return False
        
        integration = self.db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
        if not integration:
            return False
        
        client = self._get_client(integration)
        success = await client.send_webhook(delivery.event, delivery.payload)
        
        # Update delivery record
        delivery.attempts += 1
        delivery.last_attempt_at = datetime.now()
        if success:
            delivery.status = WebhookDeliveryStatus.DELIVERED
            delivery.delivered_at = datetime.now()
        else:
            delivery.status = WebhookDeliveryStatus.FAILED
        
        self.db.commit()
        
        return success
