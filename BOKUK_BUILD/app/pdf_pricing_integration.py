"""PDF Pricing Integration

Enhanced PDF generation system that integrates with the dynamic pricing system.
Provides automatic key population and pricing breakdown sections in PDF output.
"""

from __future__ import annotations

import logging
from typing import Any

# Import existing PDF generator
try:
    from pdf_generator import PDFGenerator, generate_offer_pdf
    from pdf_template_engine import build_dynamic_data
except ImportError:
    # Fallback for testing
    class PDFGenerator:
        def __init__(self, *args, **kwargs):
            pass
    def generate_offer_pdf(*args, **kwargs):
        return b""
    def build_dynamic_data(*args, **kwargs):
        return {}

# Import pricing system components
try:
    from pricing.combined_pricing_engine import CombinedPricingEngine
    from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
    from pricing.enhanced_heatpump_pricing import EnhancedHeatpumpPricingEngine
    from pricing.enhanced_pricing_engine import PricingEngine, PricingResult
    from pricing.pv_pricing_engine import PVPricingEngine
except ImportError:
    # Fallback for testing
    class KeyCategory:
        PRICING = "pricing"
        COMPONENTS = "components"
        DISCOUNTS = "discounts"
        SURCHARGES = "surcharges"
        VAT = "vat"
        TOTALS = "totals"

    class DynamicKeyManager:
        def __init__(self):
            self.key_registry = {}
        def generate_keys(self, *args, **kwargs):
            return {}
        def format_for_pdf(self, *args, **kwargs):
            return {}
        def get_all_keys(self, filter_category=None):
            return {}
        def get_keys_by_category(self, category):
            return {}
        def register_key(self, key, value, category=None):
            pass
        def clear_registry(self):
            pass

    class PricingEngine:
        def __init__(self, *args, **kwargs):
            pass

    PricingResult = dict
    CombinedPricingEngine = PricingEngine
    PVPricingEngine = PricingEngine
    EnhancedHeatpumpPricingEngine = PricingEngine

logger = logging.getLogger(__name__)


class EnhancedPDFGenerator:
    """Enhanced PDF generator with integrated pricing system"""

    def __init__(self,
                 project_data: dict[str, Any],
                 analysis_results: dict[str, Any],
                 company_info: dict[str, Any],
                 pricing_data: dict[str, Any] | None = None):
        """Initialize enhanced PDF generator
        
        Args:
            project_data: Project configuration data
            analysis_results: Analysis and calculation results
            company_info: Company information
            pricing_data: Optional pricing calculation results
        """
        self.project_data = project_data or {}
        self.analysis_results = analysis_results or {}
        self.company_info = company_info or {}
        self.pricing_data = pricing_data or {}

        # Initialize pricing components
        self.key_manager = DynamicKeyManager()
        self.pricing_keys: dict[str, Any] = {}

        # Initialize pricing engines
        self.pv_engine = PVPricingEngine()
        self.hp_engine = EnhancedHeatpumpPricingEngine()
        self.combined_engine = CombinedPricingEngine()

        # Generate pricing keys
        self._generate_pricing_keys()

    def _generate_pricing_keys(self) -> None:
        """Generate dynamic pricing keys from pricing data"""
        try:
            # Clear existing keys if method exists
            if hasattr(self.key_manager, 'clear_registry'):
                self.key_manager.clear_registry()

            # Generate keys from different pricing sources
            if self.pricing_data:
                self._process_pricing_data()

            # Generate keys from analysis results
            if self.analysis_results:
                self._process_analysis_results()

            # Generate keys from project data
            if self.project_data:
                self._process_project_data()

            # Get all formatted keys for PDF
            self.pricing_keys = self.key_manager.format_for_pdf(
                self.key_manager.get_all_keys()
            )

            logger.info(f"Generated {len(self.pricing_keys)} pricing keys for PDF")

        except Exception as e:
            logger.error(f"Error generating pricing keys: {e}")
            self.pricing_keys = {}

    def _process_pricing_data(self) -> None:
        """Process pricing data and generate keys"""
        try:
            # Process PV pricing if available
            pv_pricing = self.pricing_data.get('pv_pricing', {})
            if pv_pricing:
                pv_keys = self.key_manager.generate_keys(
                    pv_pricing,
                    prefix="PV",
                    category=KeyCategory.PRICING
                )
                logger.debug(f"Generated {len(pv_keys)} PV pricing keys")

            # Process heat pump pricing if available
            hp_pricing = self.pricing_data.get('heatpump_pricing', {})
            if hp_pricing:
                hp_keys = self.key_manager.generate_keys(
                    hp_pricing,
                    prefix="HP",
                    category=KeyCategory.PRICING
                )
                logger.debug(f"Generated {len(hp_keys)} heat pump pricing keys")

            # Process combined pricing if available
            combined_pricing = self.pricing_data.get('combined_pricing', {})
            if combined_pricing:
                combined_keys = self.key_manager.generate_keys(
                    combined_pricing,
                    prefix="COMBINED",
                    category=KeyCategory.PRICING
                )
                logger.debug(f"Generated {len(combined_keys)} combined pricing keys")

            # Process component pricing
            components = self.pricing_data.get('components', {})
            if components:
                component_keys = self.key_manager.generate_keys(
                    components,
                    prefix="COMPONENT",
                    category=KeyCategory.COMPONENTS
                )
                logger.debug(f"Generated {len(component_keys)} component keys")

            # Process discounts and surcharges
            discounts = self.pricing_data.get('discounts', {})
            if discounts:
                discount_keys = self.key_manager.generate_keys(
                    discounts,
                    prefix="DISCOUNT",
                    category=KeyCategory.DISCOUNTS
                )
                logger.debug(f"Generated {len(discount_keys)} discount keys")

            surcharges = self.pricing_data.get('surcharges', {})
            if surcharges:
                surcharge_keys = self.key_manager.generate_keys(
                    surcharges,
                    prefix="SURCHARGE",
                    category=KeyCategory.SURCHARGES
                )
                logger.debug(f"Generated {len(surcharge_keys)} surcharge keys")

            # Process VAT and tax information
            vat_data = self.pricing_data.get('vat', {})
            if vat_data:
                vat_keys = self.key_manager.generate_keys(
                    vat_data,
                    prefix="VAT",
                    category=KeyCategory.VAT
                )
                logger.debug(f"Generated {len(vat_keys)} VAT keys")

            # Process totals
            totals = self.pricing_data.get('totals', {})
            if totals:
                total_keys = self.key_manager.generate_keys(
                    totals,
                    prefix="TOTAL",
                    category=KeyCategory.TOTALS
                )
                logger.debug(f"Generated {len(total_keys)} total keys")

        except Exception as e:
            logger.error(f"Error processing pricing data: {e}")

    def _process_analysis_results(self) -> None:
        """Process analysis results and generate pricing-related keys"""
        try:
            # Extract pricing-relevant data from analysis results
            pricing_relevant = {}

            # Financial data
            financial_keys = [
                'final_price', 'total_investment_netto', 'total_investment_brutto',
                'subtotal_netto', 'subtotal_brutto', 'vat_amount',
                'annual_savings', 'payback_period', 'roi_percent'
            ]

            for key in financial_keys:
                if key in self.analysis_results:
                    pricing_relevant[key] = self.analysis_results[key]

            if pricing_relevant:
                analysis_keys = self.key_manager.generate_keys(
                    pricing_relevant,
                    prefix="ANALYSIS",
                    category=KeyCategory.PRICING
                )
                logger.debug(f"Generated {len(analysis_keys)} analysis pricing keys")

        except Exception as e:
            logger.error(f"Error processing analysis results: {e}")

    def _process_project_data(self) -> None:
        """Process project data and generate component-related keys"""
        try:
            # Extract component data
            components = {}

            # PV modules
            if 'selected_module' in self.project_data:
                module_data = self.project_data['selected_module']
                if isinstance(module_data, dict):
                    components['module_price'] = module_data.get('price_euro', 0)
                    components['module_quantity'] = self.project_data.get('module_quantity', 0)
                    components['module_total'] = (
                        module_data.get('price_euro', 0) *
                        self.project_data.get('module_quantity', 0)
                    )

            # Inverters
            if 'selected_inverter' in self.project_data:
                inverter_data = self.project_data['selected_inverter']
                if isinstance(inverter_data, dict):
                    components['inverter_price'] = inverter_data.get('price_euro', 0)
                    components['inverter_quantity'] = self.project_data.get('inverter_quantity', 1)
                    components['inverter_total'] = (
                        inverter_data.get('price_euro', 0) *
                        self.project_data.get('inverter_quantity', 1)
                    )

            # Storage
            if 'selected_storage' in self.project_data:
                storage_data = self.project_data['selected_storage']
                if isinstance(storage_data, dict):
                    components['storage_price'] = storage_data.get('price_euro', 0)
                    components['storage_quantity'] = self.project_data.get('storage_quantity', 1)
                    components['storage_total'] = (
                        storage_data.get('price_euro', 0) *
                        self.project_data.get('storage_quantity', 1)
                    )

            if components:
                project_keys = self.key_manager.generate_keys(
                    components,
                    prefix="PROJECT",
                    category=KeyCategory.COMPONENTS
                )
                logger.debug(f"Generated {len(project_keys)} project component keys")

        except Exception as e:
            logger.error(f"Error processing project data: {e}")

    def _get_keys_by_category_safe(self, category: KeyCategory) -> dict[str, Any]:
        """Safely get keys by category with fallback"""
        try:
            if hasattr(self.key_manager, 'get_keys_by_category'):
                return self.key_manager.get_keys_by_category(category)
            # Fallback: filter all keys by category
            all_keys = self.key_manager.get_all_keys()
            category_keys = {}
            for key, value in all_keys.items():
                # Simple category matching based on key name
                if category.value.upper() in key.upper():
                    category_keys[key] = value
            return category_keys
        except Exception as e:
            logger.error(f"Error getting keys by category {category}: {e}")
            return {}

    def generate_pricing_breakdown_data(self) -> dict[str, Any]:
        """Generate comprehensive pricing breakdown data for PDF templates
        
        Returns:
            Dictionary with pricing breakdown data
        """
        try:
            breakdown = {
                'components': {},
                'modifications': {},
                'totals': {},
                'vat': {},
                'summary': {}
            }

            # Get keys by category
            component_keys = self._get_keys_by_category_safe(KeyCategory.COMPONENTS)
            discount_keys = self._get_keys_by_category_safe(KeyCategory.DISCOUNTS)
            surcharge_keys = self._get_keys_by_category_safe(KeyCategory.SURCHARGES)
            vat_keys = self._get_keys_by_category_safe(KeyCategory.VAT)
            total_keys = self._get_keys_by_category_safe(KeyCategory.TOTALS)

            # Format for breakdown
            breakdown['components'] = self.key_manager.format_for_pdf(component_keys)
            breakdown['modifications'] = {
                'discounts': self.key_manager.format_for_pdf(discount_keys),
                'surcharges': self.key_manager.format_for_pdf(surcharge_keys)
            }
            breakdown['vat'] = self.key_manager.format_for_pdf(vat_keys)
            breakdown['totals'] = self.key_manager.format_for_pdf(total_keys)

            # Generate summary
            breakdown['summary'] = self._generate_pricing_summary()

            return breakdown

        except Exception as e:
            logger.error(f"Error generating pricing breakdown: {e}")
            return {}

    def _generate_pricing_summary(self) -> dict[str, str]:
        """Generate pricing summary for PDF display"""
        try:
            summary = {}

            # Get net and gross totals
            net_total = 0.0
            gross_total = 0.0
            vat_amount = 0.0

            # Try to get totals from different sources
            total_keys = self._get_keys_by_category_safe(KeyCategory.TOTALS)

            for key, value in total_keys.items():
                if 'NET_TOTAL' in key.upper():
                    try:
                        net_total = float(value)
                    except (ValueError, TypeError):
                        pass
                elif 'GROSS_TOTAL' in key.upper():
                    try:
                        gross_total = float(value)
                    except (ValueError, TypeError):
                        pass

            # Get VAT amount
            vat_keys = self._get_keys_by_category_safe(KeyCategory.VAT)
            for key, value in vat_keys.items():
                if 'VAT_AMOUNT' in key.upper():
                    try:
                        vat_amount = float(value)
                    except (ValueError, TypeError):
                        pass

            # Format summary
            summary['net_total'] = self._format_currency(net_total)
            summary['vat_amount'] = self._format_currency(vat_amount)
            summary['gross_total'] = self._format_currency(gross_total)

            # Calculate VAT rate if possible
            if net_total > 0 and vat_amount > 0:
                vat_rate = (vat_amount / net_total) * 100
                summary['vat_rate'] = f"{vat_rate:.1f}%"
            else:
                summary['vat_rate'] = "19,0%"  # Default German VAT rate

            return summary

        except Exception as e:
            logger.error(f"Error generating pricing summary: {e}")
            return {}

    def _format_currency(self, amount: float) -> str:
        """Format currency amount in German format"""
        try:
            # German formatting: dot as thousands separator, comma as decimal
            formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return f"{formatted} €"
        except (ValueError, TypeError):
            return "0,00 €"

    def get_enhanced_dynamic_data(self) -> dict[str, str]:
        """Get enhanced dynamic data including pricing keys
        
        Returns:
            Dictionary with all dynamic data for PDF templates
        """
        try:
            # Get base dynamic data from existing system
            base_data = build_dynamic_data(
                self.project_data,
                self.analysis_results,
                self.company_info
            )

            # Add pricing keys
            enhanced_data = dict(base_data)
            enhanced_data.update(self.pricing_keys)

            # Add pricing breakdown data
            breakdown = self.generate_pricing_breakdown_data()

            # Add formatted pricing summary keys
            summary = breakdown.get('summary', {})
            for key, value in summary.items():
                enhanced_data[f"PRICING_SUMMARY_{key.upper()}"] = value

            # Add component totals
            components = breakdown.get('components', {})
            for key, value in components.items():
                enhanced_data[f"PRICING_{key}"] = value

            # Add modification totals
            modifications = breakdown.get('modifications', {})
            for mod_type, mod_data in modifications.items():
                for key, value in mod_data.items():
                    enhanced_data[f"PRICING_{mod_type.upper()}_{key}"] = value

            logger.info(f"Enhanced dynamic data with {len(enhanced_data)} total keys")
            return enhanced_data

        except Exception as e:
            logger.error(f"Error getting enhanced dynamic data: {e}")
            # Return base data as fallback
            try:
                return build_dynamic_data(
                    self.project_data,
                    self.analysis_results,
                    self.company_info
                )
            except Exception:
                return {}

    def generate_pdf_with_pricing(self,
                                  filename: str | None = None,
                                  **kwargs) -> bytes | None:
        """Generate PDF with integrated pricing data
        
        Args:
            filename: Optional filename for PDF output
            **kwargs: Additional arguments for PDF generation
            
        Returns:
            PDF bytes or None if generation failed
        """
        try:
            # Get enhanced dynamic data
            enhanced_data = self.get_enhanced_dynamic_data()

            # Update analysis results with enhanced data
            enhanced_analysis = dict(self.analysis_results)
            enhanced_analysis.update(enhanced_data)

            # Generate PDF using existing system with enhanced data
            pdf_bytes = generate_offer_pdf(
                project_data=self.project_data,
                analysis_results=enhanced_analysis,
                company_info=self.company_info,
                **kwargs
            )

            if pdf_bytes:
                logger.info("Successfully generated PDF with pricing integration")

                # Save to file if filename provided
                if filename:
                    try:
                        with open(filename, 'wb') as f:
                            f.write(pdf_bytes)
                        logger.info(f"PDF saved to {filename}")
                    except Exception as e:
                        logger.error(f"Error saving PDF to file: {e}")

                return pdf_bytes
            logger.error("PDF generation returned empty result")
            return None

        except Exception as e:
            logger.error(f"Error generating PDF with pricing: {e}")
            return None


def generate_enhanced_pdf_with_pricing(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    company_info: dict[str, Any],
    pricing_data: dict[str, Any] | None = None,
    filename: str | None = None,
    **kwargs
) -> bytes | None:
    """Generate enhanced PDF with integrated pricing system
    
    Args:
        project_data: Project configuration data
        analysis_results: Analysis and calculation results
        company_info: Company information
        pricing_data: Optional pricing calculation results
        filename: Optional filename for PDF output
        **kwargs: Additional arguments for PDF generation
        
    Returns:
        PDF bytes or None if generation failed
    """
    try:
        # Create enhanced PDF generator
        pdf_generator = EnhancedPDFGenerator(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            pricing_data=pricing_data
        )

        # Generate PDF
        return pdf_generator.generate_pdf_with_pricing(
            filename=filename,
            **kwargs
        )

    except Exception as e:
        logger.error(f"Error in enhanced PDF generation: {e}")
        return None


def create_pricing_breakdown_section(pricing_data: dict[str, Any]) -> dict[str, Any]:
    """Create pricing breakdown section data for PDF templates
    
    Args:
        pricing_data: Pricing calculation results
        
    Returns:
        Dictionary with pricing breakdown section data
    """
    try:
        key_manager = DynamicKeyManager()

        # Generate keys for all pricing components
        all_keys = {}

        # Process different pricing categories
        categories = [
            ('components', KeyCategory.COMPONENTS),
            ('discounts', KeyCategory.DISCOUNTS),
            ('surcharges', KeyCategory.SURCHARGES),
            ('vat', KeyCategory.VAT),
            ('totals', KeyCategory.TOTALS)
        ]

        for category_name, category_enum in categories:
            category_data = pricing_data.get(category_name, {})
            if category_data:
                category_keys = key_manager.generate_keys(
                    category_data,
                    prefix=category_name.upper(),
                    category=category_enum
                )
                all_keys.update(category_keys)

        # Format for PDF
        formatted_keys = key_manager.format_for_pdf(all_keys)

        # Create section structure
        section_data = {
            'title': 'Preisaufstellung',
            'keys': formatted_keys,
            'categories': {
                'components': key_manager.get_all_keys('components'),
                'discounts': key_manager.get_all_keys('discounts'),
                'surcharges': key_manager.get_all_keys('surcharges'),
                'vat': key_manager.get_all_keys('vat'),
                'totals': key_manager.get_all_keys('totals')
            }
        }

        return section_data

    except Exception as e:
        logger.error(f"Error creating pricing breakdown section: {e}")
        return {}


def update_pdf_placeholders_with_pricing(
    base_placeholders: dict[str, str],
    pricing_data: dict[str, Any]
) -> dict[str, str]:
    """Update PDF placeholders with pricing data
    
    Args:
        base_placeholders: Base placeholder mapping
        pricing_data: Pricing calculation results
        
    Returns:
        Updated placeholder mapping with pricing keys
    """
    try:
        # Create key manager
        key_manager = DynamicKeyManager()

        # Generate pricing keys
        pricing_keys = key_manager.generate_keys(
            pricing_data,
            prefix="PRICING",
            category=KeyCategory.PRICING
        )

        # Format for PDF
        formatted_pricing_keys = key_manager.format_for_pdf(pricing_keys)

        # Merge with base placeholders
        updated_placeholders = dict(base_placeholders)
        updated_placeholders.update(formatted_pricing_keys)

        logger.info(f"Updated placeholders with {len(formatted_pricing_keys)} pricing keys")
        return updated_placeholders

    except Exception as e:
        logger.error(f"Error updating placeholders with pricing: {e}")
        return base_placeholders
