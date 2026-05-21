"""
Controlling System Database Models

SQLAlchemy models for the Employee Controlling System.
Provides models for employees, positions, criteria, performance data, and reports.

Requirements: 2.1, 2.2, 2.3, 4.1, 5.1, 5.2, 6.2, 8.3, 13.2
"""

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime,
    Float, Boolean, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date
import enum

from backend.core.database import Base


# Enums for type safety - all inherit from str for pickle serialization (Streamlit session state)
class CalculationMethod(str, enum.Enum):
    """Calculation methods for criteria"""
    SUM = "SUM"
    AVERAGE = "AVERAGE"
    PERCENTAGE = "PERCENTAGE"
    RATIO = "RATIO"


class ReportType(str, enum.Enum):
    """Types of reports - inherits from str to be pickle-serializable for Streamlit session state"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    SINCE_START = "SINCE_START"


class PeriodType(str, enum.Enum):
    """Types of evaluation periods - inherits from str to be pickle-serializable for Streamlit session state"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


class PeriodStatus(str, enum.Enum):
    """Status of evaluation periods"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class Team(Base):
    """
    Team model for grouping employees into organizational units.
    
    Requirements: Team-based performance evaluation and reporting
    """
    __tablename__ = "controlling_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    team_leader_id = Column(
        Integer,
        ForeignKey("controlling_employees.id"),
        nullable=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    employees = relationship("Employee", back_populates="team", foreign_keys="Employee.team_id")
    team_leader = relationship("Employee", foreign_keys=[team_leader_id], post_update=True)
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"


class Employee(Base):
    """
    Employee model for storing employee information.
    
    Requirements: 2.1, 2.2, 2.3, 2.5
    """
    __tablename__ = "controlling_employees"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    agent_name = Column(String(100), nullable=True)  # Agentname für PDF-Generierung
    city = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    position_id = Column(
        Integer,
        ForeignKey("controlling_positions.id"),
        nullable=False
    )
    team_id = Column(
        Integer,
        ForeignKey("controlling_teams.id"),
        nullable=True,  # Optional, da nicht alle Mitarbeiter einem Team zugeordnet sein müssen
        index=True
    )
    start_date = Column(Date, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    position = relationship("Position", back_populates="employees")
    team = relationship("Team", back_populates="employees", foreign_keys=[team_id])
    performance_data = relationship(
        "PerformanceData",
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    reports = relationship("Report", back_populates="employee")
    
    @property
    def full_name(self) -> str:
        """Get full name of employee."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self) -> str:
        """Get display name with agent name if available."""
        if self.agent_name:
            return f"{self.agent_name} / {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """
        Calculate current age of employee.
        
        Requirements: 2.2
        """
        today = date.today()
        age = today.year - self.birth_date.year
        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (
            self.birth_date.month,
            self.birth_date.day
        ):
            age -= 1
        return age
    
    @property
    def days_employed(self) -> int:
        """
        Calculate number of days employed.
        
        Requirements: 2.3
        """
        today = date.today()
        delta = today - self.start_date
        return delta.days
    
    def __repr__(self):
        return (
            f"<Employee(id={self.id}, name='{self.full_name}', "
            f"position_id={self.position_id})>"
        )


class Position(Base):
    """
    Position model for storing job positions.
    
    Requirements: 4.1, 4.2
    """
    __tablename__ = "controlling_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    employees = relationship("Employee", back_populates="position")
    position_criteria = relationship(
        "PositionCriterion",
        back_populates="position",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Position(id={self.id}, name='{self.name}')>"


class Criterion(Base):
    """
    Criterion model for storing evaluation criteria.
    
    Requirements: 5.1, 5.2, 5.3, 19.1, 19.3
    """
    __tablename__ = "controlling_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    calculation_method = Column(
        SQLEnum(CalculationMethod),
        default=CalculationMethod.SUM,
        nullable=False
    )
    is_standard = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    position_criteria = relationship(
        "PositionCriterion",
        back_populates="criterion",
        cascade="all, delete-orphan"
    )
    performance_data = relationship(
        "PerformanceData",
        back_populates="criterion"
    )
    
    def __repr__(self):
        return (
            f"<Criterion(id={self.id}, name='{self.name}', "
            f"method={self.calculation_method.value})>"
        )


class PositionCriterion(Base):
    """
    Many-to-many relationship between positions and criteria.
    
    Requirements: 6.2, 6.3
    """
    __tablename__ = "controlling_position_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(
        Integer,
        ForeignKey("controlling_positions.id"),
        nullable=False
    )
    criterion_id = Column(
        Integer,
        ForeignKey("controlling_criteria.id"),
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    position = relationship("Position", back_populates="position_criteria")
    criterion = relationship("Criterion", back_populates="position_criteria")
    
    def __repr__(self):
        return (
            f"<PositionCriterion(position_id={self.position_id}, "
            f"criterion_id={self.criterion_id})>"
        )


class PerformanceData(Base):
    """
    Performance data model for storing employee performance metrics.
    
    Requirements: 8.3, 8.5
    """
    __tablename__ = "controlling_performance_data"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer,
        ForeignKey("controlling_employees.id"),
        nullable=False,
        index=True
    )
    criterion_id = Column(
        Integer,
        ForeignKey("controlling_criteria.id"),
        nullable=False,
        index=True
    )
    period_id = Column(
        Integer,
        ForeignKey("controlling_evaluation_periods.id"),
        nullable=True,  # Nullable für Rückwärtskompatibilität
        index=True
    )
    value = Column(Float, nullable=False)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="performance_data")
    criterion = relationship("Criterion", back_populates="performance_data")
    period = relationship("EvaluationPeriod", back_populates="performance_data")
    
    def __repr__(self):
        return (
            f"<PerformanceData(employee_id={self.employee_id}, "
            f"criterion_id={self.criterion_id}, value={self.value}, "
            f"date={self.date})>"
        )


class Report(Base):
    """
    Report model for storing generated reports.
    
    Requirements: 13.2, 13.3, 15.1
    """
    __tablename__ = "controlling_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    # Nullable for multi-employee reports
    employee_id = Column(
        Integer,
        ForeignKey("controlling_employees.id"),
        nullable=True,
        index=True
    )
    report_type = Column(SQLEnum(ReportType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    # Serialized report data including charts, quotas, raw data
    data = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    
    # Relationships
    employee = relationship("Employee", back_populates="reports")
    
    def __repr__(self):
        return (
            f"<Report(id={self.id}, type={self.report_type.value}, "
            f"employee_id={self.employee_id}, "
            f"created_at={self.created_at})>"
        )


class EvaluationPeriod(Base):
    """
    Evaluation Period model for managing time-based performance evaluations.
    
    Allows users to create, manage, and track evaluation periods
    (monthly, quarterly, yearly, custom) for organized performance tracking.
    """
    __tablename__ = "controlling_evaluation_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # z.B. "Januar 2025", "Q1 2025"
    description = Column(Text, nullable=True)
    
    period_type = Column(
        SQLEnum(PeriodType),
        nullable=False,
        index=True
    )
    
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    status = Column(
        SQLEnum(PeriodStatus),
        default=PeriodStatus.ACTIVE,
        nullable=False,
        index=True
    )
    
    # Optionale Mitarbeiterzuordnung (None = alle Mitarbeiter)
    employee_id = Column(
        Integer,
        ForeignKey("controlling_employees.id"),
        nullable=True,
        index=True
    )
    
    # Metadaten
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    employee = relationship("Employee")
    performance_data = relationship(
        "PerformanceData",
        back_populates="period",
        cascade="all, delete-orphan"
    )
    
    @property
    def duration_days(self) -> int:
        """Calculate duration in days"""
        delta = self.end_date - self.start_date
        return delta.days + 1  # +1 to include both start and end date
    
    @property
    def is_active(self) -> bool:
        """Check if period is currently active"""
        return self.status == PeriodStatus.ACTIVE
    
    @property
    def is_completed(self) -> bool:
        """Check if period is completed"""
        return self.status == PeriodStatus.COMPLETED
    
    def __repr__(self):
        return (
            f"<EvaluationPeriod(id={self.id}, name='{self.name}', "
            f"type={self.period_type.value}, status={self.status.value})>"
        )


# Standard criteria that should be initialized
STANDARD_CRITERIA = [
    {
        "name": "Kunden terminiert",
        "description": "Anzahl der terminierten Kunden",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "QC bestanden",
        "description": "Anzahl der bestandenen Qualitätskontrollen",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Storniert / kein Interesse",
        "description": "Anzahl der stornierten oder nicht interessierten Kunden",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Nicht erreicht / neu terminieren",
        "description": (
            "Anzahl der nicht erreichten Kunden, "
            "die neu terminiert werden müssen"
        ),
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Technisch nicht machbar",
        "description": "Anzahl der technisch nicht machbaren Projekte",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Angefahrene Termine",
        "description": "Anzahl der angefahrenen Termine",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Nicht angefahrene Termine",
        "description": "Anzahl der nicht angefahrenen Termine",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Verkauf",
        "description": "Anzahl der abgeschlossenen Verkäufe",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Folgetermin gemacht",
        "description": "Anzahl der vereinbarten Folgetermine",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Zu teuer gewesen",
        "description": "Anzahl der Kunden, denen es zu teuer war",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Angebot erhalten",
        "description": "Anzahl der erstellten Angebote",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Getätigte Anrufe gesamt",
        "description": "Gesamtanzahl der getätigten Anrufe",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Angefahrene Termine gesamt",
        "description": "Gesamtanzahl der angefahrenen Termine",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    },
    {
        "name": "Sonstiges",
        "description": "Sonstige Aktivitäten",
        "calculation_method": CalculationMethod.SUM,
        "is_standard": True
    }
]
