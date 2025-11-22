"""
Feature Flag Service

This module provides the business logic for managing feature flags.
"""

import hashlib
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.models.feature_flag_models import FeatureFlag, Role, feature_flag_users, feature_flag_roles
from backend.models.feature_flag_schemas import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagCheck,
    FeatureFlagCheckResponse,
    RoleCreate,
    RoleUpdate
)
from backend.core.errors import APIError
from backend.core.base_service import BaseService
import logging

logger = logging.getLogger(__name__)


class FeatureFlagService(BaseService):
    """Service for managing feature flags"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
    
    def create_feature_flag(self, flag_data: FeatureFlagCreate, created_by: Optional[int] = None) -> FeatureFlag:
        """
        Create a new feature flag
        
        Args:
            flag_data: Feature flag creation data
            created_by: ID of user creating the flag
            
        Returns:
            Created feature flag
            
        Raises:
            APIError: If flag with key already exists
        """
        # Check if flag already exists
        existing = self.db.query(FeatureFlag).filter(FeatureFlag.key == flag_data.key).first()
        if existing:
            raise APIError(409, f"Feature flag with key '{flag_data.key}' already exists")
        
        # Create feature flag
        flag = FeatureFlag(
            key=flag_data.key,
            name=flag_data.name,
            description=flag_data.description,
            enabled=flag_data.enabled,
            flag_type=flag_data.flag_type.value,
            rollout_percentage=flag_data.rollout_percentage,
            created_by=created_by
        )
        
        self.db.add(flag)
        self.db.flush()
        
        # Add user associations
        if flag_data.user_ids:
            for user_id in flag_data.user_ids:
                self.db.execute(
                    feature_flag_users.insert().values(
                        feature_flag_id=flag.id,
                        user_id=user_id
                    )
                )
        
        # Add role associations
        if flag_data.role_ids:
            for role_id in flag_data.role_ids:
                self.db.execute(
                    feature_flag_roles.insert().values(
                        feature_flag_id=flag.id,
                        role_id=role_id
                    )
                )
        
        self.db.commit()
        self.db.refresh(flag)
        
        # Clear cache
        self._clear_cache()
        
        logger.info(f"Created feature flag: {flag.key}")
        return flag
    
    def get_feature_flag(self, flag_id: int) -> Optional[FeatureFlag]:
        """Get feature flag by ID"""
        return self.db.query(FeatureFlag).filter(FeatureFlag.id == flag_id).first()
    
    def get_feature_flag_by_key(self, key: str) -> Optional[FeatureFlag]:
        """Get feature flag by key"""
        return self.db.query(FeatureFlag).filter(FeatureFlag.key == key.lower()).first()
    
    def list_feature_flags(self, skip: int = 0, limit: int = 100) -> List[FeatureFlag]:
        """List all feature flags"""
        return self.db.query(FeatureFlag).offset(skip).limit(limit).all()
    
    def update_feature_flag(self, flag_id: int, flag_data: FeatureFlagUpdate) -> FeatureFlag:
        """
        Update a feature flag
        
        Args:
            flag_id: ID of flag to update
            flag_data: Update data
            
        Returns:
            Updated feature flag
            
        Raises:
            APIError: If flag not found
        """
        flag = self.get_feature_flag(flag_id)
        if not flag:
            raise APIError(404, f"Feature flag with ID {flag_id} not found")
        
        # Update fields
        update_data = flag_data.dict(exclude_unset=True)
        
        # Handle user_ids separately
        user_ids = update_data.pop('user_ids', None)
        role_ids = update_data.pop('role_ids', None)
        
        for key, value in update_data.items():
            if hasattr(flag, key):
                if key == 'flag_type' and value:
                    setattr(flag, key, value.value)
                else:
                    setattr(flag, key, value)
        
        # Update user associations
        if user_ids is not None:
            # Clear existing associations
            self.db.execute(
                feature_flag_users.delete().where(
                    feature_flag_users.c.feature_flag_id == flag_id
                )
            )
            # Add new associations
            for user_id in user_ids:
                self.db.execute(
                    feature_flag_users.insert().values(
                        feature_flag_id=flag_id,
                        user_id=user_id
                    )
                )
        
        # Update role associations
        if role_ids is not None:
            # Clear existing associations
            self.db.execute(
                feature_flag_roles.delete().where(
                    feature_flag_roles.c.feature_flag_id == flag_id
                )
            )
            # Add new associations
            for role_id in role_ids:
                self.db.execute(
                    feature_flag_roles.insert().values(
                        feature_flag_id=flag_id,
                        role_id=role_id
                    )
                )
        
        self.db.commit()
        self.db.refresh(flag)
        
        # Clear cache
        self._clear_cache()
        
        logger.info(f"Updated feature flag: {flag.key}")
        return flag
    
    def delete_feature_flag(self, flag_id: int) -> bool:
        """
        Delete a feature flag
        
        Args:
            flag_id: ID of flag to delete
            
        Returns:
            True if deleted
            
        Raises:
            APIError: If flag not found
        """
        flag = self.get_feature_flag(flag_id)
        if not flag:
            raise APIError(404, f"Feature flag with ID {flag_id} not found")
        
        self.db.delete(flag)
        self.db.commit()
        
        # Clear cache
        self._clear_cache()
        
        logger.info(f"Deleted feature flag: {flag.key}")
        return True
    
    def is_feature_enabled(self, key: str, user_id: Optional[int] = None) -> FeatureFlagCheckResponse:
        """
        Check if a feature is enabled for a user
        
        Args:
            key: Feature flag key
            user_id: Optional user ID to check
            
        Returns:
            FeatureFlagCheckResponse with enabled status and reason
        """
        # Check cache first
        cache_key = f"{key}:{user_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        flag = self.get_feature_flag_by_key(key)
        
        if not flag:
            result = FeatureFlagCheckResponse(
                key=key,
                enabled=False,
                reason="Feature flag not found"
            )
            self.cache[cache_key] = result
            return result
        
        # Global flag - simple enabled/disabled
        if flag.flag_type == 'global':
            result = FeatureFlagCheckResponse(
                key=key,
                enabled=flag.enabled,
                reason="Global flag" if flag.enabled else "Global flag disabled"
            )
            self.cache[cache_key] = result
            return result
        
        # If flag is disabled globally, return false
        if not flag.enabled:
            result = FeatureFlagCheckResponse(
                key=key,
                enabled=False,
                reason="Flag is globally disabled"
            )
            self.cache[cache_key] = result
            return result
        
        # User-based flag
        if flag.flag_type == 'user':
            if not user_id:
                result = FeatureFlagCheckResponse(
                    key=key,
                    enabled=False,
                    reason="User-based flag requires user_id"
                )
                self.cache[cache_key] = result
                return result
            
            # Check if user is in the allowed list
            user_in_list = self.db.query(feature_flag_users).filter(
                and_(
                    feature_flag_users.c.feature_flag_id == flag.id,
                    feature_flag_users.c.user_id == user_id
                )
            ).first()
            
            result = FeatureFlagCheckResponse(
                key=key,
                enabled=bool(user_in_list),
                reason="User in allowed list" if user_in_list else "User not in allowed list"
            )
            self.cache[cache_key] = result
            return result
        
        # Role-based flag
        if flag.flag_type == 'role':
            if not user_id:
                result = FeatureFlagCheckResponse(
                    key=key,
                    enabled=False,
                    reason="Role-based flag requires user_id"
                )
                self.cache[cache_key] = result
                return result
            
            # Get user's roles and check if any match
            from backend.models.user_models import User
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                result = FeatureFlagCheckResponse(
                    key=key,
                    enabled=False,
                    reason="User not found"
                )
                self.cache[cache_key] = result
                return result
            
            # Check if user has any of the required roles
            user_role_ids = [role.id for role in user.roles] if hasattr(user, 'roles') else []
            flag_role_ids = [role.id for role in flag.roles]
            
            has_role = bool(set(user_role_ids) & set(flag_role_ids))
            
            result = FeatureFlagCheckResponse(
                key=key,
                enabled=has_role,
                reason="User has required role" if has_role else "User does not have required role"
            )
            self.cache[cache_key] = result
            return result
        
        # Percentage rollout
        if flag.flag_type == 'percentage':
            if not user_id:
                result = FeatureFlagCheckResponse(
                    key=key,
                    enabled=False,
                    reason="Percentage rollout requires user_id"
                )
                self.cache[cache_key] = result
                return result
            
            # Use consistent hashing to determine if user is in rollout
            hash_input = f"{key}:{user_id}".encode('utf-8')
            hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
            user_percentage = hash_value % 100
            
            enabled = user_percentage < flag.rollout_percentage
            
            result = FeatureFlagCheckResponse(
                key=key,
                enabled=enabled,
                reason=f"User in {flag.rollout_percentage}% rollout" if enabled else f"User not in {flag.rollout_percentage}% rollout"
            )
            self.cache[cache_key] = result
            return result
        
        # Default to disabled
        result = FeatureFlagCheckResponse(
            key=key,
            enabled=False,
            reason="Unknown flag type"
        )
        self.cache[cache_key] = result
        return result
    
    def check_multiple_features(self, keys: List[str], user_id: Optional[int] = None) -> Dict[str, bool]:
        """
        Check multiple feature flags at once
        
        Args:
            keys: List of feature flag keys
            user_id: Optional user ID
            
        Returns:
            Dictionary mapping keys to enabled status
        """
        results = {}
        for key in keys:
            response = self.is_feature_enabled(key, user_id)
            results[key] = response.enabled
        return results
    
    def _clear_cache(self):
        """Clear the feature flag cache"""
        self.cache.clear()
        logger.debug("Feature flag cache cleared")
    
    # Role management methods
    
    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role"""
        existing = self.db.query(Role).filter(Role.name == role_data.name).first()
        if existing:
            raise APIError(409, f"Role with name '{role_data.name}' already exists")
        
        role = Role(
            name=role_data.name,
            description=role_data.description
        )
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        logger.info(f"Created role: {role.name}")
        return role
    
    def get_role(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def list_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """List all roles"""
        return self.db.query(Role).offset(skip).limit(limit).all()
    
    def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """Update a role"""
        role = self.get_role(role_id)
        if not role:
            raise APIError(404, f"Role with ID {role_id} not found")
        
        update_data = role_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role, key, value)
        
        self.db.commit()
        self.db.refresh(role)
        
        logger.info(f"Updated role: {role.name}")
        return role
    
    def delete_role(self, role_id: int) -> bool:
        """Delete a role"""
        role = self.get_role(role_id)
        if not role:
            raise APIError(404, f"Role with ID {role_id} not found")
        
        self.db.delete(role)
        self.db.commit()
        
        logger.info(f"Deleted role: {role.name}")
        return True
