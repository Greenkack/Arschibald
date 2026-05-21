"""
Settings Migration Tool
Handles migration of application settings from Streamlit to Electron format
Requirement: 5.2
"""

import json
import yaml
import configparser
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SettingsMigrator:
    """Handles migration of application settings"""
    
    def __init__(self, source_path: Path, target_path: Path):
        """
        Initialize settings migrator
        
        Args:
            source_path: Path to source settings directory
            target_path: Path to target settings directory
        """
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.settings_map: Dict[str, Any] = {}
        
        # Ensure target directory exists
        self.target_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Settings Migrator initialized: {self.source_path} -> {self.target_path}")
    
    def migrate(self) -> Dict[str, Any]:
        """
        Perform settings migration
        
        Returns:
            Migration result with statistics
        """
        logger.info("Starting settings migration")
        
        result = {
            "success": False,
            "files_migrated": 0,
            "settings_migrated": 0,
            "errors": [],
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Migrate JSON settings
            json_result = self._migrate_json_settings()
            result["files_migrated"] += json_result["files"]
            result["settings_migrated"] += json_result["settings"]
            result["errors"].extend(json_result["errors"])
            
            # Migrate YAML settings
            yaml_result = self._migrate_yaml_settings()
            result["files_migrated"] += yaml_result["files"]
            result["settings_migrated"] += yaml_result["settings"]
            result["errors"].extend(yaml_result["errors"])
            
            # Migrate INI/Config settings
            ini_result = self._migrate_ini_settings()
            result["files_migrated"] += ini_result["files"]
            result["settings_migrated"] += ini_result["settings"]
            result["errors"].extend(ini_result["errors"])
            
            # Migrate Streamlit config
            streamlit_result = self._migrate_streamlit_config()
            result["files_migrated"] += streamlit_result["files"]
            result["settings_migrated"] += streamlit_result["settings"]
            result["errors"].extend(streamlit_result["errors"])
            
            # Create consolidated settings file
            self._create_consolidated_settings()
            
            result["success"] = len(result["errors"]) == 0
            result["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Settings migration completed: {result['files_migrated']} files, {result['settings_migrated']} settings")
            
        except Exception as e:
            error_msg = f"Settings migration failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
        
        return result
    
    def _migrate_json_settings(self) -> Dict[str, Any]:
        """Migrate JSON settings files"""
        logger.info("Migrating JSON settings")
        
        result = {
            "files": 0,
            "settings": 0,
            "errors": []
        }
        
        try:
            json_files = list(self.source_path.glob("**/*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    # Transform settings if needed
                    transformed_settings = self._transform_settings(settings, json_file.stem)
                    
                    # Save to target
                    relative_path = json_file.relative_to(self.source_path)
                    target_file = self.target_path / relative_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        json.dump(transformed_settings, f, indent=2, ensure_ascii=False)
                    
                    result["files"] += 1
                    result["settings"] += len(transformed_settings)
                    
                    # Store in settings map
                    self.settings_map[json_file.stem] = transformed_settings
                    
                    logger.debug(f"Migrated JSON settings: {json_file.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to migrate {json_file.name}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
        
        except Exception as e:
            result["errors"].append(f"JSON migration error: {str(e)}")
        
        return result
    
    def _migrate_yaml_settings(self) -> Dict[str, Any]:
        """Migrate YAML settings files"""
        logger.info("Migrating YAML settings")
        
        result = {
            "files": 0,
            "settings": 0,
            "errors": []
        }
        
        try:
            yaml_files = []
            yaml_files.extend(self.source_path.glob("**/*.yaml"))
            yaml_files.extend(self.source_path.glob("**/*.yml"))
            
            for yaml_file in yaml_files:
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        settings = yaml.safe_load(f)
                    
                    if settings is None:
                        settings = {}
                    
                    # Transform settings
                    transformed_settings = self._transform_settings(settings, yaml_file.stem)
                    
                    # Save as JSON in target (standardize format)
                    relative_path = yaml_file.relative_to(self.source_path)
                    target_file = self.target_path / relative_path.with_suffix('.json')
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        json.dump(transformed_settings, f, indent=2, ensure_ascii=False)
                    
                    result["files"] += 1
                    result["settings"] += len(transformed_settings) if isinstance(transformed_settings, dict) else 1
                    
                    # Store in settings map
                    self.settings_map[yaml_file.stem] = transformed_settings
                    
                    logger.debug(f"Migrated YAML settings: {yaml_file.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to migrate {yaml_file.name}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
        
        except Exception as e:
            result["errors"].append(f"YAML migration error: {str(e)}")
        
        return result
    
    def _migrate_ini_settings(self) -> Dict[str, Any]:
        """Migrate INI/Config settings files"""
        logger.info("Migrating INI settings")
        
        result = {
            "files": 0,
            "settings": 0,
            "errors": []
        }
        
        try:
            ini_files = []
            ini_files.extend(self.source_path.glob("**/*.ini"))
            ini_files.extend(self.source_path.glob("**/*.conf"))
            ini_files.extend(self.source_path.glob("**/*.cfg"))
            
            for ini_file in ini_files:
                try:
                    config = configparser.ConfigParser()
                    config.read(ini_file, encoding='utf-8')
                    
                    # Convert to dict
                    settings = {section: dict(config[section]) for section in config.sections()}
                    
                    # Transform settings
                    transformed_settings = self._transform_settings(settings, ini_file.stem)
                    
                    # Save as JSON in target
                    relative_path = ini_file.relative_to(self.source_path)
                    target_file = self.target_path / relative_path.with_suffix('.json')
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        json.dump(transformed_settings, f, indent=2, ensure_ascii=False)
                    
                    result["files"] += 1
                    result["settings"] += sum(len(section) for section in settings.values())
                    
                    # Store in settings map
                    self.settings_map[ini_file.stem] = transformed_settings
                    
                    logger.debug(f"Migrated INI settings: {ini_file.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to migrate {ini_file.name}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
        
        except Exception as e:
            result["errors"].append(f"INI migration error: {str(e)}")
        
        return result
    
    def _migrate_streamlit_config(self) -> Dict[str, Any]:
        """Migrate Streamlit-specific configuration"""
        logger.info("Migrating Streamlit config")
        
        result = {
            "files": 0,
            "settings": 0,
            "errors": []
        }
        
        try:
            # Look for .streamlit directory
            streamlit_dir = self.source_path / ".streamlit"
            
            if streamlit_dir.exists():
                config_file = streamlit_dir / "config.toml"
                
                if config_file.exists():
                    try:
                        # Parse TOML config
                        import toml
                        config = toml.load(config_file)
                        
                        # Transform Streamlit config to Electron config
                        electron_config = self._transform_streamlit_to_electron(config)
                        
                        # Save to target
                        target_file = self.target_path / "app_config.json"
                        with open(target_file, 'w', encoding='utf-8') as f:
                            json.dump(electron_config, f, indent=2, ensure_ascii=False)
                        
                        result["files"] += 1
                        result["settings"] += len(electron_config)
                        
                        # Store in settings map
                        self.settings_map["app_config"] = electron_config
                        
                        logger.debug("Migrated Streamlit config to Electron config")
                        
                    except Exception as e:
                        error_msg = f"Failed to migrate Streamlit config: {str(e)}"
                        logger.error(error_msg)
                        result["errors"].append(error_msg)
        
        except Exception as e:
            result["errors"].append(f"Streamlit config migration error: {str(e)}")
        
        return result
    
    def _transform_settings(self, settings: Dict[str, Any], context: str) -> Dict[str, Any]:
        """
        Transform settings from old format to new format
        
        Args:
            settings: Original settings
            context: Context/filename for transformation rules
            
        Returns:
            Transformed settings
        """
        transformed = settings.copy()
        
        # Apply context-specific transformations
        if context == "database":
            transformed = self._transform_database_settings(transformed)
        elif context == "ui":
            transformed = self._transform_ui_settings(transformed)
        elif context == "api":
            transformed = self._transform_api_settings(transformed)
        
        # Add metadata
        transformed["_migrated_at"] = datetime.now().isoformat()
        transformed["_source_context"] = context
        
        return transformed
    
    def _transform_database_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform database settings"""
        # Convert SQLite paths to new structure
        if "database_path" in settings:
            settings["database"] = {
                "type": "sqlite",
                "path": settings.pop("database_path"),
                "pool_size": 5,
                "echo": False
            }
        
        return settings
    
    def _transform_ui_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform UI settings"""
        # Convert Streamlit theme to PrimeReact theme
        if "theme" in settings:
            old_theme = settings["theme"]
            settings["theme"] = {
                "mode": old_theme.get("base", "light"),
                "primaryColor": old_theme.get("primaryColor", "#1976d2"),
                "backgroundColor": old_theme.get("backgroundColor", "#ffffff"),
                "secondaryBackgroundColor": old_theme.get("secondaryBackgroundColor", "#f0f2f6"),
                "textColor": old_theme.get("textColor", "#262730"),
                "font": old_theme.get("font", "sans serif")
            }
        
        return settings
    
    def _transform_api_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform API settings"""
        # Update API endpoints
        if "base_url" in settings:
            settings["api"] = {
                "base_url": settings.pop("base_url"),
                "timeout": settings.get("timeout", 30),
                "retry_attempts": 3
            }
        
        return settings
    
    def _transform_streamlit_to_electron(self, streamlit_config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Streamlit config to Electron config"""
        electron_config = {
            "app": {
                "name": "Solar Calculator Pro",
                "version": "1.0.0"
            },
            "window": {
                "width": 1280,
                "height": 800,
                "minWidth": 800,
                "minHeight": 600
            },
            "backend": {
                "port": 8000,
                "host": "localhost"
            }
        }
        
        # Map Streamlit server settings
        if "server" in streamlit_config:
            server = streamlit_config["server"]
            electron_config["backend"]["port"] = server.get("port", 8000)
            electron_config["backend"]["host"] = server.get("address", "localhost")
        
        # Map Streamlit theme settings
        if "theme" in streamlit_config:
            theme = streamlit_config["theme"]
            electron_config["theme"] = {
                "mode": "light" if theme.get("base") == "light" else "dark",
                "colors": {
                    "primary": theme.get("primaryColor", "#1976d2"),
                    "background": theme.get("backgroundColor", "#ffffff"),
                    "text": theme.get("textColor", "#262730")
                }
            }
        
        return electron_config
    
    def _create_consolidated_settings(self):
        """Create a consolidated settings file with all migrated settings"""
        logger.info("Creating consolidated settings file")
        
        consolidated = {
            "version": "1.0.0",
            "migrated_at": datetime.now().isoformat(),
            "settings": self.settings_map
        }
        
        consolidated_file = self.target_path / "settings.json"
        
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Consolidated settings saved: {consolidated_file}")
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate settings migration
        
        Returns:
            Validation result
        """
        logger.info("Validating settings migration")
        
        result = {
            "success": False,
            "files_validated": 0,
            "issues": [],
            "errors": []
        }
        
        try:
            # Check if consolidated settings exists
            consolidated_file = self.target_path / "settings.json"
            
            if not consolidated_file.exists():
                result["issues"].append("Consolidated settings file not found")
            else:
                with open(consolidated_file, 'r', encoding='utf-8') as f:
                    consolidated = json.load(f)
                
                # Validate structure
                if "settings" not in consolidated:
                    result["issues"].append("Invalid consolidated settings structure")
                else:
                    result["files_validated"] = len(consolidated["settings"])
                    
                    # Check for required settings
                    required_settings = ["app_config"]
                    for req in required_settings:
                        if req not in consolidated["settings"]:
                            result["issues"].append(f"Missing required settings: {req}")
            
            result["success"] = len(result["issues"]) == 0
            logger.info(f"Validation completed: {result['files_validated']} files validated")
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
        
        return result
