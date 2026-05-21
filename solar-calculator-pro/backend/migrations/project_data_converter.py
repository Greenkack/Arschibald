"""
Project Data Converter
Handles conversion of project data from Streamlit format to Electron format
Requirement: 5.3
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


class ProjectDataConverter:
    """Handles conversion of project-specific data"""
    
    def __init__(self, source_path: Path, target_path: Path):
        """
        Initialize project data converter
        
        Args:
            source_path: Path to source project data
            target_path: Path to target project data
        """
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.conversion_rules: Dict[str, callable] = {}
        
        # Ensure target directory exists
        self.target_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Project Data Converter initialized: {self.source_path} -> {self.target_path}")
    
    def convert(self) -> Dict[str, Any]:
        """
        Perform project data conversion
        
        Returns:
            Conversion result with statistics
        """
        logger.info("Starting project data conversion")
        
        result = {
            "success": False,
            "projects_converted": 0,
            "files_converted": 0,
            "errors": [],
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Find all project directories
            project_dirs = self._find_project_directories()
            logger.info(f"Found {len(project_dirs)} project directories")
            
            for project_dir in project_dirs:
                try:
                    project_result = self._convert_project(project_dir)
                    result["projects_converted"] += 1
                    result["files_converted"] += project_result["files"]
                    logger.info(f"Converted project: {project_dir.name}")
                except Exception as e:
                    error_msg = f"Failed to convert project {project_dir.name}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    result["errors"].append(error_msg)
            
            result["success"] = len(result["errors"]) == 0
            result["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Project data conversion completed: {result['projects_converted']} projects, {result['files_converted']} files")
            
        except Exception as e:
            error_msg = f"Project data conversion failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
        
        return result
    
    def _find_project_directories(self) -> List[Path]:
        """Find all project directories in source"""
        project_dirs = []
        
        # Look for common project directory structures
        search_paths = [
            self.source_path / "projects",
            self.source_path / "data" / "projects",
            self.source_path
        ]
        
        for search_path in search_paths:
            if search_path.exists() and search_path.is_dir():
                # Find directories that look like projects
                for item in search_path.iterdir():
                    if item.is_dir() and self._is_project_directory(item):
                        project_dirs.append(item)
        
        return project_dirs
    
    def _is_project_directory(self, path: Path) -> bool:
        """Check if directory contains project data"""
        # Look for project indicators
        indicators = [
            "project.json",
            "project_data.json",
            "metadata.json",
            "calculations.json"
        ]
        
        return any((path / indicator).exists() for indicator in indicators)
    
    def _convert_project(self, project_dir: Path) -> Dict[str, int]:
        """
        Convert a single project
        
        Args:
            project_dir: Project directory path
            
        Returns:
            Conversion statistics
        """
        files_converted = 0
        
        # Create target project directory
        relative_path = project_dir.relative_to(self.source_path)
        target_dir = self.target_path / relative_path
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert project metadata
        metadata = self._convert_project_metadata(project_dir)
        if metadata:
            metadata_file = target_dir / "project.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            files_converted += 1
        
        # Convert calculation data
        calculations = self._convert_calculation_data(project_dir)
        if calculations:
            calc_file = target_dir / "calculations.json"
            with open(calc_file, 'w', encoding='utf-8') as f:
                json.dump(calculations, f, indent=2, ensure_ascii=False)
            files_converted += 1
        
        # Convert 3D visualization data
        visualization = self._convert_visualization_data(project_dir)
        if visualization:
            viz_file = target_dir / "visualization.json"
            with open(viz_file, 'w', encoding='utf-8') as f:
                json.dump(visualization, f, indent=2, ensure_ascii=False)
            files_converted += 1
        
        # Convert PDF data
        pdf_data = self._convert_pdf_data(project_dir)
        if pdf_data:
            pdf_file = target_dir / "pdf_config.json"
            with open(pdf_file, 'w', encoding='utf-8') as f:
                json.dump(pdf_data, f, indent=2, ensure_ascii=False)
            files_converted += 1
        
        # Copy attachments and media files
        files_converted += self._copy_project_files(project_dir, target_dir)
        
        return {"files": files_converted}
    
    def _convert_project_metadata(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """Convert project metadata"""
        metadata_files = [
            "project.json",
            "project_data.json",
            "metadata.json"
        ]
        
        for filename in metadata_files:
            metadata_file = project_dir / filename
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Transform metadata
                    return self._transform_metadata(metadata)
                    
                except Exception as e:
                    logger.error(f"Failed to load metadata from {filename}: {str(e)}")
        
        return None
    
    def _transform_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Transform metadata to new format"""
        transformed = {
            "id": metadata.get("id") or metadata.get("project_id"),
            "name": metadata.get("name") or metadata.get("project_name"),
            "type": metadata.get("type") or "solar",
            "status": self._map_status(metadata.get("status", "draft")),
            "created_at": metadata.get("created_at") or datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "customer": {
                "name": metadata.get("customer_name"),
                "email": metadata.get("customer_email"),
                "phone": metadata.get("customer_phone"),
                "address": metadata.get("customer_address")
            },
            "location": {
                "address": metadata.get("location") or metadata.get("address"),
                "latitude": metadata.get("latitude"),
                "longitude": metadata.get("longitude")
            },
            "data": metadata.get("data", {}),
            "_migrated_at": datetime.now().isoformat()
        }
        
        return transformed
    
    def _map_status(self, old_status: str) -> str:
        """Map old status values to new ones"""
        status_map = {
            "active": "in_progress",
            "done": "completed",
            "pending": "draft",
            "archived": "archived"
        }
        
        return status_map.get(old_status.lower(), "draft")
    
    def _convert_calculation_data(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """Convert calculation data"""
        calc_files = [
            "calculations.json",
            "results.json",
            "analysis.json"
        ]
        
        for filename in calc_files:
            calc_file = project_dir / filename
            if calc_file.exists():
                try:
                    with open(calc_file, 'r', encoding='utf-8') as f:
                        calculations = json.load(f)
                    
                    # Transform calculations
                    return self._transform_calculations(calculations)
                    
                except Exception as e:
                    logger.error(f"Failed to load calculations from {filename}: {str(e)}")
        
        # Try to load from pickle files (Streamlit session state)
        pickle_files = list(project_dir.glob("*.pkl"))
        for pickle_file in pickle_files:
            try:
                with open(pickle_file, 'rb') as f:
                    data = pickle.load(f)
                
                if isinstance(data, dict) and any(key in data for key in ['calculations', 'results', 'analysis']):
                    return self._transform_calculations(data)
                    
            except Exception as e:
                logger.debug(f"Could not load pickle file {pickle_file.name}: {str(e)}")
        
        return None
    
    def _transform_calculations(self, calculations: Dict[str, Any]) -> Dict[str, Any]:
        """Transform calculation data to new format"""
        transformed = {
            "solar": {
                "system_size": calculations.get("system_size"),
                "module_count": calculations.get("module_count") or calculations.get("num_modules"),
                "annual_production": calculations.get("annual_production") or calculations.get("yearly_production"),
                "self_consumption_rate": calculations.get("self_consumption_rate"),
                "payback_period": calculations.get("payback_period"),
                "total_cost": calculations.get("total_cost"),
                "savings_25_years": calculations.get("savings_25_years"),
                "co2_savings": calculations.get("co2_savings")
            },
            "inputs": {
                "roof_area": calculations.get("roof_area"),
                "roof_type": calculations.get("roof_type"),
                "roof_angle": calculations.get("roof_angle") or calculations.get("tilt_angle"),
                "orientation": calculations.get("orientation") or calculations.get("azimuth"),
                "module_type": calculations.get("module_type"),
                "annual_consumption": calculations.get("annual_consumption"),
                "location": calculations.get("location")
            },
            "calculated_at": calculations.get("calculated_at") or datetime.now().isoformat(),
            "_migrated_at": datetime.now().isoformat()
        }
        
        return transformed
    
    def _convert_visualization_data(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """Convert 3D visualization data"""
        viz_files = [
            "visualization.json",
            "3d_data.json",
            "module_placement.json"
        ]
        
        for filename in viz_files:
            viz_file = project_dir / filename
            if viz_file.exists():
                try:
                    with open(viz_file, 'r', encoding='utf-8') as f:
                        visualization = json.load(f)
                    
                    # Transform visualization data
                    return self._transform_visualization(visualization)
                    
                except Exception as e:
                    logger.error(f"Failed to load visualization from {filename}: {str(e)}")
        
        return None
    
    def _transform_visualization(self, visualization: Dict[str, Any]) -> Dict[str, Any]:
        """Transform visualization data to new format"""
        transformed = {
            "roof_model": {
                "type": visualization.get("roof_type"),
                "dimensions": visualization.get("roof_dimensions"),
                "angle": visualization.get("roof_angle"),
                "orientation": visualization.get("orientation")
            },
            "modules": {
                "positions": visualization.get("module_positions", []),
                "count": visualization.get("module_count"),
                "type": visualization.get("module_type"),
                "dimensions": visualization.get("module_dimensions")
            },
            "camera": {
                "position": visualization.get("camera_position"),
                "target": visualization.get("camera_target"),
                "zoom": visualization.get("camera_zoom")
            },
            "_migrated_at": datetime.now().isoformat()
        }
        
        return transformed
    
    def _convert_pdf_data(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """Convert PDF configuration data"""
        pdf_files = [
            "pdf_config.json",
            "pdf_settings.json"
        ]
        
        for filename in pdf_files:
            pdf_file = project_dir / filename
            if pdf_file.exists():
                try:
                    with open(pdf_file, 'r', encoding='utf-8') as f:
                        pdf_data = json.load(f)
                    
                    # Transform PDF data
                    return self._transform_pdf_data(pdf_data)
                    
                except Exception as e:
                    logger.error(f"Failed to load PDF data from {filename}: {str(e)}")
        
        return None
    
    def _transform_pdf_data(self, pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PDF data to new format"""
        transformed = {
            "template": pdf_data.get("template") or "default",
            "options": {
                "include_3d": pdf_data.get("include_3d", True),
                "include_charts": pdf_data.get("include_charts", True),
                "include_calculations": pdf_data.get("include_calculations", True),
                "include_financial": pdf_data.get("include_financial", True)
            },
            "branding": {
                "logo": pdf_data.get("logo"),
                "company_name": pdf_data.get("company_name"),
                "colors": pdf_data.get("colors", {})
            },
            "_migrated_at": datetime.now().isoformat()
        }
        
        return transformed
    
    def _copy_project_files(self, source_dir: Path, target_dir: Path) -> int:
        """Copy project files (images, documents, etc.)"""
        files_copied = 0
        
        # File extensions to copy
        extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.stl', '.obj', '.gltf']
        
        for ext in extensions:
            for file in source_dir.glob(f"*{ext}"):
                try:
                    target_file = target_dir / file.name
                    import shutil
                    shutil.copy2(file, target_file)
                    files_copied += 1
                except Exception as e:
                    logger.error(f"Failed to copy file {file.name}: {str(e)}")
        
        return files_copied
    
    def add_conversion_rule(self, data_type: str, converter: callable):
        """
        Add custom conversion rule
        
        Args:
            data_type: Type of data (e.g., 'solar', 'heatpump')
            converter: Function that converts data
        """
        self.conversion_rules[data_type] = converter
        logger.info(f"Added conversion rule for data type: {data_type}")
    
    def validate_conversion(self) -> Dict[str, Any]:
        """
        Validate project data conversion
        
        Returns:
            Validation result
        """
        logger.info("Validating project data conversion")
        
        result = {
            "success": False,
            "projects_validated": 0,
            "issues": [],
            "errors": []
        }
        
        try:
            # Find all converted projects
            project_dirs = list(self.target_path.glob("*"))
            project_dirs = [d for d in project_dirs if d.is_dir()]
            
            for project_dir in project_dirs:
                try:
                    # Check for required files
                    required_files = ["project.json"]
                    missing_files = [f for f in required_files if not (project_dir / f).exists()]
                    
                    if missing_files:
                        result["issues"].append({
                            "project": project_dir.name,
                            "missing_files": missing_files
                        })
                    else:
                        # Validate project.json structure
                        with open(project_dir / "project.json", 'r', encoding='utf-8') as f:
                            project_data = json.load(f)
                        
                        required_fields = ["id", "name", "type", "status"]
                        missing_fields = [f for f in required_fields if f not in project_data]
                        
                        if missing_fields:
                            result["issues"].append({
                                "project": project_dir.name,
                                "missing_fields": missing_fields
                            })
                        else:
                            result["projects_validated"] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to validate project {project_dir.name}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
            
            result["success"] = len(result["issues"]) == 0 and len(result["errors"]) == 0
            logger.info(f"Validation completed: {result['projects_validated']} projects validated")
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
        
        return result
