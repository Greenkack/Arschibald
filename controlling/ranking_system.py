"""
Controlling Ranking System

Dynamisches Ranking-System für Mitarbeiter-Leistungsbewertung mit
automatischer Aktualisierung und PDF-Export.
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from controlling.models import (
    Employee, PerformanceData, Position, EvaluationPeriod, PeriodStatus
)
from controlling.analytics import AnalyticsEngine

logger = logging.getLogger(__name__)


class RankingSystem:
    """
    Ranking-System für dynamische Mitarbeiter-Platzierungen.
    
    Features:
    - Automatische Ranking-Berechnung nach jeder Auswertung
    - Separate Rankings pro Zeitraum/Periode
    - Mehrere Ranking-Kriterien (Quotas)
    - PDF-Export mit Ranking-Tabellen
    """
    
    def __init__(self, db: Session):
        """
        Initialisiere Ranking System.
        
        Args:
            db: SQLAlchemy Session
        """
        self.db = db
        self.analytics_engine = AnalyticsEngine(db)
    
    def calculate_employee_rankings(
        self,
        position_id: int,
        start_date: date,
        end_date: date,
        period_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Berechne Rankings für alle Mitarbeiter einer Position.
        
        Args:
            position_id: Position ID
            start_date: Startdatum
            end_date: Enddatum
            period_id: Optional - Auswertungsperiode ID
            
        Returns:
            Dictionary mit Rankings pro Quota
        """
        # Hole Position
        position = self.db.query(Position).filter(
            Position.id == position_id
        ).first()
        
        if not position:
            raise ValueError(f"Position {position_id} nicht gefunden")
        
        # Hole aktive Mitarbeiter
        employees = self.db.query(Employee).filter(
            Employee.position_id == position_id,
            Employee.is_active == True
        ).all()
        
        if not employees:
            return {
                "position_name": position.name,
                "position_id": position_id,
                "employee_count": 0,
                "rankings": {},
                "message": "Keine Mitarbeiter gefunden"
            }
        
        # Sammle Quotas für jeden Mitarbeiter
        employee_quotas = []
        
        for employee in employees:
            # Filtere Performance-Daten
            query = self.db.query(PerformanceData).filter(
                PerformanceData.employee_id == employee.id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date
            )
            
            if period_id:
                query = query.filter(PerformanceData.period_id == period_id)
            
            perf_data = query.all()
            
            if not perf_data:
                continue
            
            # Berechne Quotas (positions-spezifisch)
            quotas = self.analytics_engine.calculate_quotas(
                perf_data,
                employee.position.name if employee.position else None
            )
            
            employee_quotas.append({
                "employee_id": employee.id,
                "name": employee.full_name,
                "agent_name": employee.agent_name,
                "quotas": quotas
            })
        
        # Erstelle Rankings pro Quota
        rankings = self._create_rankings_by_quota(employee_quotas)
        
        # Berechne Gesamt-Ranking (Durchschnitt aller Quotas)
        overall_ranking = self._calculate_overall_ranking(employee_quotas)
        
        return {
            "position_name": position.name,
            "position_id": position_id,
            "employee_count": len(employee_quotas),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "period_id": period_id,
            "generated_at": datetime.now().isoformat(),
            "quota_rankings": rankings,
            "overall_ranking": overall_ranking,
            "employees": employee_quotas
        }
    
    def _create_rankings_by_quota(
        self,
        employee_quotas: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Erstelle Rankings sortiert nach jeder Quota.
        
        Args:
            employee_quotas: Liste mit Mitarbeiter-Quotas
            
        Returns:
            Dictionary: quota_name -> sorted ranking list
        """
        rankings = {}
        
        if not employee_quotas:
            return rankings
        
        # Finde alle verfügbaren Quotas
        all_quotas = set()
        for emp in employee_quotas:
            all_quotas.update(emp["quotas"].keys())
        
        # Erstelle Ranking für jede Quota
        for quota_name in all_quotas:
            # Sammle Werte für diese Quota
            quota_values = []
            for emp in employee_quotas:
                if quota_name in emp["quotas"]:
                    quota_values.append({
                        "employee_id": emp["employee_id"],
                        "name": emp["name"],
                        "agent_name": emp["agent_name"],
                        "value": emp["quotas"][quota_name]
                    })
            
            # Sortiere absteigend (höchster Wert = Rang 1)
            quota_values.sort(key=lambda x: x["value"], reverse=True)
            
            # Vergebe Ränge
            ranked_list = []
            for rank, item in enumerate(quota_values, start=1):
                ranked_list.append({
                    "rank": rank,
                    "employee_id": item["employee_id"],
                    "name": item["name"],
                    "agent_name": item["agent_name"],
                    "value": item["value"],
                    "quota_name": quota_name
                })
            
            rankings[quota_name] = ranked_list
        
        return rankings
    
    def _calculate_overall_ranking(
        self,
        employee_quotas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Berechne Gesamt-Ranking basierend auf Durchschnitt aller Quotas.
        
        Args:
            employee_quotas: Liste mit Mitarbeiter-Quotas
            
        Returns:
            Sortierte Liste mit Gesamt-Rankings
        """
        overall_scores = []
        
        for emp in employee_quotas:
            quotas = emp["quotas"]
            if quotas:
                avg_score = sum(quotas.values()) / len(quotas)
            else:
                avg_score = 0.0
            
            overall_scores.append({
                "employee_id": emp["employee_id"],
                "name": emp["name"],
                "agent_name": emp["agent_name"],
                "average_score": avg_score,
                "quota_count": len(quotas)
            })
        
        # Sortiere nach Durchschnitt
        overall_scores.sort(key=lambda x: x["average_score"], reverse=True)
        
        # Vergebe Ränge
        for rank, item in enumerate(overall_scores, start=1):
            item["rank"] = rank
        
        return overall_scores
    
    def get_rankings_for_all_periods(
        self,
        position_id: int
    ) -> List[Dict[str, Any]]:
        """
        Hole Rankings für alle Auswertungsperioden einer Position.
        
        Args:
            position_id: Position ID
            
        Returns:
            Liste mit Rankings pro Periode
        """
        # Hole alle abgeschlossenen und aktiven Perioden (Positionsfilter folgt in Ranking)
        periods = self.db.query(EvaluationPeriod).filter(
            EvaluationPeriod.status.in_([
                PeriodStatus.ACTIVE,
                PeriodStatus.COMPLETED
            ])
        ).order_by(EvaluationPeriod.start_date.desc()).all()
        
        all_rankings = []
        
        for period in periods:
            try:
                ranking = self.calculate_employee_rankings(
                    position_id=position_id,
                    start_date=period.start_date,
                    end_date=period.end_date,
                    period_id=period.id
                )
                
                ranking["period_name"] = period.name
                ranking["period_type"] = period.period_type.value
                all_rankings.append(ranking)
                
            except Exception as e:
                logger.error(f"Fehler beim Ranking für Periode {period.id}: {e}")
                continue
        
        return all_rankings
    
    def get_employee_ranking_history(
        self,
        employee_id: int,
        quota_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Hole Ranking-Historie eines Mitarbeiters über alle Perioden.
        
        Args:
            employee_id: Mitarbeiter ID
            quota_name: Optional - Spezifische Quota, sonst Gesamt-Ranking
            
        Returns:
            Liste mit Ranking-Positionen pro Periode
        """
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()
        
        if not employee:
            raise ValueError(f"Mitarbeiter {employee_id} nicht gefunden")
        
        # Hole alle Rankings für die Position
        all_period_rankings = self.get_rankings_for_all_periods(
            employee.position_id
        )
        
        history = []
        
        for period_ranking in all_period_rankings:
            if quota_name:
                # Suche in quota_rankings
                quota_rankings = period_ranking.get("quota_rankings", {})
                if quota_name in quota_rankings:
                    for entry in quota_rankings[quota_name]:
                        if entry["employee_id"] == employee_id:
                            history.append({
                                "period_name": period_ranking["period_name"],
                                "period_type": period_ranking["period_type"],
                                "start_date": period_ranking["start_date"],
                                "end_date": period_ranking["end_date"],
                                "quota_name": quota_name,
                                "rank": entry["rank"],
                                "value": entry["value"],
                                "total_employees": period_ranking["employee_count"]
                            })
                            break
            else:
                # Suche in overall_ranking
                overall = period_ranking.get("overall_ranking", [])
                for entry in overall:
                    if entry["employee_id"] == employee_id:
                        history.append({
                            "period_name": period_ranking["period_name"],
                            "period_type": period_ranking["period_type"],
                            "start_date": period_ranking["start_date"],
                            "end_date": period_ranking["end_date"],
                            "quota_name": "Gesamt-Durchschnitt",
                            "rank": entry["rank"],
                            "value": entry["average_score"],
                            "total_employees": period_ranking["employee_count"]
                        })
                        break
        
        return history
