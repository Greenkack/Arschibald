"""
Sales Pipeline Service
Business logic for pipeline management, analytics, and forecasting
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from backend.models.pipeline_models import (
    PipelineStage, Opportunity, OpportunityActivity,
    OpportunityStageHistory, OpportunityProduct,
    PipelineForecast, PipelineAutomation,
    PipelineStageType, OpportunityStatus
)
from backend.models.pipeline_schemas import (
    PipelineStageCreate, PipelineStageUpdate,
    OpportunityCreate, OpportunityUpdate, OpportunityStageChange,
    OpportunityWin, OpportunityLoss,
    PipelineAnalytics, WinLossAnalysis, PipelineForecastData
)


class PipelineService:
    """Service for managing sales pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Pipeline Stage Management ====================
    
    def create_stage(self, stage_data: PipelineStageCreate, user_id: int) -> PipelineStage:
        """Create new pipeline stage"""
        stage = PipelineStage(
            **stage_data.dict(),
            created_by=user_id
        )
        self.db.add(stage)
        self.db.commit()
        self.db.refresh(stage)
        return stage
    
    def get_stages(self, include_inactive: bool = False) -> List[PipelineStage]:
        """Get all pipeline stages"""
        query = self.db.query(PipelineStage)
        if not include_inactive:
            query = query.filter(PipelineStage.is_active == True)
        return query.order_by(PipelineStage.order_index).all()
    
    def get_stage(self, stage_id: int) -> PipelineStage:
        """Get pipeline stage by ID"""
        stage = self.db.query(PipelineStage).filter(PipelineStage.id == stage_id).first()
        if not stage:
            raise HTTPException(status_code=404, detail="Pipeline stage not found")
        return stage
    
    def update_stage(self, stage_id: int, stage_data: PipelineStageUpdate) -> PipelineStage:
        """Update pipeline stage"""
        stage = self.get_stage(stage_id)
        
        if stage.is_system:
            raise HTTPException(status_code=400, detail="Cannot modify system stage")
        
        for key, value in stage_data.dict(exclude_unset=True).items():
            setattr(stage, key, value)
        
        stage.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(stage)
        return stage
    
    def delete_stage(self, stage_id: int):
        """Delete pipeline stage"""
        stage = self.get_stage(stage_id)
        
        if stage.is_system:
            raise HTTPException(status_code=400, detail="Cannot delete system stage")
        
        # Check if stage has opportunities
        opp_count = self.db.query(func.count(Opportunity.id)).filter(
            Opportunity.stage_id == stage_id
        ).scalar()
        
        if opp_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete stage with {opp_count} opportunities"
            )
        
        self.db.delete(stage)
        self.db.commit()
    
    def reorder_stages(self, stage_orders: List[Dict[str, int]]):
        """Reorder pipeline stages"""
        for item in stage_orders:
            stage = self.get_stage(item['stage_id'])
            stage.order_index = item['order_index']
        
        self.db.commit()
    
    # ==================== Opportunity Management ====================
    
    def create_opportunity(self, opp_data: OpportunityCreate) -> Opportunity:
        """Create new opportunity"""
        # Validate stage exists
        stage = self.get_stage(opp_data.stage_id)
        
        # Calculate weighted value
        probability = opp_data.probability if opp_data.probability is not None else stage.probability
        weighted_value = opp_data.estimated_value * (probability / 100)
        
        opportunity = Opportunity(
            **opp_data.dict(),
            probability=probability,
            weighted_value=weighted_value,
            stage_entered_at=datetime.utcnow()
        )
        
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        
        # Create initial stage history
        self._create_stage_history(opportunity.id, None, opp_data.stage_id, opp_data.owner_id)
        
        # Execute stage automation
        self._execute_stage_automation(opportunity)
        
        return opportunity
    
    def get_opportunities(
        self,
        stage_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        status: Optional[OpportunityStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Opportunity], int]:
        """Get opportunities with filters"""
        query = self.db.query(Opportunity)
        
        if stage_id:
            query = query.filter(Opportunity.stage_id == stage_id)
        if owner_id:
            query = query.filter(Opportunity.owner_id == owner_id)
        if status:
            query = query.filter(Opportunity.status == status)
        
        total = query.count()
        opportunities = query.order_by(Opportunity.created_at.desc()).offset(skip).limit(limit).all()
        
        return opportunities, total
    
    def get_opportunity(self, opportunity_id: int) -> Opportunity:
        """Get opportunity by ID"""
        opportunity = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return opportunity
    
    def update_opportunity(self, opportunity_id: int, opp_data: OpportunityUpdate) -> Opportunity:
        """Update opportunity"""
        opportunity = self.get_opportunity(opportunity_id)
        
        # Handle stage change separately
        if opp_data.stage_id and opp_data.stage_id != opportunity.stage_id:
            raise HTTPException(
                status_code=400,
                detail="Use change_stage endpoint to move opportunities"
            )
        
        for key, value in opp_data.dict(exclude_unset=True, exclude={'stage_id'}).items():
            setattr(opportunity, key, value)
        
        # Recalculate weighted value if needed
        if opp_data.estimated_value or opp_data.probability:
            probability = opportunity.probability or opportunity.stage.probability
            opportunity.weighted_value = opportunity.estimated_value * (probability / 100)
        
        opportunity.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity
    
    def change_stage(
        self,
        opportunity_id: int,
        stage_change: OpportunityStageChange,
        user_id: int
    ) -> Opportunity:
        """Move opportunity to different stage"""
        opportunity = self.get_opportunity(opportunity_id)
        old_stage_id = opportunity.stage_id
        new_stage = self.get_stage(stage_change.stage_id)
        
        # Calculate days in previous stage
        days_in_stage = (datetime.utcnow() - opportunity.stage_entered_at).days
        
        # Update opportunity
        opportunity.stage_id = stage_change.stage_id
        opportunity.stage_entered_at = datetime.utcnow()
        opportunity.probability = new_stage.probability
        opportunity.weighted_value = opportunity.estimated_value * (new_stage.probability / 100)
        opportunity.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Create stage history
        self._create_stage_history(
            opportunity_id,
            old_stage_id,
            stage_change.stage_id,
            user_id,
            days_in_stage,
            stage_change.reason
        )
        
        # Execute stage automation
        self._execute_stage_automation(opportunity)
        
        self.db.refresh(opportunity)
        return opportunity
    
    def win_opportunity(
        self,
        opportunity_id: int,
        win_data: OpportunityWin
    ) -> Opportunity:
        """Mark opportunity as won"""
        opportunity = self.get_opportunity(opportunity_id)
        
        opportunity.status = OpportunityStatus.WON
        opportunity.actual_value = win_data.actual_value
        opportunity.actual_close_date = win_data.actual_close_date or datetime.utcnow()
        opportunity.win_reason = win_data.win_reason
        opportunity.updated_at = datetime.utcnow()
        
        # Move to closed_won stage if not already there
        won_stage = self.db.query(PipelineStage).filter(
            PipelineStage.stage_type == PipelineStageType.CLOSED_WON
        ).first()
        
        if won_stage and opportunity.stage_id != won_stage.id:
            opportunity.stage_id = won_stage.id
            opportunity.stage_entered_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity
    
    def lose_opportunity(
        self,
        opportunity_id: int,
        loss_data: OpportunityLoss
    ) -> Opportunity:
        """Mark opportunity as lost"""
        opportunity = self.get_opportunity(opportunity_id)
        
        opportunity.status = OpportunityStatus.LOST
        opportunity.actual_close_date = loss_data.actual_close_date or datetime.utcnow()
        opportunity.loss_reason = loss_data.loss_reason
        opportunity.competitor = loss_data.competitor
        opportunity.updated_at = datetime.utcnow()
        
        # Move to closed_lost stage if not already there
        lost_stage = self.db.query(PipelineStage).filter(
            PipelineStage.stage_type == PipelineStageType.CLOSED_LOST
        ).first()
        
        if lost_stage and opportunity.stage_id != lost_stage.id:
            opportunity.stage_id = lost_stage.id
            opportunity.stage_entered_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity
    
    def delete_opportunity(self, opportunity_id: int):
        """Delete opportunity"""
        opportunity = self.get_opportunity(opportunity_id)
        self.db.delete(opportunity)
        self.db.commit()
    
    # ==================== Analytics ====================
    
    def get_pipeline_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PipelineAnalytics:
        """Get comprehensive pipeline analytics"""
        query = self.db.query(Opportunity).filter(Opportunity.status == OpportunityStatus.ACTIVE)
        
        if start_date:
            query = query.filter(Opportunity.created_at >= start_date)
        if end_date:
            query = query.filter(Opportunity.created_at <= end_date)
        
        opportunities = query.all()
        
        total_opportunities = len(opportunities)
        total_value = sum(opp.estimated_value for opp in opportunities)
        weighted_value = sum(opp.weighted_value for opp in opportunities)
        average_deal_size = total_value / total_opportunities if total_opportunities > 0 else 0
        
        # Win rate
        won_count = self.db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == OpportunityStatus.WON
        ).scalar()
        lost_count = self.db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == OpportunityStatus.LOST
        ).scalar()
        win_rate = (won_count / (won_count + lost_count) * 100) if (won_count + lost_count) > 0 else 0
        
        # Average sales cycle
        closed_opps = self.db.query(Opportunity).filter(
            Opportunity.status.in_([OpportunityStatus.WON, OpportunityStatus.LOST])
        ).all()
        
        if closed_opps:
            total_days = sum(
                (opp.actual_close_date - opp.created_at).days
                for opp in closed_opps
                if opp.actual_close_date
            )
            average_sales_cycle_days = total_days / len(closed_opps)
        else:
            average_sales_cycle_days = 0
        
        # By stage
        by_stage = self.db.query(
            PipelineStage.name,
            func.count(Opportunity.id).label('count'),
            func.sum(Opportunity.estimated_value).label('value')
        ).join(Opportunity).group_by(PipelineStage.id).all()
        
        # By owner
        by_owner = self.db.query(
            Opportunity.owner_id,
            func.count(Opportunity.id).label('count'),
            func.sum(Opportunity.estimated_value).label('value')
        ).group_by(Opportunity.owner_id).all()
        
        # By source
        by_source = self.db.query(
            Opportunity.source,
            func.count(Opportunity.id).label('count'),
            func.sum(Opportunity.estimated_value).label('value')
        ).group_by(Opportunity.source).all()
        
        return PipelineAnalytics(
            total_opportunities=total_opportunities,
            total_value=total_value,
            weighted_value=weighted_value,
            average_deal_size=average_deal_size,
            win_rate=win_rate,
            average_sales_cycle_days=average_sales_cycle_days,
            by_stage=[{'name': s[0], 'count': s[1], 'value': s[2] or 0} for s in by_stage],
            by_owner=[{'owner_id': o[0], 'count': o[1], 'value': o[2] or 0} for o in by_owner],
            by_source=[{'source': s[0] or 'Unknown', 'count': s[1], 'value': s[2] or 0} for s in by_source],
            trend_data=self._get_trend_data(start_date, end_date)
        )
    
    def get_win_loss_analysis(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> WinLossAnalysis:
        """Get win/loss analysis"""
        query = self.db.query(Opportunity).filter(
            Opportunity.status.in_([OpportunityStatus.WON, OpportunityStatus.LOST])
        )
        
        if start_date:
            query = query.filter(Opportunity.actual_close_date >= start_date)
        if end_date:
            query = query.filter(Opportunity.actual_close_date <= end_date)
        
        opportunities = query.all()
        
        won_opps = [opp for opp in opportunities if opp.status == OpportunityStatus.WON]
        lost_opps = [opp for opp in opportunities if opp.status == OpportunityStatus.LOST]
        
        total_won = len(won_opps)
        total_lost = len(lost_opps)
        win_rate = (total_won / (total_won + total_lost) * 100) if (total_won + total_lost) > 0 else 0
        
        total_won_value = sum(opp.actual_value or 0 for opp in won_opps)
        total_lost_value = sum(opp.estimated_value for opp in lost_opps)
        
        average_won_deal_size = total_won_value / total_won if total_won > 0 else 0
        average_lost_deal_size = total_lost_value / total_lost if total_lost > 0 else 0
        
        # Win reasons
        win_reasons = {}
        for opp in won_opps:
            if opp.win_reason:
                win_reasons[opp.win_reason] = win_reasons.get(opp.win_reason, 0) + 1
        
        # Loss reasons
        loss_reasons = {}
        for opp in lost_opps:
            if opp.loss_reason:
                loss_reasons[opp.loss_reason] = loss_reasons.get(opp.loss_reason, 0) + 1
        
        # Competitors
        competitors = {}
        for opp in lost_opps:
            if opp.competitor:
                competitors[opp.competitor] = competitors.get(opp.competitor, 0) + 1
        
        return WinLossAnalysis(
            total_won=total_won,
            total_lost=total_lost,
            win_rate=win_rate,
            total_won_value=total_won_value,
            total_lost_value=total_lost_value,
            average_won_deal_size=average_won_deal_size,
            average_lost_deal_size=average_lost_deal_size,
            win_reasons=[{'reason': k, 'count': v} for k, v in win_reasons.items()],
            loss_reasons=[{'reason': k, 'count': v} for k, v in loss_reasons.items()],
            competitors=[{'name': k, 'count': v} for k, v in competitors.items()],
            by_stage=[],
            by_source=[]
        )
    
    def generate_forecast(
        self,
        period_start: datetime,
        period_end: datetime,
        user_id: int
    ) -> PipelineForecastData:
        """Generate pipeline forecast"""
        # Get opportunities expected to close in period
        opportunities = self.db.query(Opportunity).filter(
            and_(
                Opportunity.status == OpportunityStatus.ACTIVE,
                Opportunity.expected_close_date >= period_start,
                Opportunity.expected_close_date <= period_end
            )
        ).all()
        
        total_opportunities = len(opportunities)
        total_value = sum(opp.estimated_value for opp in opportunities)
        weighted_value = sum(opp.weighted_value for opp in opportunities)
        
        # Expected wins based on probability
        expected_wins = sum(1 for opp in opportunities if opp.probability >= 70)
        expected_revenue = sum(
            opp.estimated_value for opp in opportunities if opp.probability >= 70
        )
        
        # Confidence level based on data quality
        confidence_level = self._calculate_forecast_confidence(opportunities)
        
        # Save forecast
        forecast = PipelineForecast(
            forecast_date=datetime.utcnow(),
            period_start=period_start,
            period_end=period_end,
            total_opportunities=total_opportunities,
            total_value=total_value,
            weighted_value=weighted_value,
            expected_wins=expected_wins,
            expected_revenue=expected_revenue,
            confidence_level=confidence_level,
            created_by=user_id
        )
        
        self.db.add(forecast)
        self.db.commit()
        
        return PipelineForecastData(
            period_start=period_start,
            period_end=period_end,
            total_opportunities=total_opportunities,
            total_value=total_value,
            weighted_value=weighted_value,
            expected_wins=expected_wins,
            expected_revenue=expected_revenue,
            confidence_level=confidence_level,
            by_stage=[],
            by_owner=[],
            by_month=[]
        )
    
    # ==================== Helper Methods ====================
    
    def _create_stage_history(
        self,
        opportunity_id: int,
        from_stage_id: Optional[int],
        to_stage_id: int,
        user_id: int,
        days_in_previous_stage: Optional[int] = None,
        reason: Optional[str] = None
    ):
        """Create stage history record"""
        history = OpportunityStageHistory(
            opportunity_id=opportunity_id,
            from_stage_id=from_stage_id,
            to_stage_id=to_stage_id,
            days_in_previous_stage=days_in_previous_stage,
            changed_by=user_id,
            reason=reason
        )
        self.db.add(history)
        self.db.commit()
    
    def _execute_stage_automation(self, opportunity: Opportunity):
        """Execute automation rules for stage"""
        stage = opportunity.stage
        if not stage.auto_actions:
            return
        
        # Execute configured actions
        for action in stage.auto_actions.get('actions', []):
            action_type = action.get('type')
            
            if action_type == 'send_email':
                # TODO: Implement email sending
                pass
            elif action_type == 'create_task':
                # TODO: Implement task creation
                pass
            elif action_type == 'update_field':
                # TODO: Implement field update
                pass
    
    def _get_trend_data(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Dict[str, List[float]]:
        """Get trend data for analytics"""
        # TODO: Implement trend calculation
        return {
            'opportunities': [],
            'value': [],
            'win_rate': []
        }
    
    def _calculate_forecast_confidence(self, opportunities: List[Opportunity]) -> float:
        """Calculate forecast confidence level"""
        if not opportunities:
            return 0.0
        
        # Factors affecting confidence:
        # - Number of opportunities
        # - Data completeness
        # - Historical accuracy
        
        confidence = 50.0  # Base confidence
        
        # More opportunities = higher confidence
        if len(opportunities) > 10:
            confidence += 20.0
        elif len(opportunities) > 5:
            confidence += 10.0
        
        # Data completeness
        complete_data = sum(
            1 for opp in opportunities
            if opp.expected_close_date and opp.probability
        )
        completeness_ratio = complete_data / len(opportunities)
        confidence += completeness_ratio * 30.0
        
        return min(confidence, 100.0)
