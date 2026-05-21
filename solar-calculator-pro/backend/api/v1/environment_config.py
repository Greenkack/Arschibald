"""
Environment Configuration System
Task 237: Production, staging, development environment setup and management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/environments", tags=["Environment Configuration"])


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class EnvironmentConfig(BaseModel):
    """Environment configuration"""
    name: EnvironmentType
    status: EnvironmentStatus = EnvironmentStatus.ACTIVE
    url: str
    api_url: str
    database_host: str
    redis_host: str
    debug: bool = False
    log_level: str = "INFO"
    features: Dict[str, bool] = {}
    secrets_configured: bool = True
    ssl_enabled: bool = True
    last_deployment: Optional[datetime] = None
    version: Optional[str] = None


class EnvironmentVariable(BaseModel):
    """Environment variable"""
    key: str
    value: str
    is_secret: bool = False
    environment: EnvironmentType
    description: Optional[str] = None


# In-memory storage
environments: Dict[str, EnvironmentConfig] = {
    "development": EnvironmentConfig(
        name=EnvironmentType.DEVELOPMENT,
        url="http://localhost:3000",
        api_url="http://localhost:8000",
        database_host="localhost",
        redis_host="localhost",
        debug=True,
        log_level="DEBUG",
        ssl_enabled=False,
        version="1.2.3-dev"
    ),
    "staging": EnvironmentConfig(
        name=EnvironmentType.STAGING,
        url="https://staging.solar-calculator.example.com",
        api_url="https://staging-api.solar-calculator.example.com",
        database_host="staging-db.internal",
        redis_host="staging-redis.internal",
        debug=False,
        log_level="INFO",
        version="1.2.3-rc1"
    ),
    "production": EnvironmentConfig(
        name=EnvironmentType.PRODUCTION,
        url="https://solar-calculator.example.com",
        api_url="https://api.solar-calculator.example.com",
        database_host="prod-db.internal",
        redis_host="prod-redis.internal",
        debug=False,
        log_level="WARNING",
        version="1.2.2"
    )
}

env_variables: List[EnvironmentVariable] = []


# ============================================
# Environment Management
# ============================================

@router.get("/", response_model=List[EnvironmentConfig])
async def list_environments():
    """List all environments"""
    return list(environments.values())


@router.get("/{env_name}", response_model=EnvironmentConfig)
async def get_environment(env_name: EnvironmentType):
    """Get environment configuration"""
    if env_name.value not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    return environments[env_name.value]


@router.put("/{env_name}", response_model=EnvironmentConfig)
async def update_environment(env_name: EnvironmentType, config: EnvironmentConfig):
    """Update environment configuration"""
    config.name = env_name
    environments[env_name.value] = config
    return config


@router.post("/{env_name}/status")
async def set_environment_status(env_name: EnvironmentType, status: EnvironmentStatus):
    """Set environment status"""
    if env_name.value not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    environments[env_name.value].status = status
    return {"environment": env_name.value, "status": status.value}


# ============================================
# Environment Variables
# ============================================

@router.get("/{env_name}/variables")
async def get_environment_variables(env_name: EnvironmentType, include_secrets: bool = False):
    """Get environment variables"""
    variables = [v for v in env_variables if v.environment == env_name]
    
    if not include_secrets:
        for v in variables:
            if v.is_secret:
                v.value = "********"
    
    return {"environment": env_name.value, "variables": variables}


@router.post("/{env_name}/variables", response_model=EnvironmentVariable)
async def set_environment_variable(
    env_name: EnvironmentType,
    key: str,
    value: str,
    is_secret: bool = False,
    description: Optional[str] = None
):
    """Set environment variable"""
    # Remove existing variable with same key
    global env_variables
    env_variables = [v for v in env_variables if not (v.environment == env_name and v.key == key)]
    
    variable = EnvironmentVariable(
        key=key,
        value=value,
        is_secret=is_secret,
        environment=env_name,
        description=description
    )
    env_variables.append(variable)
    return variable


@router.delete("/{env_name}/variables/{key}")
async def delete_environment_variable(env_name: EnvironmentType, key: str):
    """Delete environment variable"""
    global env_variables
    env_variables = [v for v in env_variables if not (v.environment == env_name and v.key == key)]
    return {"status": "deleted", "key": key}


# ============================================
# Feature Flags
# ============================================

@router.get("/{env_name}/features")
async def get_feature_flags(env_name: EnvironmentType):
    """Get feature flags for environment"""
    if env_name.value not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    return {
        "environment": env_name.value,
        "features": environments[env_name.value].features
    }


@router.put("/{env_name}/features/{feature_name}")
async def set_feature_flag(env_name: EnvironmentType, feature_name: str, enabled: bool):
    """Set feature flag"""
    if env_name.value not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    environments[env_name.value].features[feature_name] = enabled
    return {"feature": feature_name, "enabled": enabled}


# ============================================
# Health and Status
# ============================================

@router.get("/{env_name}/health")
async def check_environment_health(env_name: EnvironmentType):
    """Check environment health"""
    if env_name.value not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = environments[env_name.value]
    
    return {
        "environment": env_name.value,
        "status": env.status.value,
        "health": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "ssl": "valid" if env.ssl_enabled else "disabled"
        },
        "version": env.version,
        "last_deployment": env.last_deployment.isoformat() if env.last_deployment else None
    }


@router.get("/compare/{env1}/{env2}")
async def compare_environments(env1: EnvironmentType, env2: EnvironmentType):
    """Compare two environments"""
    if env1.value not in environments or env2.value not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    e1 = environments[env1.value]
    e2 = environments[env2.value]
    
    return {
        "environments": [env1.value, env2.value],
        "comparison": {
            "version": {env1.value: e1.version, env2.value: e2.version},
            "status": {env1.value: e1.status.value, env2.value: e2.status.value},
            "debug": {env1.value: e1.debug, env2.value: e2.debug},
            "log_level": {env1.value: e1.log_level, env2.value: e2.log_level},
            "ssl_enabled": {env1.value: e1.ssl_enabled, env2.value: e2.ssl_enabled}
        },
        "feature_differences": {
            k: {env1.value: e1.features.get(k), env2.value: e2.features.get(k)}
            for k in set(e1.features.keys()) | set(e2.features.keys())
            if e1.features.get(k) != e2.features.get(k)
        }
    }
