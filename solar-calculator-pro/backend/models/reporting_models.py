# Reporting and Analytics Database Models

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class Report(Base):
    """Report definition model"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False, index=True)
    definition = Column(JSON, nullable=False)  # ReportDefinition as JSON
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="reports")
    schedules = relationship("ReportSchedule", back_populates="report", cascade="all, delete-orphan")
    executions = relationship("ReportExecution", back_populates="report", cascade="all, delete-orphan")


class ReportSchedule(Base):
    """Report schedule model"""
    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    frequency = Column(String(50), nullable=False)
    time_of_day = Column(String(5), nullable=False)  # HH:MM
    recipients = Column(JSON, nullable=False)  # List of email addresses
    format = Column(String(20), nullable=False)
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    report = relationship("Report", back_populates="schedules")


class ReportExecution(Base):
    """Report execution history model"""
    __tablename__ = "report_executions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)
    parameters = Column(JSON, default=dict)
    format = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, running
    result_file = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    
    # Relationships
    report = relationship("Report", back_populates="executions")
    user = relationship("User")


class Dashboard(Base):
    """Dashboard model"""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    layout = Column(String(20), default="grid")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="dashboards")
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")


class DashboardWidget(Base):
    """Dashboard widget model"""
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    config = Column(JSON, nullable=False)  # WidgetConfig as JSON
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")


class KPI(Base):
    """KPI tracking model"""
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    metric = Column(String(100), nullable=False, index=True)
    target = Column(JSON, nullable=False)  # KPITarget as JSON
    data_source = Column(String(255), nullable=False)
    calculation = Column(JSON, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="kpis")
    values = relationship("KPIValue", back_populates="kpi", cascade="all, delete-orphan")


class KPIValue(Base):
    """KPI value history model"""
    __tablename__ = "kpi_values"

    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(Integer, ForeignKey("kpis.id"), nullable=False)
    value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=False)
    achievement_percentage = Column(Float, nullable=False)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    kpi = relationship("KPI", back_populates="values")


class PredictionModel(Base):
    """Prediction model storage"""
    __tablename__ = "prediction_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)
    data_source = Column(String(255), nullable=False)
    target_field = Column(String(100), nullable=False)
    feature_fields = Column(JSON, nullable=False)
    model_data = Column(JSON, nullable=False)  # Serialized model
    accuracy_metrics = Column(JSON, nullable=False)
    trained_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User")
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")


class Prediction(Base):
    """Prediction results model"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("prediction_models.id"), nullable=False)
    predictions = Column(JSON, nullable=False)
    confidence_intervals = Column(JSON, nullable=False)
    prediction_period = Column(Integer, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    model = relationship("PredictionModel", back_populates="predictions")


class DataExport(Base):
    """Data export history model"""
    __tablename__ = "data_exports"

    id = Column(Integer, primary_key=True, index=True)
    data_source = Column(String(255), nullable=False)
    filters = Column(JSON, default=list)
    fields = Column(JSON, default=list)
    format = Column(String(20), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    row_count = Column(Integer, nullable=False)
    exported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    exported_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User")
