"""
Lead Management Service
Implements lead capture, scoring, assignment, nurturing, and conversion tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import logging

from backend.models.lead_models import (
    Lead, LeadActivity, LeadScoringRule, LeadAssignmentRule,
    LeadNurturingCampaign, LeadSourceAnalytics,
    LeadStatus, LeadSource, LeadPriority
)
from backend.models.lead_schemas import (
    LeadCreate, LeadUpdate, LeadActivityCreate, LeadActivityUpdate,
    LeadScoringRuleCreate, LeadScoringRuleUpdate,
    LeadAssignmentRuleCreate, LeadAssignmentRuleUpdate,
    LeadNurturingCampaignCreate, LeadNurturingCampaignUpdate,
    LeadScoreBreakdown, LeadDashboardMetrics
)

logger = logging.getLogger(__name__)


class LeadService:
    """Service for managing leads"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Lead CRUD Operations
    
    def create_lead(self, lead_data: LeadCreate, created_by_id: Optional[int] = None) -> Lead:
        """Create a new lead"""
        try:
            # Convert interested_in list to JSON string
            interested_in_json = json.dumps(lead_data.interested_in) if lead_data.interested_in else None
            
            lead = Lead(
                **lead_data.dict(exclude={'interested_in'}),
                interested_in=interested_in_json,
                created_by_id=created_by_id
            )
            
            self.db.add(lead)
            self.db.flush()
            
            # Calculate initial score
            lead.score = self._calculate_lead_score(lead)
            
            # Auto-assign based on rules
            self._auto_assign_lead(lead)
            
            self.db.commit()
            self.db.refresh(lead)
            
            logger.info(f"Created lead: {lead.id} - {lead.email}")
            return lead
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating lead: {str(e)}")
            raise
    
    def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Get a lead by ID"""
        return self.db.query(Lead).filter(Lead.id == lead_id).first()
    
    def get_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None,
        priority: Optional[LeadPriority] = None,
        assigned_to_id: Optional[int] = None,
        min_score: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Lead], int]:
        """Get leads with filtering and pagination"""
        query = self.db.query(Lead)
        
        # Apply filters
        if status:
            query = query.filter(Lead.status == status)
        if source:
            query = query.filter(Lead.source == source)
        if priority:
            query = query.filter(Lead.priority == priority)
        if assigned_to_id:
            query = query.filter(Lead.assigned_to_id == assigned_to_id)
        if min_score is not None:
            query = query.filter(Lead.score >= min_score)
        if search:
            search_filter = or_(
                Lead.first_name.ilike(f"%{search}%"),
                Lead.last_name.ilike(f"%{search}%"),
                Lead.email.ilike(f"%{search}%"),
                Lead.company.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        leads = query.order_by(desc(Lead.created_at)).offset(skip).limit(limit).all()
        
        return leads, total
    
    def update_lead(self, lead_id: int, lead_data: LeadUpdate) -> Optional[Lead]:
        """Update a lead"""
        try:
            lead = self.get_lead(lead_id)
            if not lead:
                return None
            
            # Update fields
            update_data = lead_data.dict(exclude_unset=True, exclude={'interested_in'})
            for field, value in update_data.items():
                setattr(lead, field, value)
            
            # Handle interested_in separately
            if lead_data.interested_in is not None:
                lead.interested_in = json.dumps(lead_data.interested_in)
            
            # Recalculate score if relevant fields changed
            if any(field in update_data for field in ['status', 'source', 'estimated_value']):
                lead.score = self._calculate_lead_score(lead)
            
            self.db.commit()
            self.db.refresh(lead)
            
            logger.info(f"Updated lead: {lead.id}")
            return lead
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating lead {lead_id}: {str(e)}")
            raise
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead"""
        try:
            lead = self.get_lead(lead_id)
            if not lead:
                return False
            
            self.db.delete(lead)
            self.db.commit()
            
            logger.info(f"Deleted lead: {lead_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting lead {lead_id}: {str(e)}")
            raise
    
    # Lead Scoring
    
    def _calculate_lead_score(self, lead: Lead) -> int:
        """Calculate lead score based on scoring rules"""
        try:
            rules = self.db.query(LeadScoringRule).filter(
                LeadScoringRule.active == True
            ).order_by(LeadScoringRule.priority.desc()).all()
            
            total_score = 0
            rules_applied = []
            
            for rule in rules:
                points = self._evaluate_scoring_rule(lead, rule)
                if points != 0:
                    total_score += points
                    rules_applied.append({
                        'rule_name': rule.name,
                        'points': points,
                        'category': rule.category
                    })
            
            # Store breakdown
            lead.score_breakdown = json.dumps(rules_applied)
            
            return max(0, total_score)  # Ensure non-negative score
            
        except Exception as e:
            logger.error(f"Error calculating lead score: {str(e)}")
            return 0
    
    def _evaluate_scoring_rule(self, lead: Lead, rule: LeadScoringRule) -> int:
        """Evaluate a single scoring rule against a lead"""
        try:
            # Get field value from lead
            field_value = getattr(lead, rule.field, None)
            
            if field_value is None:
                return 0
            
            # Convert to string for comparison
            field_value_str = str(field_value)
            rule_value = rule.value
            
            # Evaluate based on operator
            if rule.operator == "equals":
                return rule.points if field_value_str == rule_value else 0
            elif rule.operator == "not_equals":
                return rule.points if field_value_str != rule_value else 0
            elif rule.operator == "contains":
                return rule.points if rule_value in field_value_str else 0
            elif rule.operator == "not_contains":
                return rule.points if rule_value not in field_value_str else 0
            elif rule.operator == "greater_than":
                try:
                    return rule.points if float(field_value_str) > float(rule_value) else 0
                except ValueError:
                    return 0
            elif rule.operator == "less_than":
                try:
                    return rule.points if float(field_value_str) < float(rule_value) else 0
                except ValueError:
                    return 0
            elif rule.operator == "is_empty":
                return rule.points if not field_value_str else 0
            elif rule.operator == "is_not_empty":
                return rule.points if field_value_str else 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Error evaluating scoring rule {rule.id}: {str(e)}")
            return 0
    
    def get_lead_score_breakdown(self, lead_id: int) -> Optional[LeadScoreBreakdown]:
        """Get detailed score breakdown for a lead"""
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        
        rules_applied = json.loads(lead.score_breakdown) if lead.score_breakdown else []
        
        # Calculate category scores
        demographic_score = sum(r['points'] for r in rules_applied if r['category'] == 'demographic')
        behavioral_score = sum(r['points'] for r in rules_applied if r['category'] == 'behavioral')
        engagement_score = sum(r['points'] for r in rules_applied if r['category'] == 'engagement')
        
        return LeadScoreBreakdown(
            total_score=lead.score,
            rules_applied=rules_applied,
            demographic_score=demographic_score,
            behavioral_score=behavioral_score,
            engagement_score=engagement_score
        )
    
    def recalculate_all_scores(self) -> int:
        """Recalculate scores for all leads"""
        try:
            leads = self.db.query(Lead).all()
            count = 0
            
            for lead in leads:
                lead.score = self._calculate_lead_score(lead)
                count += 1
            
            self.db.commit()
            logger.info(f"Recalculated scores for {count} leads")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recalculating scores: {str(e)}")
            raise
    
    # Lead Assignment
    
    def _auto_assign_lead(self, lead: Lead) -> None:
        """Automatically assign lead based on assignment rules"""
        try:
            rules = self.db.query(LeadAssignmentRule).filter(
                LeadAssignmentRule.active == True
            ).order_by(LeadAssignmentRule.priority.desc()).all()
            
            for rule in rules:
                if self._evaluate_assignment_rule(lead, rule):
                    lead.assigned_to_id = rule.assign_to_user_id
                    lead.assigned_at = datetime.utcnow()
                    logger.info(f"Auto-assigned lead {lead.id} to user {rule.assign_to_user_id}")
                    break
                    
        except Exception as e:
            logger.error(f"Error auto-assigning lead: {str(e)}")
    
    def _evaluate_assignment_rule(self, lead: Lead, rule: LeadAssignmentRule) -> bool:
        """Evaluate if a lead matches assignment rule conditions"""
        try:
            conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
            
            for field, expected_value in conditions.items():
                actual_value = getattr(lead, field, None)
                if actual_value != expected_value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating assignment rule {rule.id}: {str(e)}")
            return False
    
    def assign_lead(self, lead_id: int, assign_to_user_id: int) -> Optional[Lead]:
        """Manually assign a lead to a user"""
        try:
            lead = self.get_lead(lead_id)
            if not lead:
                return None
            
            lead.assigned_to_id = assign_to_user_id
            lead.assigned_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(lead)
            
            logger.info(f"Assigned lead {lead_id} to user {assign_to_user_id}")
            return lead
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning lead: {str(e)}")
            raise
    
    # Lead Activities
    
    def create_activity(self, activity_data: LeadActivityCreate, created_by_id: Optional[int] = None) -> LeadActivity:
        """Create a lead activity"""
        try:
            activity = LeadActivity(
                **activity_data.dict(),
                created_by_id=created_by_id
            )
            
            self.db.add(activity)
            
            # Update lead contact tracking
            lead = self.get_lead(activity_data.lead_id)
            if lead:
                lead.contact_count += 1
                lead.last_contact_date = datetime.utcnow()
                if not lead.first_contact_date:
                    lead.first_contact_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(activity)
            
            logger.info(f"Created activity for lead {activity_data.lead_id}")
            return activity
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating activity: {str(e)}")
            raise
    
    def get_lead_activities(self, lead_id: int) -> List[LeadActivity]:
        """Get all activities for a lead"""
        return self.db.query(LeadActivity).filter(
            LeadActivity.lead_id == lead_id
        ).order_by(desc(LeadActivity.created_at)).all()
    
    # Lead Nurturing
    
    def create_nurturing_campaign(self, campaign_data: LeadNurturingCampaignCreate) -> LeadNurturingCampaign:
        """Create a lead nurturing campaign"""
        try:
            campaign = LeadNurturingCampaign(**campaign_data.dict())
            
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            
            logger.info(f"Created nurturing campaign for lead {campaign_data.lead_id}")
            return campaign
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating nurturing campaign: {str(e)}")
            raise
    
    def get_active_nurturing_campaigns(self) -> List[LeadNurturingCampaign]:
        """Get all active nurturing campaigns"""
        return self.db.query(LeadNurturingCampaign).filter(
            LeadNurturingCampaign.status == "active"
        ).all()
    
    # Lead Conversion
    
    def convert_lead(self, lead_id: int, customer_id: int) -> Optional[Lead]:
        """Convert a lead to a customer"""
        try:
            lead = self.get_lead(lead_id)
            if not lead:
                return None
            
            lead.converted = True
            lead.converted_at = datetime.utcnow()
            lead.converted_to_customer_id = customer_id
            lead.status = LeadStatus.WON
            
            self.db.commit()
            self.db.refresh(lead)
            
            logger.info(f"Converted lead {lead_id} to customer {customer_id}")
            return lead
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error converting lead: {str(e)}")
            raise
    
    def get_conversion_tracking(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get lead conversion tracking data"""
        leads = self.db.query(Lead).filter(
            and_(
                Lead.created_at >= start_date,
                Lead.created_at <= end_date
            )
        ).all()
        
        tracking_data = []
        for lead in leads:
            conversion_time_days = None
            if lead.converted_at and lead.first_contact_date:
                conversion_time_days = (lead.converted_at - lead.first_contact_date).days
            
            tracking_data.append({
                'lead_id': lead.id,
                'lead_name': f"{lead.first_name} {lead.last_name}",
                'source': lead.source,
                'created_at': lead.created_at,
                'first_contact_date': lead.first_contact_date,
                'converted_at': lead.converted_at,
                'conversion_time_days': conversion_time_days,
                'estimated_value': lead.estimated_value,
                'status': lead.status
            })
        
        return tracking_data
    
    # Analytics
    
    def get_dashboard_metrics(self) -> LeadDashboardMetrics:
        """Get lead dashboard metrics"""
        try:
            # Total leads
            total_leads = self.db.query(func.count(Lead.id)).scalar()
            
            # New leads (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_leads = self.db.query(func.count(Lead.id)).filter(
                Lead.created_at >= thirty_days_ago
            ).scalar()
            
            # Qualified leads
            qualified_leads = self.db.query(func.count(Lead.id)).filter(
                Lead.status == LeadStatus.QUALIFIED
            ).scalar()
            
            # Converted leads
            converted_leads = self.db.query(func.count(Lead.id)).filter(
                Lead.converted == True
            ).scalar()
            
            # Conversion rate
            conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
            
            # Average score
            average_score = self.db.query(func.avg(Lead.score)).scalar() or 0
            
            # Average conversion time
            avg_conversion_time = self.db.query(
                func.avg(func.julianday(Lead.converted_at) - func.julianday(Lead.first_contact_date))
            ).filter(Lead.converted == True).scalar() or 0
            
            # Total estimated value
            total_estimated_value = self.db.query(func.sum(Lead.estimated_value)).scalar() or 0
            
            # Leads by source
            leads_by_source = {}
            source_counts = self.db.query(
                Lead.source, func.count(Lead.id)
            ).group_by(Lead.source).all()
            for source, count in source_counts:
                leads_by_source[source.value] = count
            
            # Leads by status
            leads_by_status = {}
            status_counts = self.db.query(
                Lead.status, func.count(Lead.id)
            ).group_by(Lead.status).all()
            for status, count in status_counts:
                leads_by_status[status.value] = count
            
            # Leads by priority
            leads_by_priority = {}
            priority_counts = self.db.query(
                Lead.priority, func.count(Lead.id)
            ).group_by(Lead.priority).all()
            for priority, count in priority_counts:
                leads_by_priority[priority.value] = count
            
            return LeadDashboardMetrics(
                total_leads=total_leads,
                new_leads=new_leads,
                qualified_leads=qualified_leads,
                converted_leads=converted_leads,
                conversion_rate=round(conversion_rate, 2),
                average_score=round(average_score, 2),
                average_conversion_time_days=round(avg_conversion_time, 2),
                total_estimated_value=total_estimated_value,
                leads_by_source=leads_by_source,
                leads_by_status=leads_by_status,
                leads_by_priority=leads_by_priority
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            raise
    
    def get_source_analytics(self, start_date: datetime, end_date: datetime) -> List[LeadSourceAnalytics]:
        """Get lead source analytics"""
        return self.db.query(LeadSourceAnalytics).filter(
            and_(
                LeadSourceAnalytics.period_start >= start_date,
                LeadSourceAnalytics.period_end <= end_date
            )
        ).all()
