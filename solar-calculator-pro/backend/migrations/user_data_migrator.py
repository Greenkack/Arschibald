"""
User Data Migrator
Handles migration of user accounts, preferences, and authentication data
Requirement: 5.4
"""

import json
import bcrypt
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import secrets

logger = logging.getLogger(__name__)


class UserDataMigrator:
    """Handles migration of user-specific data"""
    
    def __init__(self, source_path: Path, target_path: Path):
        """
        Initialize user data migrator
        
        Args:
            source_path: Path to source user data
            target_path: Path to target user data
        """
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        
        # Ensure target directory exists
        self.target_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"User Data Migrator initialized: {self.source_path} -> {self.target_path}")
    
    def migrate(self) -> Dict[str, Any]:
        """
        Perform user data migration
        
        Returns:
            Migration result with statistics
        """
        logger.info("Starting user data migration")
        
        result = {
            "success": False,
            "users_migrated": 0,
            "preferences_migrated": 0,
            "errors": [],
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Migrate user accounts
            users_result = self._migrate_user_accounts()
            result["users_migrated"] = users_result["users"]
            result["errors"].extend(users_result["errors"])
            
            # Migrate user preferences
            prefs_result = self._migrate_user_preferences()
            result["preferences_migrated"] = prefs_result["preferences"]
            result["errors"].extend(prefs_result["errors"])
            
            # Migrate user sessions
            sessions_result = self._migrate_user_sessions()
            result["errors"].extend(sessions_result["errors"])
            
            # Create default admin user if none exists
            if result["users_migrated"] == 0:
                self._create_default_admin()
                result["users_migrated"] = 1
            
            result["success"] = len(result["errors"]) == 0
            result["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"User data migration completed: {result['users_migrated']} users, {result['preferences_migrated']} preferences")
            
        except Exception as e:
            error_msg = f"User data migration failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
        
        return result
    
    def _migrate_user_accounts(self) -> Dict[str, Any]:
        """Migrate user accounts"""
        logger.info("Migrating user accounts")
        
        result = {
            "users": 0,
            "errors": []
        }
        
        try:
            # Look for user data files
            user_files = [
                self.source_path / "users.json",
                self.source_path / "accounts.json",
                self.source_path / "user_database.json"
            ]
            
            users_data = []
            
            for user_file in user_files:
                if user_file.exists():
                    try:
                        with open(user_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if isinstance(data, list):
                            users_data.extend(data)
                        elif isinstance(data, dict):
                            if "users" in data:
                                users_data.extend(data["users"])
                            else:
                                users_data.append(data)
                        
                        logger.debug(f"Loaded users from {user_file.name}")
                        
                    except Exception as e:
                        error_msg = f"Failed to load users from {user_file.name}: {str(e)}"
                        logger.error(error_msg)
                        result["errors"].append(error_msg)
            
            # Transform and save users
            if users_data:
                transformed_users = []
                
                for user in users_data:
                    try:
                        transformed_user = self._transform_user(user)
                        transformed_users.append(transformed_user)
                        result["users"] += 1
                    except Exception as e:
                        error_msg = f"Failed to transform user {user.get('username', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        result["errors"].append(error_msg)
                
                # Save transformed users
                target_file = self.target_path / "users.json"
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(transformed_users, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved {len(transformed_users)} users to {target_file}")
        
        except Exception as e:
            result["errors"].append(f"User account migration error: {str(e)}")
        
        return result
    
    def _transform_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Transform user data to new format"""
        # Generate new user ID if not present
        user_id = user.get("id") or user.get("user_id") or self._generate_user_id()
        
        # Hash password if not already hashed
        password = user.get("password", "")
        if password and not password.startswith("$2b$"):
            password = self._hash_password(password)
        elif not password:
            # Generate random password for users without one
            password = self._hash_password(secrets.token_urlsafe(16))
        
        transformed = {
            "id": user_id,
            "username": user.get("username") or user.get("email", "").split("@")[0],
            "email": user.get("email"),
            "password": password,
            "role": self._map_role(user.get("role", "user")),
            "first_name": user.get("first_name") or user.get("name", "").split()[0] if user.get("name") else None,
            "last_name": user.get("last_name") or " ".join(user.get("name", "").split()[1:]) if user.get("name") else None,
            "phone": user.get("phone"),
            "company": user.get("company"),
            "is_active": user.get("is_active", True),
            "is_verified": user.get("is_verified", False),
            "created_at": user.get("created_at") or datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": user.get("last_login"),
            "settings": user.get("settings", {}),
            "_migrated_at": datetime.now().isoformat()
        }
        
        return transformed
    
    def _generate_user_id(self) -> int:
        """Generate unique user ID"""
        import random
        return random.randint(1000, 9999)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _map_role(self, old_role: str) -> str:
        """Map old role values to new ones"""
        role_map = {
            "administrator": "admin",
            "superuser": "admin",
            "manager": "manager",
            "standard": "user",
            "basic": "user",
            "viewer": "viewer"
        }
        
        return role_map.get(old_role.lower(), "user")
    
    def _migrate_user_preferences(self) -> Dict[str, Any]:
        """Migrate user preferences"""
        logger.info("Migrating user preferences")
        
        result = {
            "preferences": 0,
            "errors": []
        }
        
        try:
            # Look for preference files
            pref_files = [
                self.source_path / "preferences.json",
                self.source_path / "user_preferences.json",
                self.source_path / "settings.json"
            ]
            
            preferences_data = {}
            
            for pref_file in pref_files:
                if pref_file.exists():
                    try:
                        with open(pref_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if isinstance(data, dict):
                            preferences_data.update(data)
                        
                        logger.debug(f"Loaded preferences from {pref_file.name}")
                        
                    except Exception as e:
                        error_msg = f"Failed to load preferences from {pref_file.name}: {str(e)}"
                        logger.error(error_msg)
                        result["errors"].append(error_msg)
            
            # Transform preferences
            if preferences_data:
                transformed_prefs = self._transform_preferences(preferences_data)
                
                # Save transformed preferences
                target_file = self.target_path / "preferences.json"
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(transformed_prefs, f, indent=2, ensure_ascii=False)
                
                result["preferences"] = len(transformed_prefs)
                logger.info(f"Saved {result['preferences']} preference sets to {target_file}")
        
        except Exception as e:
            result["errors"].append(f"User preferences migration error: {str(e)}")
        
        return result
    
    def _transform_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Transform preferences to new format"""
        transformed = {
            "theme": {
                "mode": preferences.get("theme", {}).get("mode", "light"),
                "primary_color": preferences.get("theme", {}).get("primaryColor", "#1976d2"),
                "font_size": preferences.get("theme", {}).get("fontSize", "medium")
            },
            "language": preferences.get("language", "de"),
            "number_format": {
                "locale": preferences.get("number_format", {}).get("locale", "de-DE"),
                "decimal_places": preferences.get("number_format", {}).get("decimal_places", 2)
            },
            "notifications": {
                "email": preferences.get("notifications", {}).get("email", True),
                "desktop": preferences.get("notifications", {}).get("desktop", True),
                "sound": preferences.get("notifications", {}).get("sound", False)
            },
            "dashboard": {
                "default_view": preferences.get("dashboard", {}).get("default_view", "overview"),
                "widgets": preferences.get("dashboard", {}).get("widgets", [])
            },
            "_migrated_at": datetime.now().isoformat()
        }
        
        return transformed
    
    def _migrate_user_sessions(self) -> Dict[str, Any]:
        """Migrate user sessions"""
        logger.info("Migrating user sessions")
        
        result = {
            "errors": []
        }
        
        try:
            # Note: Sessions are typically not migrated as they expire
            # We just clear old sessions and let users log in again
            logger.info("User sessions will be cleared - users need to log in again")
            
        except Exception as e:
            result["errors"].append(f"User sessions migration error: {str(e)}")
        
        return result
    
    def _create_default_admin(self):
        """Create default admin user if no users exist"""
        logger.info("Creating default admin user")
        
        default_admin = {
            "id": 1,
            "username": "admin",
            "email": "admin@solarcalculator.local",
            "password": self._hash_password("admin123"),  # Should be changed on first login
            "role": "admin",
            "first_name": "System",
            "last_name": "Administrator",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "settings": {},
            "_migrated_at": datetime.now().isoformat(),
            "_default_user": True
        }
        
        # Save default admin
        target_file = self.target_path / "users.json"
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump([default_admin], f, indent=2, ensure_ascii=False)
        
        logger.warning("Default admin user created - username: admin, password: admin123 (CHANGE THIS!)")
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate user data migration
        
        Returns:
            Validation result
        """
        logger.info("Validating user data migration")
        
        result = {
            "success": False,
            "users_validated": 0,
            "issues": [],
            "errors": []
        }
        
        try:
            # Check if users file exists
            users_file = self.target_path / "users.json"
            
            if not users_file.exists():
                result["issues"].append("Users file not found")
            else:
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
                
                if not isinstance(users, list):
                    result["issues"].append("Invalid users file format")
                else:
                    # Validate each user
                    for user in users:
                        validation = self._validate_user(user)
                        if validation["valid"]:
                            result["users_validated"] += 1
                        else:
                            result["issues"].append({
                                "user": user.get("username", "unknown"),
                                "issues": validation["issues"]
                            })
            
            # Check preferences file
            prefs_file = self.target_path / "preferences.json"
            if not prefs_file.exists():
                logger.warning("Preferences file not found (optional)")
            
            result["success"] = len(result["issues"]) == 0
            logger.info(f"Validation completed: {result['users_validated']} users validated")
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
        
        return result
    
    def _validate_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single user"""
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check required fields
        required_fields = ["id", "username", "email", "password", "role"]
        for field in required_fields:
            if field not in user or not user[field]:
                validation["valid"] = False
                validation["issues"].append(f"Missing required field: {field}")
        
        # Validate email format
        if "email" in user and user["email"]:
            if "@" not in user["email"]:
                validation["valid"] = False
                validation["issues"].append("Invalid email format")
        
        # Validate password hash
        if "password" in user and user["password"]:
            if not user["password"].startswith("$2b$"):
                validation["valid"] = False
                validation["issues"].append("Password not properly hashed")
        
        # Validate role
        valid_roles = ["admin", "manager", "user", "viewer"]
        if "role" in user and user["role"] not in valid_roles:
            validation["valid"] = False
            validation["issues"].append(f"Invalid role: {user['role']}")
        
        return validation
