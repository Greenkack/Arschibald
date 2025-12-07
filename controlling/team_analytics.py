"""
Team-Auswertung und Mitarbeiter-Vergleich

Ermöglicht Auswertung mehrerer Mitarbeiter als Team und Vergleich von Mitarbeitern
derselben Position.
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from controlling.models import Employee, PerformanceData, Position
from controlling.analytics import AnalyticsEngine

logger = logging.getLogger(__name__)


class TeamAnalytics:
    """
    Team-Analysen für Controlling System.
    
    Unterstützt:
    - Team-Auswertung (alle Mitarbeiter einer Position)
    - Mitarbeiter-Vergleich (Vergleich von 2+ Mitarbeitern)
    """
    
    def __init__(self, db: Session):
        """
        Initialisiere Team Analytics.
        
        Args:
            db: SQLAlchemy Session
        """
        self.db = db
        self.analytics_engine = AnalyticsEngine(db)
    
    def generate_team_report(
        self,
        position_id: int,
        start_date: date,
        end_date: date,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """
        Erstelle Team-Auswertung für alle Mitarbeiter einer Position.
        
        Args:
            position_id: ID der Position
            start_date: Startdatum
            end_date: Enddatum
            include_inactive: Inaktive Mitarbeiter einbeziehen
            
        Returns:
            Team-Auswertungsdaten
        """
        # Hole Position
        position = self.db.query(Position).filter(
            Position.id == position_id
        ).first()
        
        if not position:
            raise ValueError(f"Position mit ID {position_id} nicht gefunden")
        
        # Hole Mitarbeiter
        query = self.db.query(Employee).filter(
            Employee.position_id == position_id
        )
        
        if not include_inactive:
            query = query.filter(Employee.is_active == True)
        
        employees = query.all()
        
        if not employees:
            return {
                "position_name": position.name,
                "position_id": position_id,
                "employee_count": 0,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "generated_at": datetime.now().isoformat(),
                "message": "Keine Mitarbeiter für diese Position gefunden"
            }
        
        # Sammle Daten für jeden Mitarbeiter
        employee_data = []
        team_aggregates = {}
        
        for employee in employees:
            # Hole Performance-Daten
            perf_data = self.db.query(PerformanceData).filter(
                PerformanceData.employee_id == employee.id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date
            ).all()
            
            if not perf_data:
                continue
            
            # Berechne Quotas für Mitarbeiter
            quotas = self.analytics_engine.calculate_quotas(perf_data)
            
            # Aggregiere Rohdaten
            aggregated = self.analytics_engine.aggregate_performance_data(perf_data)
            
            employee_info = {
                "id": employee.id,
                "name": employee.full_name,
                "agent_name": employee.agent_name,
                "is_active": employee.is_active,
                "start_date": employee.start_date.isoformat(),
                "quotas": quotas,
                "raw_data": aggregated.get("raw_data", {})
            }
            
            employee_data.append(employee_info)
            
            # Aggregiere für Team
            for key, value in aggregated.get("raw_data", {}).items():
                if key not in team_aggregates:
                    team_aggregates[key] = 0.0
                team_aggregates[key] += value
        
        # Berechne Team-Durchschnitts-Quotas
        team_quotas = self._calculate_team_quotas(team_aggregates)
        
        # Berechne Statistiken
        statistics = self._calculate_team_statistics(employee_data)
        
        return {
            "report_type": "team",
            "position_name": position.name,
            "position_id": position_id,
            "employee_count": len(employee_data),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.now().isoformat(),
            
            # Team-Daten
            "team_quotas": team_quotas,
            "team_aggregates": team_aggregates,
            
            # Einzelne Mitarbeiter
            "employees": employee_data,
            
            # Statistiken
            "statistics": statistics
        }
    
    def generate_comparison_report(
        self,
        employee_ids: List[int],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Erstelle Vergleichsbericht für mehrere Mitarbeiter.
        
        Args:
            employee_ids: Liste von Mitarbeiter-IDs
            start_date: Startdatum
            end_date: Enddatum
            
        Returns:
            Vergleichsdaten
        """
        if len(employee_ids) < 2:
            raise ValueError("Mindestens 2 Mitarbeiter für Vergleich erforderlich")
        
        # Hole Mitarbeiter
        employees = self.db.query(Employee).filter(
            Employee.id.in_(employee_ids)
        ).all()
        
        if len(employees) != len(employee_ids):
            missing = set(employee_ids) - {e.id for e in employees}
            raise ValueError(f"Mitarbeiter nicht gefunden: {missing}")
        
        # Prüfe ob gleiche Position
        positions = {e.position_id for e in employees}
        same_position = len(positions) == 1
        
        if same_position:
            position_name = employees[0].position.name
        else:
            position_name = "Verschiedene Positionen"
        
        # Sammle Daten für jeden Mitarbeiter
        employee_data = []
        
        for employee in employees:
            # Hole Performance-Daten
            perf_data = self.db.query(PerformanceData).filter(
                PerformanceData.employee_id == employee.id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date
            ).all()
            
            # Berechne Quotas
            quotas = self.analytics_engine.calculate_quotas(perf_data)
            
            # Aggregiere Rohdaten
            aggregated = self.analytics_engine.aggregate_performance_data(perf_data)
            
            employee_info = {
                "id": employee.id,
                "name": employee.full_name,
                "agent_name": employee.agent_name,
                "position": employee.position.name,
                "position_id": employee.position_id,
                "is_active": employee.is_active,
                "quotas": quotas,
                "raw_data": aggregated.get("raw_data", {})
            }
            
            employee_data.append(employee_info)
        
        # Berechne Vergleichs-Statistiken
        comparison_stats = self._calculate_comparison_statistics(employee_data)
        
        return {
            "report_type": "comparison",
            "position_name": position_name,
            "same_position": same_position,
            "employee_count": len(employee_data),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.now().isoformat(),
            
            # Mitarbeiter-Daten
            "employees": employee_data,
            
            # Vergleichs-Statistiken
            "comparison_statistics": comparison_stats
        }
    
    def _calculate_team_quotas(self, team_aggregates: Dict[str, float]) -> Dict[str, float]:
        """
        Berechne Team-Quotas aus aggregierten Daten.
        
        Args:
            team_aggregates: Aggregierte Team-Daten
            
        Returns:
            Dictionary mit Team-Quotas
        """
        verkauf = team_aggregates.get("Verkauf", 0)
        angefahrene_termine_gesamt = team_aggregates.get("Angefahrene Termine gesamt", 0)
        kunden_terminiert = team_aggregates.get("Kunden terminiert", 0)
        anrufe_gesamt = team_aggregates.get("Getätigte Anrufe gesamt", 0)
        angefahrene_termine = team_aggregates.get("Angefahrene Termine", 0)
        qc_bestanden = team_aggregates.get("QC bestanden", 0)
        
        quotas = {}
        
        # Abschlussquote
        if angefahrene_termine_gesamt > 0:
            quotas["Abschlussquote"] = (verkauf / angefahrene_termine_gesamt) * 100
        else:
            quotas["Abschlussquote"] = 0.0
        
        # Terminvereinbarungsquote
        if anrufe_gesamt > 0:
            quotas["Terminvereinbarungsquote"] = (kunden_terminiert / anrufe_gesamt) * 100
        else:
            quotas["Terminvereinbarungsquote"] = 0.0
        
        # Termine-Anfahrquote
        if kunden_terminiert > 0:
            quotas["Termine-Anfahrquote"] = (angefahrene_termine / kunden_terminiert) * 100
        else:
            quotas["Termine-Anfahrquote"] = 0.0
        
        # QC Quote
        if verkauf > 0:
            quotas["QC bestanden Quote"] = (qc_bestanden / verkauf) * 100
        else:
            quotas["QC bestanden Quote"] = 0.0
        
        return quotas
    
    def _calculate_team_statistics(self, employee_data: List[Dict]) -> Dict[str, Any]:
        """
        Berechne Team-Statistiken.
        
        Args:
            employee_data: Liste mit Mitarbeiter-Daten
            
        Returns:
            Statistiken
        """
        if not employee_data:
            return {}
        
        stats = {
            "quota_statistics": {},
            "top_performers": {},
            "bottom_performers": {},
            "averages": {}
        }
        
        # Berechne Durchschnitte und Extremwerte für jede Quote
        quota_names = employee_data[0]["quotas"].keys()
        
        for quota_name in quota_names:
            values = [emp["quotas"].get(quota_name, 0) for emp in employee_data]
            
            if not values:
                continue
            
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            
            # Finde beste und schlechteste Performer
            best_emp = max(employee_data, key=lambda x: x["quotas"].get(quota_name, 0))
            worst_emp = min(employee_data, key=lambda x: x["quotas"].get(quota_name, 0))
            
            stats["quota_statistics"][quota_name] = {
                "average": avg,
                "min": min_val,
                "max": max_val,
                "best_performer": best_emp["name"],
                "worst_performer": worst_emp["name"]
            }
        
        return stats
    
    def _calculate_comparison_statistics(self, employee_data: List[Dict]) -> Dict[str, Any]:
        """
        Berechne Vergleichs-Statistiken.
        
        Args:
            employee_data: Liste mit Mitarbeiter-Daten
            
        Returns:
            Vergleichs-Statistiken
        """
        if not employee_data:
            return {}
        
        stats = {
            "rankings": {},
            "differences": {},
            "summary": {}
        }
        
        # Rankings für jede Quote
        quota_names = employee_data[0]["quotas"].keys()
        
        for quota_name in quota_names:
            # Sortiere Mitarbeiter nach Quote (absteigend)
            sorted_employees = sorted(
                employee_data,
                key=lambda x: x["quotas"].get(quota_name, 0),
                reverse=True
            )
            
            rankings = []
            for rank, emp in enumerate(sorted_employees, 1):
                rankings.append({
                    "rank": rank,
                    "name": emp["name"],
                    "value": emp["quotas"].get(quota_name, 0)
                })
            
            stats["rankings"][quota_name] = rankings
            
            # Berechne Unterschiede zwischen erstem und letztem
            if len(rankings) >= 2:
                first = rankings[0]["value"]
                last = rankings[-1]["value"]
                difference = first - last
                
                stats["differences"][quota_name] = {
                    "leader": rankings[0]["name"],
                    "leader_value": first,
                    "last": rankings[-1]["name"],
                    "last_value": last,
                    "difference": difference,
                    "difference_percent": (difference / last * 100) if last > 0 else 0
                }
        
        return stats
