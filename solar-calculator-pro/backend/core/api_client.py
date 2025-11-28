"""
API Client Framework for External Integrations
Provides a unified interface for OAuth, webhooks, rate limiting, caching, and monitoring
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urlencode
import aiohttp
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class APIClientConfig(BaseModel):
    """Configuration for API client"""
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds
    cache_ttl: int = 300  # seconds
    enable_monitoring: bool = True


class OAuthConfig(BaseModel):
    """OAuth 2.0 configuration"""
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    redirect_uri: str
    scope: List[str] = []
    token_type: str = "Bearer"


class WebhookConfig(BaseModel):
    """Webhook configuration"""
    url: str
    secret: str
    events: List[str] = []
    retry_attempts: int = 3
    timeout: int = 10


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.tokens = calls
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Refill tokens based on elapsed time
            self.tokens = min(
                self.calls,
                self.tokens + (elapsed * self.calls / self.period)
            )
            self.last_update = now
            
            if self.tokens < 1:
                # Wait until we have a token
                wait_time = (1 - self.tokens) * self.period / self.calls
                await asyncio.sleep(wait_time)
                self.tokens = 1
            
            self.tokens -= 1


class APICache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.lock = asyncio.Lock()
    
    def _generate_key(self, method: str, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key"""
        key_data = f"{method}:{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, method: str, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get cached response"""
        async with self.lock:
            key = self._generate_key(method, url, params)
            if key in self.cache:
                data, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    logger.debug(f"Cache hit for {method} {url}")
                    return data
                else:
                    del self.cache[key]
        return None
    
    async def set(self, method: str, url: str, params: Optional[Dict], data: Any):
        """Cache response"""
        async with self.lock:
            key = self._generate_key(method, url, params)
            self.cache[key] = (data, time.time())
            logger.debug(f"Cached response for {method} {url}")
    
    async def clear(self):
        """Clear all cache"""
        async with self.lock:
            self.cache.clear()


class APIMonitor:
    """Monitor API calls and performance"""
    
    def __init__(self):
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_duration': 0.0,
            'errors': []
        }
        self.lock = asyncio.Lock()
    
    async def record_call(self, method: str, url: str, duration: float, success: bool, error: Optional[str] = None):
        """Record API call metrics"""
        async with self.lock:
            self.metrics['total_calls'] += 1
            self.metrics['total_duration'] += duration
            
            if success:
                self.metrics['successful_calls'] += 1
            else:
                self.metrics['failed_calls'] += 1
                if error:
                    self.metrics['errors'].append({
                        'timestamp': datetime.now().isoformat(),
                        'method': method,
                        'url': url,
                        'error': error
                    })
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        async with self.lock:
            avg_duration = (
                self.metrics['total_duration'] / self.metrics['total_calls']
                if self.metrics['total_calls'] > 0 else 0
            )
            
            return {
                **self.metrics,
                'average_duration': avg_duration,
                'success_rate': (
                    self.metrics['successful_calls'] / self.metrics['total_calls']
                    if self.metrics['total_calls'] > 0 else 0
                )
            }


class OAuthClient:
    """OAuth 2.0 client implementation"""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get OAuth authorization URL"""
        params = {
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.config.scope)
        }
        if state:
            params['state'] = state
        
        return f"{self.config.authorization_url}?{urlencode(params)}"
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.config.redirect_uri,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            async with session.post(self.config.token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self._store_tokens(token_data)
                    return token_data
                else:
                    error = await response.text()
                    raise Exception(f"Token exchange failed: {error}")
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            async with session.post(self.config.token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self._store_tokens(token_data)
                    return token_data
                else:
                    error = await response.text()
                    raise Exception(f"Token refresh failed: {error}")
    
    def _store_tokens(self, token_data: Dict[str, Any]):
        """Store tokens from response"""
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token', self.refresh_token)
        
        if 'expires_in' in token_data:
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
    
    async def is_token_valid(self) -> bool:
        """Check if access token is still valid"""
        if not self.access_token:
            return False
        
        if self.token_expires_at:
            # Refresh 5 minutes before expiry
            return datetime.now() < (self.token_expires_at - timedelta(minutes=5))
        
        return True
    
    async def get_valid_token(self) -> str:
        """Get valid access token, refreshing if necessary"""
        if not await self.is_token_valid():
            if self.refresh_token:
                await self.refresh_access_token()
            else:
                raise Exception("No valid token and no refresh token available")
        
        return self.access_token


class WebhookManager:
    """Webhook management and delivery"""
    
    def __init__(self, config: WebhookConfig):
        self.config = config
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook"""
        import hmac
        signature = hmac.new(
            self.config.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    async def send_webhook(self, event: str, data: Dict[str, Any]) -> bool:
        """Send webhook with retry logic"""
        if event not in self.config.events:
            logger.warning(f"Event {event} not configured for webhooks")
            return False
        
        payload = json.dumps({
            'event': event,
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        signature = self._generate_signature(payload)
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-Event': event
        }
        
        for attempt in range(self.config.retry_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.config.url,
                        data=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                    ) as response:
                        if response.status in [200, 201, 202, 204]:
                            logger.info(f"Webhook delivered successfully for event {event}")
                            return True
                        else:
                            logger.warning(f"Webhook delivery failed with status {response.status}")
            except Exception as e:
                logger.error(f"Webhook delivery attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature)


class APIClient:
    """Unified API client with OAuth, rate limiting, caching, and monitoring"""
    
    def __init__(
        self,
        config: APIClientConfig,
        oauth_config: Optional[OAuthConfig] = None,
        webhook_config: Optional[WebhookConfig] = None
    ):
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_calls, config.rate_limit_period)
        self.cache = APICache(config.cache_ttl)
        self.monitor = APIMonitor() if config.enable_monitoring else None
        self.oauth_client = OAuthClient(oauth_config) if oauth_config else None
        self.webhook_manager = WebhookManager(webhook_config) if webhook_config else None
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get request headers including OAuth token if configured"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SolarCalculatorPro/1.0'
        }
        
        if self.oauth_client:
            token = await self.oauth_client.get_valid_token()
            headers['Authorization'] = f"{self.oauth_client.config.token_type} {token}"
        
        return headers
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True,
        bypass_rate_limit: bool = False
    ) -> Dict[str, Any]:
        """Make API request with rate limiting, caching, and monitoring"""
        url = f"{self.config.base_url}{endpoint}"
        
        # Check cache for GET requests
        if method.upper() == 'GET' and use_cache:
            cached = await self.cache.get(method, url, params)
            if cached is not None:
                return cached
        
        # Apply rate limiting
        if not bypass_rate_limit:
            await self.rate_limiter.acquire()
        
        # Make request with retry logic
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                headers = await self._get_headers()
                
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        params=params,
                        json=data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                    ) as response:
                        duration = time.time() - start_time
                        
                        if response.status >= 200 and response.status < 300:
                            result = await response.json()
                            
                            # Cache successful GET requests
                            if method.upper() == 'GET' and use_cache:
                                await self.cache.set(method, url, params, result)
                            
                            # Record metrics
                            if self.monitor:
                                await self.monitor.record_call(method, url, duration, True)
                            
                            return result
                        else:
                            error_text = await response.text()
                            last_error = f"HTTP {response.status}: {error_text}"
                            logger.warning(f"Request failed: {last_error}")
                            
                            # Don't retry client errors (4xx)
                            if 400 <= response.status < 500:
                                break
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Request attempt {attempt + 1} failed: {last_error}")
            
            # Wait before retry
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
        
        # Record failure
        duration = time.time() - start_time
        if self.monitor:
            await self.monitor.record_call(method, url, duration, False, last_error)
        
        raise Exception(f"Request failed after {self.config.max_retries} attempts: {last_error}")
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self.request('GET', endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self.request('POST', endpoint, data=data, use_cache=False, **kwargs)
    
    async def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return await self.request('PUT', endpoint, data=data, use_cache=False, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return await self.request('DELETE', endpoint, use_cache=False, **kwargs)
    
    async def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get API monitoring metrics"""
        if self.monitor:
            return await self.monitor.get_metrics()
        return None
    
    async def clear_cache(self):
        """Clear API cache"""
        await self.cache.clear()
    
    async def send_webhook(self, event: str, data: Dict[str, Any]) -> bool:
        """Send webhook if configured"""
        if self.webhook_manager:
            return await self.webhook_manager.send_webhook(event, data)
        return False
