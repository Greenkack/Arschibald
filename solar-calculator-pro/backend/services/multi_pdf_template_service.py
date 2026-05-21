"""
Multi-PDF Template & Koordinaten System Service

This service handles the Multi-PDF template and coordinate system for generating
multiple company-specific PDF offers with different templates and positioning.

**Template Structure:**
- Template Folder: `pdf_templates_static/multi/`
- Template Files: `multi_nt_01_f1.pdf`, `multi_nt_02_f1.pdf`, ..., `multi_nt_08_f1.pdf` (Company 1)
- Template Files: `multi_nt_01_f2.pdf`, `multi_nt_02_f2.pdf`, ..., `multi_nt_08_f2.pdf` (Company 2)
- Naming Convention: `multi_nt_{XX}_f{Y}.pdf` (XX = page 01-08, Y = company number)

**Coordinate Structure:**
- Coordinate Folder: `coords_multi/`
- Coordinate Files: `seite1_f1.yml`, `seite2_f1.yml`, ..., `seite8_f1.yml` (Company 1)
- Coordinate Files: `seite1_f2.yml`, `seite2_f2.yml`, ..., `seite8_f2.yml` (Company 2)
- Naming Convention: `seite{X}_f{Y}.yml` (X = page number, Y = company number)

Requirements: 1.3, 6.1, 7.3
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TemplateInfo:
    """Information about a PDF template"""
    company_id: int
    page_number: int
    file_path: Path
    exists: bool
    file_size: Optional[int] = None


@dataclass
class CoordinateInfo:
    """Information about a coordinate YML file"""
    company_id: int
    page_number: int
    file_path: Path
    exists: bool
    coordinates: Optional[Dict[str, Any]] = None


class MultiPDFTemplateService:
    """
    Service for managing Multi-PDF templates and coordinates.
    
    This service provides:
    - Multi-Template-Loader for all companies
    - Multi-Coordinate-Parser (seite{X}_f{Y}.yml)
    - Company-specific positioning
    - Template assignment based on company number
    - Batch processing for all selected companies
    """
    
    def __init__(
        self,
        template_base_dir: str = "pdf_templates_static/multi",
        coordinate_base_dir: str = "coords_multi"
    ):
        """
        Initialize the Multi-PDF Template Service.
        
        Args:
            template_base_dir: Base directory for multi-PDF templates
            coordinate_base_dir: Base directory for multi-PDF coordinates
        """
        self.template_base_dir = Path(template_base_dir)
        self.coordinate_base_dir = Path(coordinate_base_dir)
        
        # Template naming pattern: multi_nt_{page:02d}_f{company}.pdf
        self.template_pattern = "multi_nt_{page:02d}_f{company}.pdf"
        
        # Coordinate naming pattern: seite{page}_f{company}.yml
        self.coordinate_pattern = "seite{page}_f{company}.yml"
        
        logger.info(
            f"MultiPDFTemplateService initialized with "
            f"template_dir={self.template_base_dir}, "
            f"coordinate_dir={self.coordinate_base_dir}"
        )
    
    def get_template_path(self, company_id: int, page_number: int) -> Path:
        """
        Get the path to a specific template file.
        
        Args:
            company_id: Company number (e.g., 1, 2, 3, ...)
            page_number: Page number (1-8)
            
        Returns:
            Path to the template file
        """
        filename = self.template_pattern.format(
            page=page_number,
            company=company_id
        )
        return self.template_base_dir / filename
    
    def get_coordinate_path(self, company_id: int, page_number: int) -> Path:
        """
        Get the path to a specific coordinate file.
        
        Args:
            company_id: Company number (e.g., 1, 2, 3, ...)
            page_number: Page number (1-8)
            
        Returns:
            Path to the coordinate file
        """
        filename = self.coordinate_pattern.format(
            page=page_number,
            company=company_id
        )
        return self.coordinate_base_dir / filename
    
    def load_template(self, company_id: int, page_number: int) -> Optional[bytes]:
        """
        Load a template PDF file.
        
        Args:
            company_id: Company number
            page_number: Page number (1-8)
            
        Returns:
            PDF file content as bytes, or None if file doesn't exist
        """
        template_path = self.get_template_path(company_id, page_number)
        
        if not template_path.exists():
            logger.warning(
                f"Template not found: {template_path} "
                f"(company={company_id}, page={page_number})"
            )
            return None
        
        try:
            with open(template_path, 'rb') as f:
                content = f.read()
            logger.debug(
                f"Loaded template: {template_path} "
                f"({len(content)} bytes)"
            )
            return content
        except Exception as e:
            logger.error(
                f"Error loading template {template_path}: {e}"
            )
            return None
    
    def load_coordinates(
        self,
        company_id: int,
        page_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Load and parse a coordinate YML file.
        
        Args:
            company_id: Company number
            page_number: Page number (1-8)
            
        Returns:
            Parsed coordinate data as dictionary, or None if file doesn't exist
        """
        coord_path = self.get_coordinate_path(company_id, page_number)
        
        if not coord_path.exists():
            logger.warning(
                f"Coordinate file not found: {coord_path} "
                f"(company={company_id}, page={page_number})"
            )
            return None
        
        try:
            with open(coord_path, 'r', encoding='utf-8') as f:
                coordinates = yaml.safe_load(f)
            logger.debug(
                f"Loaded coordinates: {coord_path} "
                f"({len(coordinates) if coordinates else 0} entries)"
            )
            return coordinates
        except Exception as e:
            logger.error(
                f"Error loading coordinates {coord_path}: {e}"
            )
            return None
    
    def get_template_info(
        self,
        company_id: int,
        page_number: int
    ) -> TemplateInfo:
        """
        Get information about a template file.
        
        Args:
            company_id: Company number
            page_number: Page number (1-8)
            
        Returns:
            TemplateInfo object with file information
        """
        template_path = self.get_template_path(company_id, page_number)
        exists = template_path.exists()
        file_size = template_path.stat().st_size if exists else None
        
        return TemplateInfo(
            company_id=company_id,
            page_number=page_number,
            file_path=template_path,
            exists=exists,
            file_size=file_size
        )
    
    def get_coordinate_info(
        self,
        company_id: int,
        page_number: int
    ) -> CoordinateInfo:
        """
        Get information about a coordinate file.
        
        Args:
            company_id: Company number
            page_number: Page number (1-8)
            
        Returns:
            CoordinateInfo object with file information
        """
        coord_path = self.get_coordinate_path(company_id, page_number)
        exists = coord_path.exists()
        coordinates = self.load_coordinates(company_id, page_number) if exists else None
        
        return CoordinateInfo(
            company_id=company_id,
            page_number=page_number,
            file_path=coord_path,
            exists=exists,
            coordinates=coordinates
        )
    
    def get_all_templates_for_company(
        self,
        company_id: int,
        pages: int = 8
    ) -> List[TemplateInfo]:
        """
        Get information about all templates for a specific company.
        
        Args:
            company_id: Company number
            pages: Number of pages (default: 8)
            
        Returns:
            List of TemplateInfo objects
        """
        return [
            self.get_template_info(company_id, page_num)
            for page_num in range(1, pages + 1)
        ]
    
    def get_all_coordinates_for_company(
        self,
        company_id: int,
        pages: int = 8
    ) -> List[CoordinateInfo]:
        """
        Get information about all coordinate files for a specific company.
        
        Args:
            company_id: Company number
            pages: Number of pages (default: 8)
            
        Returns:
            List of CoordinateInfo objects
        """
        return [
            self.get_coordinate_info(company_id, page_num)
            for page_num in range(1, pages + 1)
        ]
    
    def discover_companies(self) -> List[int]:
        """
        Discover all available companies by scanning template files.
        
        Returns:
            List of company IDs found in the template directory
        """
        if not self.template_base_dir.exists():
            logger.warning(
                f"Template directory not found: {self.template_base_dir}"
            )
            return []
        
        companies = set()
        
        # Scan all template files
        for file_path in self.template_base_dir.glob("multi_nt_*_f*.pdf"):
            # Extract company ID from filename
            # Format: multi_nt_01_f1.pdf -> company_id = 1
            try:
                parts = file_path.stem.split('_')
                if len(parts) >= 4 and parts[3].startswith('f'):
                    company_id = int(parts[3][1:])
                    companies.add(company_id)
            except (ValueError, IndexError) as e:
                logger.warning(
                    f"Could not parse company ID from filename: {file_path.name}"
                )
        
        company_list = sorted(list(companies))
        logger.info(f"Discovered {len(company_list)} companies: {company_list}")
        return company_list
    
    def validate_company_templates(
        self,
        company_id: int,
        pages: int = 8
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all required templates exist for a company.
        
        Args:
            company_id: Company number
            pages: Number of pages to validate (default: 8)
            
        Returns:
            Tuple of (is_valid, list_of_missing_files)
        """
        missing_files = []
        
        for page_num in range(1, pages + 1):
            template_info = self.get_template_info(company_id, page_num)
            if not template_info.exists:
                missing_files.append(str(template_info.file_path))
        
        is_valid = len(missing_files) == 0
        
        if is_valid:
            logger.info(
                f"All templates valid for company {company_id} ({pages} pages)"
            )
        else:
            logger.warning(
                f"Missing {len(missing_files)} templates for company {company_id}: "
                f"{missing_files}"
            )
        
        return is_valid, missing_files
    
    def validate_company_coordinates(
        self,
        company_id: int,
        pages: int = 8
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all required coordinate files exist for a company.
        
        Args:
            company_id: Company number
            pages: Number of pages to validate (default: 8)
            
        Returns:
            Tuple of (is_valid, list_of_missing_files)
        """
        missing_files = []
        
        for page_num in range(1, pages + 1):
            coord_info = self.get_coordinate_info(company_id, page_num)
            if not coord_info.exists:
                missing_files.append(str(coord_info.file_path))
        
        is_valid = len(missing_files) == 0
        
        if is_valid:
            logger.info(
                f"All coordinates valid for company {company_id} ({pages} pages)"
            )
        else:
            logger.warning(
                f"Missing {len(missing_files)} coordinate files for company {company_id}: "
                f"{missing_files}"
            )
        
        return is_valid, missing_files
    
    def batch_load_templates(
        self,
        company_ids: List[int],
        pages: int = 8
    ) -> Dict[int, Dict[int, Optional[bytes]]]:
        """
        Batch load templates for multiple companies.
        
        Args:
            company_ids: List of company IDs to load
            pages: Number of pages per company (default: 8)
            
        Returns:
            Dictionary mapping company_id -> page_number -> template_bytes
        """
        result = {}
        
        for company_id in company_ids:
            result[company_id] = {}
            for page_num in range(1, pages + 1):
                template_bytes = self.load_template(company_id, page_num)
                result[company_id][page_num] = template_bytes
        
        logger.info(
            f"Batch loaded templates for {len(company_ids)} companies, "
            f"{pages} pages each"
        )
        
        return result
    
    def batch_load_coordinates(
        self,
        company_ids: List[int],
        pages: int = 8
    ) -> Dict[int, Dict[int, Optional[Dict[str, Any]]]]:
        """
        Batch load coordinates for multiple companies.
        
        Args:
            company_ids: List of company IDs to load
            pages: Number of pages per company (default: 8)
            
        Returns:
            Dictionary mapping company_id -> page_number -> coordinates
        """
        result = {}
        
        for company_id in company_ids:
            result[company_id] = {}
            for page_num in range(1, pages + 1):
                coordinates = self.load_coordinates(company_id, page_num)
                result[company_id][page_num] = coordinates
        
        logger.info(
            f"Batch loaded coordinates for {len(company_ids)} companies, "
            f"{pages} pages each"
        )
        
        return result
    
    def get_company_summary(self, company_id: int) -> Dict[str, Any]:
        """
        Get a summary of templates and coordinates for a company.
        
        Args:
            company_id: Company number
            
        Returns:
            Dictionary with summary information
        """
        templates = self.get_all_templates_for_company(company_id)
        coordinates = self.get_all_coordinates_for_company(company_id)
        
        templates_valid, templates_missing = self.validate_company_templates(company_id)
        coords_valid, coords_missing = self.validate_company_coordinates(company_id)
        
        return {
            "company_id": company_id,
            "templates": {
                "total": len(templates),
                "existing": sum(1 for t in templates if t.exists),
                "missing": len(templates_missing),
                "missing_files": templates_missing,
                "valid": templates_valid,
                "total_size_bytes": sum(
                    t.file_size for t in templates if t.file_size is not None
                )
            },
            "coordinates": {
                "total": len(coordinates),
                "existing": sum(1 for c in coordinates if c.exists),
                "missing": len(coords_missing),
                "missing_files": coords_missing,
                "valid": coords_valid
            },
            "ready_for_generation": templates_valid and coords_valid
        }
    
    def get_all_companies_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all discovered companies.
        
        Returns:
            Dictionary with summary information for all companies
        """
        companies = self.discover_companies()
        
        summaries = {
            company_id: self.get_company_summary(company_id)
            for company_id in companies
        }
        
        total_ready = sum(
            1 for s in summaries.values() if s["ready_for_generation"]
        )
        
        return {
            "total_companies": len(companies),
            "companies_ready": total_ready,
            "companies_with_issues": len(companies) - total_ready,
            "company_ids": companies,
            "details": summaries
        }
