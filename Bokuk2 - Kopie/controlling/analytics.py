"""
Controlling System Analytics Engine

Provides analytics and quota calculation functionality for the Employee
Controlling System.

Requirements: 9.2, 9.3, 9.5, 10.1, 10.2, 10.3, 11.1, 11.2, 11.4
"""

import sys
import logging
from pathlib import Path
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from controlling.models import (  # noqa: E402
    Employee,
    PerformanceData,
    ReportType
)

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Analytics engine for calculating quotas and aggregating performance data.

    Requirements: 9.2, 9.3, 9.5, 10.1, 10.2, 10.3, 11.1, 11.2, 11.4
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_abschlussquote(
        self,
        verkauf: float,
        kunden_terminiert: float
    ) -> float:
        """
        Calculate Abschlussquote (closing rate).

        Formula: (Verkauf / Kunden terminiert) × 100

        Args:
            verkauf: Number of sales
            kunden_terminiert: Number of customers scheduled

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if kunden_terminiert == 0:
            return 0.0
        return (verkauf / kunden_terminiert) * 100

    def calculate_terminvereinbarungsquote(
        self,
        kunden_terminiert: float,
        getaetigte_anrufe_gesamt: float
    ) -> float:
        """
        Calculate Terminvereinbarungsquote (appointment scheduling rate).

        Formula: (Kunden terminiert / Getätigte Anrufe gesamt) × 100

        Args:
            kunden_terminiert: Number of customers scheduled
            getaetigte_anrufe_gesamt: Total calls made

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if getaetigte_anrufe_gesamt == 0:
            return 0.0
        return (kunden_terminiert / getaetigte_anrufe_gesamt) * 100

    def calculate_anfahrquote(
        self,
        angefahrene_termine: float,
        kunden_terminiert: float
    ) -> float:
        """
        Calculate Termine-Anfahrquote (appointment attendance rate).

        Formula: (Angefahrene Termine / Kunden terminiert) × 100

        Args:
            angefahrene_termine: Number of appointments attended
            kunden_terminiert: Number of customers scheduled

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if kunden_terminiert == 0:
            return 0.0
        return (angefahrene_termine / kunden_terminiert) * 100

    def calculate_nicht_interessiert_quote(
        self,
        storniert_kein_interesse: float,
        kunden_terminiert: float
    ) -> float:
        """
        Calculate nicht interessierte Kunden Quote (not interested rate).

        Formula: (Storniert/kein Interesse / Kunden terminiert) × 100

        Args:
            storniert_kein_interesse: Number of cancelled/not interested
            kunden_terminiert: Number of customers scheduled

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if kunden_terminiert == 0:
            return 0.0
        return (storniert_kein_interesse / kunden_terminiert) * 100

    def calculate_technisch_nicht_machbar_quote(
        self,
        technisch_nicht_machbar: float,
        kunden_terminiert: float
    ) -> float:
        """
        Calculate technisch nicht machbar Quote (technically unfeasible rate).

        Formula: (Technisch nicht machbar / Kunden terminiert) × 100

        Args:
            technisch_nicht_machbar: Number of technically unfeasible projects
            kunden_terminiert: Number of customers scheduled

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if kunden_terminiert == 0:
            return 0.0
        return (technisch_nicht_machbar / kunden_terminiert) * 100

    def calculate_nicht_erreicht_quote(
        self,
        nicht_erreicht: float,
        getaetigte_anrufe_gesamt: float
    ) -> float:
        """
        Calculate Quote der nicht erreichten Kunden (not reached rate).

        Formula: (Nicht erreicht / Getätigte Anrufe gesamt) × 100

        Args:
            nicht_erreicht: Number of customers not reached
            getaetigte_anrufe_gesamt: Total calls made

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if getaetigte_anrufe_gesamt == 0:
            return 0.0
        return (nicht_erreicht / getaetigte_anrufe_gesamt) * 100

    def calculate_folgetermin_quote(
        self,
        folgetermin_gemacht: float,
        kunden_terminiert: float
    ) -> float:
        """
        Calculate Quote für Folgetermine-Vereinbarungen (follow-up rate).

        Formula: (Folgetermin gemacht / Kunden terminiert) × 100

        Args:
            folgetermin_gemacht: Number of follow-up appointments scheduled
            kunden_terminiert: Number of customers scheduled

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if kunden_terminiert == 0:
            return 0.0
        return (folgetermin_gemacht / kunden_terminiert) * 100

    def calculate_angebot_quote(
        self,
        angebot_erhalten: float,
        kunden_terminiert: float
    ) -> float:
        """
        Calculate Quote für Angebote (quote rate).

        Formula: (Angebot erhalten / Kunden terminiert) × 100

        Args:
            angebot_erhalten: Number of quotes provided
            kunden_terminiert: Number of customers scheduled

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if kunden_terminiert == 0:
            return 0.0
        return (angebot_erhalten / kunden_terminiert) * 100

    def calculate_zu_teuer_quote(
        self,
        zu_teuer: float,
        kunden_terminiert: float
    ) -> float:
        """
        Calculate Quote für zu teuer (too expensive rate).

        Formula: (Zu teuer / Kunden terminiert) × 100

        Args:
            zu_teuer: Number of customers who found pricing too high
            kunden_terminiert: Number of customers scheduled

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if kunden_terminiert == 0:
            return 0.0
        return (zu_teuer / kunden_terminiert) * 100

    def calculate_qc_bestanden_quote(
        self,
        qc_bestanden: float,
        verkauf: float
    ) -> float:
        """
        Calculate Quote für QC bestanden (QC passed rate).

        Formula: (QC bestanden / Verkauf) × 100

        Args:
            qc_bestanden: Number of QC checks passed
            verkauf: Number of sales

        Returns:
            Percentage as float

        Requirements: 10.1, 10.2
        """
        if verkauf == 0:
            return 0.0
        return (qc_bestanden / verkauf) * 100

    def calculate_ratio_description(
        self,
        quota_percentage: float,
        criterion_name: str
    ) -> str:
        """
        Generate a descriptive ratio for a quota.

        Formula: "Jeder X. [context] ist [outcome]" where X = 100 / quota

        Args:
            quota_percentage: The quota as a percentage
            criterion_name: Name of the criterion for context

        Returns:
            German description string

        Requirements: 11.1, 11.2, 11.3
        """
        if quota_percentage == 0:
            return "keine Daten"

        # Handle extreme percentages
        if quota_percentage > 100:
            # If quota > 100%, show multiplicative relationship instead
            multiplier = round(quota_percentage / 100, 2)
            context_map = {
                "Abschlussquote": "angefahrenen Termin",
                "Terminvereinbarungsquote": "Anruf",
                "Termine-Anfahrquote": "terminierten Kunden",
                "nicht interessierte Kunden Quote": "angefahrenen Termin",
                "technisch nicht machbar Quote": "angefahrenen Termin",
                "Quote der nicht erreichten Kunden": "Anruf",
                "Quote für Folgetermine-Vereinbarungen": "angefahrenen Termin",
                "Quote für Angebote": "angefahrenen Termin",
                "Quote für zu teuer": "angefahrenen Termin",
                "Quote für QC bestanden": "Verkauf"
            }
            context = context_map.get(criterion_name, "Element")
            return f"⚠️ {multiplier}× pro {context} (Daten prüfen!)"
        
        # Normal case: quota <= 100%
        ratio = round(100 / quota_percentage)
        
        # Prevent ratio = 0 (happens when quota is very high)
        if ratio < 1:
            ratio = 1

        # Map criterion names to descriptions
        descriptions = {
            "Abschlussquote": (
                f"Jeder {ratio}. angefahrene Termin ist ein Verkauf"
            ),
            "Terminvereinbarungsquote": (
                f"Jeder {ratio}. Anruf führt zu einem Termin"
            ),
            "Termine-Anfahrquote": (
                f"Jeder {ratio}. terminierte Kunde wird angefahren"
            ),
            "nicht interessierte Kunden Quote": (
                f"Jeder {ratio}. angefahrene Termin ist nicht interessiert"
            ),
            "technisch nicht machbar Quote": (
                f"Jeder {ratio}. angefahrene Termin ist technisch nicht "
                f"machbar"
            ),
            "Quote der nicht erreichten Kunden": (
                f"Jeder {ratio}. Anruf erreicht den Kunden nicht"
            ),
            "Quote für Folgetermine-Vereinbarungen": (
                f"Jeder {ratio}. angefahrene Termin führt zu einem "
                f"Folgetermin"
            ),
            "Quote für Angebote": (
                f"Jeder {ratio}. angefahrene Termin erhält ein Angebot"
            ),
            "Quote für zu teuer": (
                f"Jeder {ratio}. angefahrene Termin ist zu teuer"
            ),
            "Quote für QC bestanden": (
                f"Jeder {ratio}. Verkauf besteht die Qualitätskontrolle"
            )
        }

        return descriptions.get(
            criterion_name,
            f"1 zu {ratio}"
        )

    def _get_criterion_value(
        self,
        performance_data: List[PerformanceData],
        criterion_name: str
    ) -> float:
        """
        Get the sum of values for a specific criterion from performance data.

        Args:
            performance_data: List of performance data records
            criterion_name: Name of the criterion to sum

        Returns:
            Sum of values for the criterion
        """
        total = 0.0
        for record in performance_data:
            if record.criterion.name == criterion_name:
                total += record.value
        return total

    def calculate_quotas(
        self,
        performance_data: List[PerformanceData]
    ) -> Dict[str, float]:
        """
        Calculate all quotas from performance data.

        Args:
            performance_data: List of performance data records

        Returns:
            Dictionary mapping quota names to percentages

        Requirements: 10.1, 10.2
        """
        # Extract values for each criterion
        verkauf = self._get_criterion_value(performance_data, "Verkauf")
        kunden_terminiert = self._get_criterion_value(
            performance_data,
            "Kunden terminiert"
        )
        angefahrene_termine = self._get_criterion_value(
            performance_data,
            "Angefahrene Termine"
        )
        angefahrene_termine_gesamt = self._get_criterion_value(
            performance_data,
            "Angefahrene Termine gesamt"
        )
        getaetigte_anrufe_gesamt = self._get_criterion_value(
            performance_data,
            "Getätigte Anrufe gesamt"
        )
        storniert_kein_interesse = self._get_criterion_value(
            performance_data,
            "Storniert / kein Interesse"
        )
        technisch_nicht_machbar = self._get_criterion_value(
            performance_data,
            "Technisch nicht machbar"
        )
        nicht_erreicht = self._get_criterion_value(
            performance_data,
            "Nicht erreicht / neu terminieren"
        )
        folgetermin_gemacht = self._get_criterion_value(
            performance_data,
            "Folgetermin gemacht"
        )
        angebot_erhalten = self._get_criterion_value(
            performance_data,
            "Angebot erhalten"
        )
        zu_teuer = self._get_criterion_value(
            performance_data,
            "Zu teuer gewesen"
        )
        qc_bestanden = self._get_criterion_value(
            performance_data,
            "QC bestanden"
        )

        # Data validation: Log warnings for suspicious values
        validation_warnings = []
        
        # Check for decimal values where integers are expected
        criteria_that_should_be_integers = [
            ("Verkauf", verkauf),
            ("Kunden terminiert", kunden_terminiert),
            ("Angefahrene Termine", angefahrene_termine),
            ("Angefahrene Termine gesamt", angefahrene_termine_gesamt),
            ("Getätigte Anrufe gesamt", getaetigte_anrufe_gesamt),
            ("QC bestanden", qc_bestanden)
        ]
        
        for name, value in criteria_that_should_be_integers:
            if value != 0 and value != int(value):
                validation_warnings.append(
                    f"⚠️ {name}: {value} (erwartet ganze Zahl, nicht Dezimalzahl)"
                )
        
        # Check for logical inconsistencies
        if qc_bestanden > verkauf and verkauf > 0:
            validation_warnings.append(
                f"⚠️ QC bestanden ({qc_bestanden}) > Verkauf ({verkauf}) - "
                f"logisch unmöglich!"
            )
        
        if kunden_terminiert > getaetigte_anrufe_gesamt and getaetigte_anrufe_gesamt > 0:
            validation_warnings.append(
                f"⚠️ Terminierte Kunden ({kunden_terminiert}) > "
                f"Anrufe ({getaetigte_anrufe_gesamt}) - prüfen!"
            )
        
        # Log warnings
        if validation_warnings:
            logger.warning(
                "Data validation issues detected:\n" + "\n".join(validation_warnings)
            )

        # Calculate all quotas
        quotas = {
            "Abschlussquote": self.calculate_abschlussquote(
                verkauf,
                kunden_terminiert
            ),
            "Terminvereinbarungsquote": (
                self.calculate_terminvereinbarungsquote(
                    kunden_terminiert,
                    getaetigte_anrufe_gesamt
                )
            ),
            "Termine-Anfahrquote": self.calculate_anfahrquote(
                angefahrene_termine,
                kunden_terminiert
            ),
            "nicht interessierte Kunden Quote": (
                self.calculate_nicht_interessiert_quote(
                    storniert_kein_interesse,
                    kunden_terminiert
                )
            ),
            "technisch nicht machbar Quote": (
                self.calculate_technisch_nicht_machbar_quote(
                    technisch_nicht_machbar,
                    kunden_terminiert
                )
            ),
            "Quote der nicht erreichten Kunden": (
                self.calculate_nicht_erreicht_quote(
                    nicht_erreicht,
                    getaetigte_anrufe_gesamt
                )
            ),
            "Quote für Folgetermine-Vereinbarungen": (
                self.calculate_folgetermin_quote(
                    folgetermin_gemacht,
                    kunden_terminiert
                )
            ),
            "Quote für Angebote": self.calculate_angebot_quote(
                angebot_erhalten,
                kunden_terminiert
            ),
            "Quote für zu teuer": self.calculate_zu_teuer_quote(
                zu_teuer,
                kunden_terminiert
            ),
            "Quote für QC bestanden": self.calculate_qc_bestanden_quote(
                qc_bestanden,
                verkauf
            )
        }

        return quotas

    def aggregate_performance_data(
        self,
        performance_data: List[PerformanceData]
    ) -> Dict[str, Any]:
        """
        Aggregate performance data records into structured output.
        
        Args:
            performance_data: List of PerformanceData objects
            
        Returns:
            Dictionary with quotas and aggregated raw data
        """
        # Calculate quotas from performance data
        quotas = self.calculate_quotas(performance_data)
        
        # Aggregate raw data by criterion
        raw_data = defaultdict(float)
        for record in performance_data:
            raw_data[record.criterion.name] += record.value
        
        return {
            "quotas": quotas,
            "raw_data": dict(raw_data),
            "record_count": len(performance_data)
        }
    
    def aggregate_data(
        self,
        employee_id: int,
        period_type: ReportType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Aggregate performance data for a specific time period.

        Args:
            employee_id: ID of the employee
            period_type: Type of report period
            start_date: Start date (optional, calculated if not provided)
            end_date: End date (optional, defaults to today)

        Returns:
            Dictionary with aggregated data and quotas

        Requirements: 9.2, 9.3, 9.5
        """
        # Get employee
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")

        # Calculate date range if not provided
        if end_date is None:
            end_date = date.today()

        if start_date is None:
            start_date = self._calculate_start_date(
                period_type,
                end_date,
                employee.start_date
            )

        # Retrieve performance data for the period
        performance_data = self.db.query(PerformanceData).filter(
            PerformanceData.employee_id == employee_id,
            PerformanceData.date >= start_date,
            PerformanceData.date <= end_date
        ).all()

        # Calculate quotas
        quotas = self.calculate_quotas(performance_data)

        # Generate ratio descriptions
        ratios = {
            name: self.calculate_ratio_description(percentage, name)
            for name, percentage in quotas.items()
        }

        # Aggregate raw data by criterion
        raw_data = defaultdict(float)
        for record in performance_data:
            raw_data[record.criterion.name] += record.value

        return {
            "employee_id": employee_id,
            "employee_name": employee.full_name,
            "period_type": period_type.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "quotas": quotas,
            "ratios": ratios,
            "raw_data": dict(raw_data),
            "performance_records_count": len(performance_data)
        }

    def _calculate_start_date(
        self,
        period_type: ReportType,
        end_date: date,
        employee_start_date: date
    ) -> date:
        """
        Calculate the start date for a report period.

        Args:
            period_type: Type of report period
            end_date: End date of the period
            employee_start_date: Employee's start date

        Returns:
            Calculated start date
        """
        if period_type == ReportType.DAILY:
            return end_date

        elif period_type == ReportType.WEEKLY:
            # Start of week (Monday)
            days_since_monday = end_date.weekday()
            return end_date - timedelta(days=days_since_monday)

        elif period_type == ReportType.MONTHLY:
            # First day of month
            return end_date.replace(day=1)

        elif period_type == ReportType.QUARTERLY:
            # First day of quarter
            quarter_month = ((end_date.month - 1) // 3) * 3 + 1
            return end_date.replace(month=quarter_month, day=1)

        elif period_type == ReportType.YEARLY:
            # First day of year
            return end_date.replace(month=1, day=1)

        elif period_type == ReportType.SINCE_START:
            # Employee's start date
            return employee_start_date

        else:
            raise ValueError(f"Unknown period type: {period_type}")

    def calculate_comparison(
        self,
        employee_ids: List[int],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calculate comparison data for multiple employees.

        Args:
            employee_ids: List of employee IDs to compare
            start_date: Start date of comparison period
            end_date: End date of comparison period

        Returns:
            Dictionary with comparison data for all employees

        Requirements: 11.4, 20.1, 20.2
        """
        if len(employee_ids) > 10:
            raise ValueError(
                "Comparison supports maximum 10 employees at once"
            )

        comparison_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "employees": []
        }

        for employee_id in employee_ids:
            # Get employee
            employee = self.db.query(Employee).filter(
                Employee.id == employee_id
            ).first()
            if not employee:
                logger.warning(
                    f"Employee with ID {employee_id} not found, skipping"
                )
                continue

            # Retrieve performance data
            performance_data = self.db.query(PerformanceData).filter(
                PerformanceData.employee_id == employee_id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date
            ).all()

            # Calculate quotas
            quotas = self.calculate_quotas(performance_data)

            # Aggregate raw data
            raw_data = defaultdict(float)
            for record in performance_data:
                raw_data[record.criterion.name] += record.value

            comparison_data["employees"].append({
                "employee_id": employee_id,
                "employee_name": employee.full_name,
                "position": employee.position.name,
                "quotas": quotas,
                "raw_data": dict(raw_data)
            })

        return comparison_data
