"""
Production Server Configuration
Task 76: Configure production server, SSL, reverse proxy, and monitoring
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum
import os


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SSLConfig(BaseModel):
    """SSL/TLS Configuration"""
    enabled: bool = True
    cert_path: str = "/etc/ssl/certs/solar-calculator.crt"
    key_path: str = "/etc/ssl/private/solar-calculator.key"
    ca_bundle_path: Optional[str] = "/etc/ssl/certs/ca-bundle.crt"
    min_tls_version: str = "TLSv1.2"
    cipher_suites: List[str] = [
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384"
    ]
    hsts_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year


class ReverseProxyConfig(BaseModel):
    """Reverse Proxy (Nginx) Configuration"""
    upstream_servers: List[str] = ["127.0.0.1:8000"]
    worker_processes: int = 4
    worker_connections: int = 1024
    keepalive_timeout: int = 65
    client_max_body_size: str = "100M"
    proxy_read_timeout: int = 300
    proxy_connect_timeout: int = 60
    proxy_send_timeout: int = 300
    gzip_enabled: bool = True
    gzip_types: List[str] = [
        "text/plain",
        "text/css",
        "application/json",
        "application/javascript",
        "text/xml",
        "application/xml"
    ]
    rate_limiting_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: str = "1m"


class DatabaseConfig(BaseModel):
    """Production Database Configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "solar_calculator"
    username: str = "solar_app"
    password: str = ""  # Set via environment variable
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    ssl_mode: str = "require"
    connection_timeout: int = 10


class RedisConfig(BaseModel):
    """Redis Cache Configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 50
    socket_timeout: int = 5
    ssl: bool = False


class MonitoringConfig(BaseModel):
    """Monitoring and Alerting Configuration"""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    grafana_enabled: bool = True
    grafana_port: int = 3000
    alertmanager_enabled: bool = True
    alertmanager_port: int = 9093
    log_level: str = "INFO"
    log_format: str = "json"
    log_retention_days: int = 30
    metrics_retention_days: int = 90
    health_check_interval: int = 30
    alert_email: Optional[str] = None
    slack_webhook: Optional[str] = None


class SecurityConfig(BaseModel):
    """Security Configuration"""
    cors_origins: List[str] = ["https://solar-calculator.example.com"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    csrf_enabled: bool = True
    csrf_secret: str = ""  # Set via environment variable
    session_secret: str = ""  # Set via environment variable
    session_lifetime: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900
    password_min_length: int = 12
    require_mfa: bool = True


class ServerConfig(BaseModel):
    """Main Server Configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    timeout: int = 120
    keepalive: int = 5
    max_requests: int = 1000
    max_requests_jitter: int = 50
    graceful_timeout: int = 30
    preload_app: bool = True


class ProductionConfig(BaseModel):
    """Complete Production Configuration"""
    environment: Environment = Environment.PRODUCTION
    app_name: str = "Solar Calculator Pro"
    app_version: str = "1.0.0"
    debug: bool = False
    
    server: ServerConfig = ServerConfig()
    ssl: SSLConfig = SSLConfig()
    reverse_proxy: ReverseProxyConfig = ReverseProxyConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    security: SecurityConfig = SecurityConfig()
    
    class Config:
        env_prefix = "SOLAR_"


def get_production_config() -> ProductionConfig:
    """Get production configuration with environment overrides"""
    config = ProductionConfig()
    
    # Override from environment variables
    config.database.password = os.getenv("SOLAR_DB_PASSWORD", "")
    config.redis.password = os.getenv("SOLAR_REDIS_PASSWORD")
    config.security.csrf_secret = os.getenv("SOLAR_CSRF_SECRET", "")
    config.security.session_secret = os.getenv("SOLAR_SESSION_SECRET", "")
    config.monitoring.alert_email = os.getenv("SOLAR_ALERT_EMAIL")
    config.monitoring.slack_webhook = os.getenv("SOLAR_SLACK_WEBHOOK")
    
    return config


# Nginx configuration template
NGINX_CONFIG_TEMPLATE = """
# Solar Calculator Pro - Nginx Configuration
# Generated for production deployment

user nginx;
worker_processes {worker_processes};
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections {worker_connections};
    use epoll;
    multi_accept on;
}}

http {{
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout {keepalive_timeout};
    types_hash_max_size 2048;
    
    # Gzip compression
    gzip {gzip_enabled};
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types {gzip_types};
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate={rate_limit}r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    
    # Upstream backend servers
    upstream backend {{
        least_conn;
        {upstream_servers}
        keepalive 32;
    }}
    
    # HTTP to HTTPS redirect
    server {{
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }}
    
    # Main HTTPS server
    server {{
        listen 443 ssl http2;
        server_name solar-calculator.example.com;
        
        # SSL configuration
        ssl_certificate {ssl_cert};
        ssl_certificate_key {ssl_key};
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers {ssl_ciphers};
        ssl_prefer_server_ciphers off;
        
        # HSTS
        add_header Strict-Transport-Security "max-age={hsts_max_age}; includeSubDomains" always;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        client_max_body_size {client_max_body_size};
        
        # Static files
        location /static/ {{
            alias /var/www/solar-calculator/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }}
        
        # API endpoints
        location /api/ {{
            limit_req zone=api_limit burst=20 nodelay;
            limit_conn conn_limit 10;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout {proxy_connect_timeout};
            proxy_send_timeout {proxy_send_timeout};
            proxy_read_timeout {proxy_read_timeout};
            
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }}
        
        # Health check endpoint
        location /health {{
            proxy_pass http://backend/health;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
        }}
        
        # Frontend application
        location / {{
            root /var/www/solar-calculator/frontend;
            try_files $uri $uri/ /index.html;
            expires 1h;
        }}
    }}
}}
"""


def generate_nginx_config(config: ProductionConfig) -> str:
    """Generate Nginx configuration from ProductionConfig"""
    proxy = config.reverse_proxy
    ssl = config.ssl
    
    upstream_servers = "\n        ".join(
        f"server {server};" for server in proxy.upstream_servers
    )
    
    return NGINX_CONFIG_TEMPLATE.format(
        worker_processes=proxy.worker_processes,
        worker_connections=proxy.worker_connections,
        keepalive_timeout=proxy.keepalive_timeout,
        gzip_enabled="on" if proxy.gzip_enabled else "off",
        gzip_types=" ".join(proxy.gzip_types),
        rate_limit=proxy.rate_limit_requests,
        upstream_servers=upstream_servers,
        ssl_cert=ssl.cert_path,
        ssl_key=ssl.key_path,
        ssl_ciphers=":".join(ssl.cipher_suites),
        hsts_max_age=ssl.hsts_max_age,
        client_max_body_size=proxy.client_max_body_size,
        proxy_connect_timeout=proxy.proxy_connect_timeout,
        proxy_send_timeout=proxy.proxy_send_timeout,
        proxy_read_timeout=proxy.proxy_read_timeout
    )


# Systemd service template
SYSTEMD_SERVICE_TEMPLATE = """
[Unit]
Description=Solar Calculator Pro Backend
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=solar
Group=solar
WorkingDirectory=/opt/solar-calculator
Environment="PATH=/opt/solar-calculator/venv/bin"
Environment="SOLAR_ENV=production"
ExecStart=/opt/solar-calculator/venv/bin/gunicorn main:app \\
    --bind {host}:{port} \\
    --workers {workers} \\
    --worker-class {worker_class} \\
    --timeout {timeout} \\
    --keepalive {keepalive} \\
    --max-requests {max_requests} \\
    --max-requests-jitter {max_requests_jitter} \\
    --graceful-timeout {graceful_timeout} \\
    --access-logfile /var/log/solar-calculator/access.log \\
    --error-logfile /var/log/solar-calculator/error.log \\
    --capture-output \\
    --enable-stdio-inheritance

ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=solar-calculator

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/solar-calculator /opt/solar-calculator/data

[Install]
WantedBy=multi-user.target
"""


def generate_systemd_service(config: ProductionConfig) -> str:
    """Generate systemd service file"""
    server = config.server
    return SYSTEMD_SERVICE_TEMPLATE.format(
        host=server.host,
        port=server.port,
        workers=server.workers,
        worker_class=server.worker_class,
        timeout=server.timeout,
        keepalive=server.keepalive,
        max_requests=server.max_requests,
        max_requests_jitter=server.max_requests_jitter,
        graceful_timeout=server.graceful_timeout
    )


# Docker Compose template for production
DOCKER_COMPOSE_TEMPLATE = """
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    image: solar-calculator-pro:latest
    container_name: solar-calculator-app
    restart: always
    environment:
      - SOLAR_ENV=production
      - SOLAR_DB_HOST=db
      - SOLAR_REDIS_HOST=redis
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - app_data:/opt/solar-calculator/data
      - app_logs:/var/log/solar-calculator
    networks:
      - solar-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    container_name: solar-calculator-db
    restart: always
    environment:
      - POSTGRES_DB=solar_calculator
      - POSTGRES_USER=solar_app
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - solar-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U solar_app -d solar_calculator"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: solar-calculator-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - solar-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: solar-calculator-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
      - static_files:/var/www/solar-calculator/static:ro
      - frontend_build:/var/www/solar-calculator/frontend:ro
    depends_on:
      - app
    networks:
      - solar-network

  prometheus:
    image: prom/prometheus:latest
    container_name: solar-calculator-prometheus
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - solar-network

  grafana:
    image: grafana/grafana:latest
    container_name: solar-calculator-grafana
    restart: always
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
    secrets:
      - grafana_password
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro
    depends_on:
      - prometheus
    networks:
      - solar-network

volumes:
  app_data:
  app_logs:
  postgres_data:
  redis_data:
  static_files:
  frontend_build:
  prometheus_data:
  grafana_data:

networks:
  solar-network:
    driver: bridge

secrets:
  db_password:
    file: ./secrets/db_password.txt
  grafana_password:
    file: ./secrets/grafana_password.txt
"""


def generate_docker_compose() -> str:
    """Generate Docker Compose configuration"""
    return DOCKER_COMPOSE_TEMPLATE


# Prometheus configuration
PROMETHEUS_CONFIG = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'solar-calculator'
    static_configs:
      - targets: ['app:8000']
    metrics_path: /metrics

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
"""


def generate_prometheus_config() -> str:
    """Generate Prometheus configuration"""
    return PROMETHEUS_CONFIG
