"""
CRM Advanced Service

This service wraps all CRM modules from the legacy system and provides
advanced CRM functionality including lead scoring, sales pipeline automation,
email campaigns, customer segmentation, forecasting, contract management,
warranty tracking, customer feedback, geo mapping, and knowledge base.

Requirements: 1.3, 6.1
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

# Add parent directory to path to import legacy modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import legacy CRM modules
try:
    from crm.features.lead_scoring import LeadScoringEngine
    from crm.features.email_manager import EmailManager
    from crm.features.forecasting_engine import ForecastingEngine
    from crm.features.contract_manager import ContractManager
    from crm.features.feedback_manager import FeedbackManager
    from crm.features.geo_mapper import GeoMapper
    from crm.features.knowledge_base import KnowledgeBase
    from crm.features.offer_tracker import OfferTracker
    from crm.features.task_manager import TaskManager
    from crm.features.note_manager import NoteManager
    from crm.features.tag_manager import TagManager
    from crm.features.reporting_engine import ReportingEngine
    from crm.features.dashboard_widgets import DashboardWidgets
    from crm.features.template_manager import TemplateManager
    from crm.features.call_manager import CallManager
except ImportError as e:
    logging.warning(f"Could not import legacy CRM modules: {e}")
    # Define placeholder classes for development
    class LeadScoringEngine: pass
    class EmailManager: pass
    class ForecastingEngine: pass
    class ContractManager: pass
    class FeedbackManager: pass
    class GeoMapper: pass
    class KnowledgeBase: pass
    class OfferTracker: pass
    class TaskManager: pass
    class NoteManager: pass
    class TagManager: pass
    class ReportingEngine: pass
    class DashboardWidgets: pass
    class TemplateManager: pass
    class CallManager: pass


logger = logging.getLogger(__name__)


class CRMAdvancedService:
    """
    Advanced CRM Service that wraps all legacy CRM modules and provides
    comprehensive customer relationship management functionality.
    """
    
    def __init__(self, database_path: str = "crm_database.db"):
        """
        Initialize CRM Advanced Service with all sub-modules.
        
        Args:
            database_path: Path to CRM database
        """
        self.database_path = database_path
        
        # Initialize all CRM modules
        try:
            self.lead_scoring = LeadScoringEngine(database_path)
            self.email_manager = EmailManager(database_path)
            self.forecasting = ForecastingEngine(database_path)
            self.contract_manager = ContractManager(database_path)
            self.feedback_manager = FeedbackManager(database_path)
            self.geo_mapper = GeoMapper(database_path)
            self.knowledge_base = KnowledgeBase(database_path)
            self.offer_tracker = OfferTracker(database_path)
            self.task_manager = TaskManager(database_path)
            self.note_manager = NoteManager(database_path)
            self.tag_manager = TagManager(database_path)
            self.reporting = ReportingEngine(database_path)
            self.dashboard = DashboardWidgets(database_path)
            self.template_manager = TemplateManager(database_path)
            self.call_manager = CallManager(database_path)
            
            logger.info("CRM Advanced Service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CRM modules: {e}")
            raise
    
    # ==================== Lead Scoring ====================
    
    def calculate_lead_score(self, lead_id: int) -> Dict[str, Any]:
        """
        Calculate lead score using the lead scoring algorithm.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            Dictionary with lead score and breakdown
        """
        try:
            return self.lead_scoring.calculate_score(lead_id)
        except Exception as e:
            logger.error(f"Error calculating lead score: {e}")
            raise
    
    def get_lead_scores(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Get lead scores for multiple leads with optional filtering.
        
        Args:
            filters: Optional filters for leads
            
        Returns:
            List of lead scores
        """
        try:
            return self.lead_scoring.get_scores(filters)
        except Exception as e:
            logger.error(f"Error getting lead scores: {e}")
            raise
    
    def update_lead_score_weights(self, weights: Dict[str, float]) -> bool:
        """
        Update the weights used in lead scoring algorithm.
        
        Args:
            weights: Dictionary of scoring weights
            
        Returns:
            True if successful
        """
        try:
            return self.lead_scoring.update_weights(weights)
        except Exception as e:
            logger.error(f"Error updating lead score weights: {e}")
            raise
    
    # ==================== Sales Pipeline Automation ====================
    
    def automate_pipeline_stage(self, lead_id: int, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically move lead through pipeline stages based on rules.
        
        Args:
            lead_id: ID of the lead
            rules: Automation rules
            
        Returns:
            Dictionary with automation results
        """
        try:
            # Get current lead score
            score_data = self.lead_scoring.calculate_score(lead_id)
            score = score_data.get('total_score', 0)
            
            # Apply automation rules
            result = {
                'lead_id': lead_id,
                'current_score': score,
                'actions_taken': []
            }
            
            # Example automation: Move to qualified if score > threshold
            if score >= rules.get('qualification_threshold', 70):
                result['actions_taken'].append('moved_to_qualified')
            
            # Example: Assign to sales rep if score > threshold
            if score >= rules.get('assignment_threshold', 80):
                result['actions_taken'].append('assigned_to_sales')
            
            return result
        except Exception as e:
            logger.error(f"Error in pipeline automation: {e}")
            raise
    
    # ==================== Email Campaign Management ====================
    
    def create_email_campaign(self, campaign_data: Dict[str, Any]) -> int:
        """
        Create a new email campaign.
        
        Args:
            campaign_data: Campaign configuration
            
        Returns:
            Campaign ID
        """
        try:
            return self.email_manager.create_campaign(campaign_data)
        except Exception as e:
            logger.error(f"Error creating email campaign: {e}")
            raise
    
    def send_campaign_email(self, campaign_id: int, recipient_ids: List[int]) -> Dict[str, Any]:
        """
        Send campaign emails to recipients.
        
        Args:
            campaign_id: ID of the campaign
            recipient_ids: List of recipient IDs
            
        Returns:
            Dictionary with send results
        """
        try:
            return self.email_manager.send_campaign(campaign_id, recipient_ids)
        except Exception as e:
            logger.error(f"Error sending campaign emails: {e}")
            raise
    
    def get_campaign_analytics(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get analytics for an email campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary with campaign analytics
        """
        try:
            return self.email_manager.get_campaign_analytics(campaign_id)
        except Exception as e:
            logger.error(f"Error getting campaign analytics: {e}")
            raise
    
    def schedule_campaign(self, campaign_id: int, schedule_time: datetime) -> bool:
        """
        Schedule an email campaign for future sending.
        
        Args:
            campaign_id: ID of the campaign
            schedule_time: When to send the campaign
            
        Returns:
            True if scheduled successfully
        """
        try:
            return self.email_manager.schedule_campaign(campaign_id, schedule_time)
        except Exception as e:
            logger.error(f"Error scheduling campaign: {e}")
            raise
    
    # ==================== Customer Segmentation ====================
    
    def create_customer_segment(self, segment_data: Dict[str, Any]) -> int:
        """
        Create a customer segment based on criteria.
        
        Args:
            segment_data: Segment definition and criteria
            
        Returns:
            Segment ID
        """
        try:
            # Use tag manager for segmentation
            return self.tag_manager.create_segment(segment_data)
        except Exception as e:
            logger.error(f"Error creating customer segment: {e}")
            raise
    
    def get_segment_customers(self, segment_id: int) -> List[Dict[str, Any]]:
        """
        Get all customers in a segment.
        
        Args:
            segment_id: ID of the segment
            
        Returns:
            List of customers in segment
        """
        try:
            return self.tag_manager.get_segment_members(segment_id)
        except Exception as e:
            logger.error(f"Error getting segment customers: {e}")
            raise
    
    def analyze_segment(self, segment_id: int) -> Dict[str, Any]:
        """
        Analyze a customer segment for insights.
        
        Args:
            segment_id: ID of the segment
            
        Returns:
            Dictionary with segment analysis
        """
        try:
            customers = self.tag_manager.get_segment_members(segment_id)
            
            # Calculate segment metrics
            analysis = {
                'segment_id': segment_id,
                'total_customers': len(customers),
                'avg_lifetime_value': 0,
                'avg_engagement_score': 0,
                'top_products': [],
                'geographic_distribution': {}
            }
            
            # Add more sophisticated analysis here
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing segment: {e}")
            raise
    
    # ==================== Forecasting Engine ====================
    
    def generate_sales_forecast(self, period: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate sales forecast for specified period.
        
        Args:
            period: Forecast period (month, quarter, year)
            parameters: Optional forecast parameters
            
        Returns:
            Dictionary with forecast data
        """
        try:
            return self.forecasting.generate_forecast(period, parameters)
        except Exception as e:
            logger.error(f"Error generating sales forecast: {e}")
            raise
    
    def get_pipeline_forecast(self) -> Dict[str, Any]:
        """
        Get forecast based on current sales pipeline.
        
        Returns:
            Dictionary with pipeline forecast
        """
        try:
            return self.forecasting.get_pipeline_forecast()
        except Exception as e:
            logger.error(f"Error getting pipeline forecast: {e}")
            raise
    
    def analyze_forecast_accuracy(self, period: str) -> Dict[str, Any]:
        """
        Analyze accuracy of past forecasts.
        
        Args:
            period: Period to analyze
            
        Returns:
            Dictionary with accuracy metrics
        """
        try:
            return self.forecasting.analyze_accuracy(period)
        except Exception as e:
            logger.error(f"Error analyzing forecast accuracy: {e}")
            raise
    
    # ==================== Contract Management ====================
    
    def create_contract(self, contract_data: Dict[str, Any]) -> int:
        """
        Create a new contract.
        
        Args:
            contract_data: Contract details
            
        Returns:
            Contract ID
        """
        try:
            return self.contract_manager.create_contract(contract_data)
        except Exception as e:
            logger.error(f"Error creating contract: {e}")
            raise
    
    def get_contract(self, contract_id: int) -> Dict[str, Any]:
        """
        Get contract details.
        
        Args:
            contract_id: ID of the contract
            
        Returns:
            Contract details
        """
        try:
            return self.contract_manager.get_contract(contract_id)
        except Exception as e:
            logger.error(f"Error getting contract: {e}")
            raise
    
    def update_contract_status(self, contract_id: int, status: str) -> bool:
        """
        Update contract status.
        
        Args:
            contract_id: ID of the contract
            status: New status
            
        Returns:
            True if successful
        """
        try:
            return self.contract_manager.update_status(contract_id, status)
        except Exception as e:
            logger.error(f"Error updating contract status: {e}")
            raise
    
    def get_expiring_contracts(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get contracts expiring within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of expiring contracts
        """
        try:
            return self.contract_manager.get_expiring_contracts(days)
        except Exception as e:
            logger.error(f"Error getting expiring contracts: {e}")
            raise
    
    # ==================== Warranty Tracking ====================
    
    def register_warranty(self, warranty_data: Dict[str, Any]) -> int:
        """
        Register a new warranty.
        
        Args:
            warranty_data: Warranty details
            
        Returns:
            Warranty ID
        """
        try:
            # Use contract manager for warranty tracking
            return self.contract_manager.register_warranty(warranty_data)
        except Exception as e:
            logger.error(f"Error registering warranty: {e}")
            raise
    
    def get_warranty_status(self, warranty_id: int) -> Dict[str, Any]:
        """
        Get warranty status and details.
        
        Args:
            warranty_id: ID of the warranty
            
        Returns:
            Warranty status and details
        """
        try:
            return self.contract_manager.get_warranty_status(warranty_id)
        except Exception as e:
            logger.error(f"Error getting warranty status: {e}")
            raise
    
    def get_active_warranties(self, customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all active warranties, optionally filtered by customer.
        
        Args:
            customer_id: Optional customer ID filter
            
        Returns:
            List of active warranties
        """
        try:
            return self.contract_manager.get_active_warranties(customer_id)
        except Exception as e:
            logger.error(f"Error getting active warranties: {e}")
            raise
    
    # ==================== Customer Feedback System ====================
    
    def submit_feedback(self, feedback_data: Dict[str, Any]) -> int:
        """
        Submit customer feedback.
        
        Args:
            feedback_data: Feedback details
            
        Returns:
            Feedback ID
        """
        try:
            return self.feedback_manager.submit_feedback(feedback_data)
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            raise
    
    def get_feedback(self, feedback_id: int) -> Dict[str, Any]:
        """
        Get feedback details.
        
        Args:
            feedback_id: ID of the feedback
            
        Returns:
            Feedback details
        """
        try:
            return self.feedback_manager.get_feedback(feedback_id)
        except Exception as e:
            logger.error(f"Error getting feedback: {e}")
            raise
    
    def analyze_feedback(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze customer feedback with optional filters.
        
        Args:
            filters: Optional filters for feedback
            
        Returns:
            Dictionary with feedback analysis
        """
        try:
            return self.feedback_manager.analyze_feedback(filters)
        except Exception as e:
            logger.error(f"Error analyzing feedback: {e}")
            raise
    
    def get_feedback_trends(self, period: str = "month") -> Dict[str, Any]:
        """
        Get feedback trends over time.
        
        Args:
            period: Time period for trends
            
        Returns:
            Dictionary with trend data
        """
        try:
            return self.feedback_manager.get_trends(period)
        except Exception as e:
            logger.error(f"Error getting feedback trends: {e}")
            raise
    
    # ==================== Geo Mapping ====================
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        Convert address to geographic coordinates.
        
        Args:
            address: Address string
            
        Returns:
            Dictionary with coordinates and location data
        """
        try:
            return self.geo_mapper.geocode(address)
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            raise
    
    def get_customers_in_area(self, center: Dict[str, float], radius_km: float) -> List[Dict[str, Any]]:
        """
        Get customers within specified radius of a location.
        
        Args:
            center: Dictionary with 'lat' and 'lon' keys
            radius_km: Radius in kilometers
            
        Returns:
            List of customers in area
        """
        try:
            return self.geo_mapper.get_customers_in_radius(center, radius_km)
        except Exception as e:
            logger.error(f"Error getting customers in area: {e}")
            raise
    
    def create_territory_map(self, territories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create sales territory map.
        
        Args:
            territories: List of territory definitions
            
        Returns:
            Dictionary with territory map data
        """
        try:
            return self.geo_mapper.create_territory_map(territories)
        except Exception as e:
            logger.error(f"Error creating territory map: {e}")
            raise
    
    def optimize_route(self, locations: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Optimize route for visiting multiple locations.
        
        Args:
            locations: List of locations with lat/lon
            
        Returns:
            Dictionary with optimized route
        """
        try:
            return self.geo_mapper.optimize_route(locations)
        except Exception as e:
            logger.error(f"Error optimizing route: {e}")
            raise
    
    # ==================== Knowledge Base ====================
    
    def create_kb_article(self, article_data: Dict[str, Any]) -> int:
        """
        Create a knowledge base article.
        
        Args:
            article_data: Article content and metadata
            
        Returns:
            Article ID
        """
        try:
            return self.knowledge_base.create_article(article_data)
        except Exception as e:
            logger.error(f"Error creating KB article: {e}")
            raise
    
    def search_kb(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            filters: Optional filters
            
        Returns:
            List of matching articles
        """
        try:
            return self.knowledge_base.search(query, filters)
        except Exception as e:
            logger.error(f"Error searching KB: {e}")
            raise
    
    def get_kb_article(self, article_id: int) -> Dict[str, Any]:
        """
        Get knowledge base article.
        
        Args:
            article_id: ID of the article
            
        Returns:
            Article details
        """
        try:
            return self.knowledge_base.get_article(article_id)
        except Exception as e:
            logger.error(f"Error getting KB article: {e}")
            raise
    
    def update_kb_article(self, article_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update knowledge base article.
        
        Args:
            article_id: ID of the article
            updates: Updates to apply
            
        Returns:
            True if successful
        """
        try:
            return self.knowledge_base.update_article(article_id, updates)
        except Exception as e:
            logger.error(f"Error updating KB article: {e}")
            raise
    
    def get_popular_kb_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular knowledge base articles.
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of popular articles
        """
        try:
            return self.knowledge_base.get_popular_articles(limit)
        except Exception as e:
            logger.error(f"Error getting popular KB articles: {e}")
            raise
    
    # ==================== Additional CRM Features ====================
    
    def create_offer(self, offer_data: Dict[str, Any]) -> int:
        """
        Create a new offer.
        
        Args:
            offer_data: Offer details
            
        Returns:
            Offer ID
        """
        try:
            return self.offer_tracker.create_offer(offer_data)
        except Exception as e:
            logger.error(f"Error creating offer: {e}")
            raise
    
    def track_offer_status(self, offer_id: int) -> Dict[str, Any]:
        """
        Track offer status and history.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Offer status and history
        """
        try:
            return self.offer_tracker.track_status(offer_id)
        except Exception as e:
            logger.error(f"Error tracking offer status: {e}")
            raise
    
    def create_task(self, task_data: Dict[str, Any]) -> int:
        """
        Create a new task.
        
        Args:
            task_data: Task details
            
        Returns:
            Task ID
        """
        try:
            return self.task_manager.create_task(task_data)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    def get_tasks(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Get tasks with optional filtering.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of tasks
        """
        try:
            return self.task_manager.get_tasks(filters)
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            raise
    
    def create_note(self, note_data: Dict[str, Any]) -> int:
        """
        Create a new note.
        
        Args:
            note_data: Note details
            
        Returns:
            Note ID
        """
        try:
            return self.note_manager.create_note(note_data)
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            raise
    
    def log_call(self, call_data: Dict[str, Any]) -> int:
        """
        Log a customer call.
        
        Args:
            call_data: Call details
            
        Returns:
            Call log ID
        """
        try:
            return self.call_manager.log_call(call_data)
        except Exception as e:
            logger.error(f"Error logging call: {e}")
            raise
    
    def get_call_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """
        Get call history for a customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            List of call logs
        """
        try:
            return self.call_manager.get_call_history(customer_id)
        except Exception as e:
            logger.error(f"Error getting call history: {e}")
            raise
    
    def generate_report(self, report_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a CRM report.
        
        Args:
            report_type: Type of report to generate
            parameters: Report parameters
            
        Returns:
            Report data
        """
        try:
            return self.reporting.generate_report(report_type, parameters)
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def get_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get dashboard data for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dashboard data
        """
        try:
            return self.dashboard.get_dashboard_data(user_id)
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all CRM modules.
        
        Returns:
            Dictionary with health status of each module
        """
        health_status = {
            'overall': 'healthy',
            'modules': {}
        }
        
        modules = [
            ('lead_scoring', self.lead_scoring),
            ('email_manager', self.email_manager),
            ('forecasting', self.forecasting),
            ('contract_manager', self.contract_manager),
            ('feedback_manager', self.feedback_manager),
            ('geo_mapper', self.geo_mapper),
            ('knowledge_base', self.knowledge_base),
            ('offer_tracker', self.offer_tracker),
            ('task_manager', self.task_manager),
            ('note_manager', self.note_manager),
            ('tag_manager', self.tag_manager),
            ('reporting', self.reporting),
            ('dashboard', self.dashboard),
            ('template_manager', self.template_manager),
            ('call_manager', self.call_manager)
        ]
        
        for module_name, module in modules:
            try:
                if hasattr(module, 'health_check'):
                    health_status['modules'][module_name] = module.health_check()
                else:
                    health_status['modules'][module_name] = 'ok'
            except Exception as e:
                health_status['modules'][module_name] = f'error: {str(e)}'
                health_status['overall'] = 'degraded'
        
        return health_status
