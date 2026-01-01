"""
Database Models with Universal Data Support

SQLAlchemy models that include dynamic_key and pdf_bytes columns
for all tables, integrating with the Universal Data System.

Requirements: 14.4, 14.7
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, LargeBinary, Index
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from backend.core.database import Base
from backend.core.universal_data import UniversalDataModel
from backend.core.dynamic_keys import KeyPrefix, DynamicKeyMixin
from backend.core.pdf_bytes import PDFByteMixin


class UniversalDatabaseModel(Base):
    """
    Base class for all database models with universal data support.
    
    This class combines SQLAlchemy ORM with UniversalDataModel capabilities,
    providing dynamic keys, PDF generation, and German formatting for all models.
    """
    
    __abstract__ = True
    
    # Universal columns for all tables
    id = Column(Integer, primary_key=True, index=True)
    dynamic_key = Column(String(255), unique=True, index=True, nullable=True)
    pdf_bytes = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __init__(self, **kwargs):
        """Initialize model with universal data support"""
        super().__init__(**kwargs)
        # Initialize mixins manually
        DynamicKeyMixin.__init__(self)
        PDFByteMixin.__init__(self)
        # Initialize German formatter
        from backend.core.german_formatter import GermanNumberFormatter
        self._german_formatter = GermanNumberFormatter()
        self._locale = 'de-DE'
        self._decimal_places = 2
    
    def generate_and_store_key(self, prefix: KeyPrefix):
        """Generate dynamic key and store in database column"""
        key = self.generate_dynamic_key(prefix)
        self.dynamic_key = key
        return key
    
    def generate_and_store_pdf(self, metadata=None) -> bytes:
        """Generate PDF bytes and store in database column"""
        pdf_data = self.to_pdf_bytes(metadata)
        self.pdf_bytes = pdf_data
        return pdf_data
    
    def get_stored_pdf(self) -> Optional[bytes]:
        """Get stored PDF bytes from database"""
        return self.pdf_bytes
    
    def has_pdf(self) -> bool:
        """Check if PDF bytes are stored"""
        return self.pdf_bytes is not None and len(self.pdf_bytes) > 0
    
    def get_formatted_value(self, key: str, locale: Optional[str] = None, format_type: Optional[str] = None) -> str:
        """Get a formatted value based on locale"""
        locale = locale or self._locale
        value = getattr(self, key, None)
        
        if value is None:
            return ""
        
        # Handle boolean values BEFORE numeric
        if isinstance(value, bool):
            return "Ja" if value else "Nein" if locale == 'de-DE' else ("Yes" if value else "No")
        
        # Handle numeric values
        if isinstance(value, (int, float)):
            from decimal import Decimal
            if locale == 'de-DE':
                if format_type == 'currency':
                    return self._german_formatter.format_currency(value)
                elif format_type == 'percent':
                    return self._german_formatter.format_percent(value, multiply_by_100=False)
                else:
                    return self._german_formatter.format(value)
            else:
                if format_type == 'currency':
                    return f"${value:,.2f}"
                elif format_type == 'percent':
                    return f"{value:.2f}%"
                else:
                    return f"{value:,.2f}"
        
        # Handle datetime values
        from datetime import datetime
        if isinstance(value, datetime):
            if locale == 'de-DE':
                return value.strftime("%d.%m.%Y %H:%M:%S")
            else:
                return value.strftime("%Y-%m-%d %H:%M:%S")
        
        return str(value)
    
    def to_dict(self, include_keys: bool = True, include_metadata: bool = True, formatted: bool = False, locale: Optional[str] = None) -> dict:
        """Convert model to dictionary"""
        from sqlalchemy import inspect
        result = {}
        
        # Get all columns
        mapper = inspect(self.__class__)
        for column in mapper.columns:
            value = getattr(self, column.name)
            if formatted and value is not None:
                result[column.name] = self.get_formatted_value(column.name, locale or self._locale)
            else:
                result[column.name] = value
        
        # Add dynamic key information
        if include_keys:
            result['_dynamic_key'] = self.get_dynamic_key()
            result['_key_metadata'] = self.get_key_metadata()
        
        return result
    
    def to_json_serializable(self) -> dict:
        """Convert model to JSON-serializable dictionary"""
        from datetime import datetime
        from decimal import Decimal
        data = self.to_dict(formatted=False)
        
        # Convert non-serializable types
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Decimal):
                data[key] = float(value)
            elif isinstance(value, bytes):
                data[key] = value.decode('utf-8', errors='ignore')
        
        return data


# Example models with universal data support

class User(UniversalDatabaseModel):
    """User model with universal data support"""
    
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    
    def _get_default_title(self) -> str:
        return f"User Profile: {self.username}"
    
    def _render_to_pdf(self, story, doc):
        """Render user profile to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer
            
            styles = getSampleStyleSheet()
            
            story.append(Paragraph(f"User: {self.username}", styles['Heading1']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Email: {self.email}", styles['Normal']))
            story.append(Paragraph(f"Full Name: {self.full_name or 'N/A'}", styles['Normal']))
            story.append(Paragraph(f"Role: {self.role}", styles['Normal']))
            story.append(Paragraph(f"Status: {'Active' if self.is_active else 'Inactive'}", styles['Normal']))
        except ImportError:
            pass


class Customer(UniversalDatabaseModel):
    """Customer model with universal data support"""
    
    __tablename__ = "customers"
    
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="Germany")
    notes = Column(Text)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_customer_name', 'name'),
        Index('idx_customer_email', 'email'),
        Index('idx_customer_dynamic_key', 'dynamic_key'))
    
    def _get_default_title(self) -> str:
        return f"Customer: {self.name}"
    
    def _render_to_pdf(self, story, doc):
        """Render customer information to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer
            
            styles = getSampleStyleSheet()
            
            story.append(Paragraph(f"Customer: {self.name}", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            if self.email:
                story.append(Paragraph(f"Email: {self.email}", styles['Normal']))
            if self.phone:
                story.append(Paragraph(f"Phone: {self.phone}", styles['Normal']))
            if self.address:
                story.append(Paragraph(f"Address: {self.address}", styles['Normal']))
            if self.city:
                story.append(Paragraph(f"City: {self.city} {self.postal_code or ''}", styles['Normal']))
        except ImportError:
            pass


class Project(UniversalDatabaseModel):
    """Project model with universal data support"""
    
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    customer_id = Column(Integer, nullable=False)
    project_type = Column(String(50))  # 'solar', 'heatpump', 'combined'
    status = Column(String(50), default='draft')  # 'draft', 'active', 'completed', 'archived'
    data = Column(Text)  # JSON data
    
    # Indexes
    __table_args__ = (
        Index('idx_project_customer', 'customer_id'),
        Index('idx_project_type', 'project_type'),
        Index('idx_project_status', 'status'),
        Index('idx_project_dynamic_key', 'dynamic_key'))
    
    def _get_default_title(self) -> str:
        return f"Project: {self.name}"
    
    def _render_to_pdf(self, story, doc):
        """Render project information to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer
            
            styles = getSampleStyleSheet()
            
            story.append(Paragraph(f"Project: {self.name}", styles['Heading1']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Type: {self.project_type}", styles['Normal']))
            story.append(Paragraph(f"Status: {self.status}", styles['Normal']))
            story.append(Paragraph(f"Created: {self.created_at.strftime('%d.%m.%Y')}", styles['Normal']))
        except ImportError:
            pass


class SolarCalculation(UniversalDatabaseModel):
    """Solar calculation model with universal data support"""
    
    __tablename__ = "solar_calculations"
    
    project_id = Column(Integer, nullable=False)
    system_size = Column(Float)
    module_count = Column(Integer)
    annual_production = Column(Float)
    self_consumption_rate = Column(Float)
    payback_period = Column(Float)
    total_cost = Column(Float)
    savings_25_years = Column(Float)
    co2_savings = Column(Float)
    calculation_data = Column(Text)  # JSON with all details
    
    # Indexes
    __table_args__ = (
        Index('idx_solar_project', 'project_id'),
        Index('idx_solar_dynamic_key', 'dynamic_key'))
    
    def _get_default_title(self) -> str:
        return "Solar System Calculation"
    
    def _render_to_pdf(self, story, doc):
        """Render solar calculation to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer
            
            styles = getSampleStyleSheet()
            
            story.append(Paragraph("Solar System Calculation", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Format numbers in German format
            if self.system_size:
                formatted = self.get_formatted_value('system_size', locale='de-DE')
                story.append(Paragraph(f"System Size: {formatted} kWp", styles['Normal']))
            
            if self.module_count:
                story.append(Paragraph(f"Module Count: {self.module_count}", styles['Normal']))
            
            if self.annual_production:
                formatted = self.get_formatted_value('annual_production', locale='de-DE')
                story.append(Paragraph(f"Annual Production: {formatted} kWh", styles['Normal']))
            
            if self.total_cost:
                formatted = self.get_formatted_value('total_cost', format_type='currency')
                story.append(Paragraph(f"Total Cost: {formatted}", styles['Normal']))
        except ImportError:
            pass


class Product(UniversalDatabaseModel):
    """Product model with universal data support"""
    
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    manufacturer = Column(String(255))
    price = Column(Float)
    specifications = Column(Text)  # JSON
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_product_category', 'category'),
        Index('idx_product_manufacturer', 'manufacturer'),
        Index('idx_product_active', 'is_active'),
        Index('idx_product_dynamic_key', 'dynamic_key'))
    
    def _get_default_title(self) -> str:
        return f"Product: {self.name}"
    
    def _render_to_pdf(self, story, doc):
        """Render product information to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer
            
            styles = getSampleStyleSheet()
            
            story.append(Paragraph(f"Product: {self.name}", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            if self.manufacturer:
                story.append(Paragraph(f"Manufacturer: {self.manufacturer}", styles['Normal']))
            if self.category:
                story.append(Paragraph(f"Category: {self.category}", styles['Normal']))
            if self.price:
                formatted = self.get_formatted_value('price', format_type='currency')
                story.append(Paragraph(f"Price: {formatted}", styles['Normal']))
        except ImportError:
            pass


class Offer(UniversalDatabaseModel):
    """Offer model with universal data support"""
    
    __tablename__ = "offers"
    
    customer_id = Column(Integer, nullable=False)
    project_id = Column(Integer)
    offer_number = Column(String(100), unique=True)
    status = Column(String(50), default='draft')  # 'draft', 'sent', 'accepted', 'rejected'
    total_amount = Column(Float)
    valid_until = Column(DateTime(timezone=True))
    offer_data = Column(Text)  # JSON
    
    # Indexes
    __table_args__ = (
        Index('idx_offer_customer', 'customer_id'),
        Index('idx_offer_project', 'project_id'),
        Index('idx_offer_number', 'offer_number'),
        Index('idx_offer_status', 'status'),
        Index('idx_offer_dynamic_key', 'dynamic_key'))
    
    def _get_default_title(self) -> str:
        return f"Offer: {self.offer_number}"
    
    def _render_to_pdf(self, story, doc):
        """Render offer to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer
            
            styles = getSampleStyleSheet()
            
            story.append(Paragraph(f"Offer: {self.offer_number}", styles['Heading1']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Status: {self.status}", styles['Normal']))
            
            if self.total_amount:
                formatted = self.get_formatted_value('total_amount', format_type='currency')
                story.append(Paragraph(f"Total Amount: {formatted}", styles['Normal']))
            
            if self.valid_until:
                formatted = self.get_formatted_value('valid_until', locale='de-DE')
                story.append(Paragraph(f"Valid Until: {formatted}", styles['Normal']))
        except ImportError:
            pass


class Task(UniversalDatabaseModel):
    """Task model with universal data support"""
    
    __tablename__ = "tasks"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    customer_id = Column(Integer)
    project_id = Column(Integer)
    assigned_to = Column(Integer)  # user_id
    status = Column(String(50), default='open')  # 'open', 'in_progress', 'completed', 'cancelled'
    priority = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'urgent'
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Indexes
    __table_args__ = (
        Index('idx_task_customer', 'customer_id'),
        Index('idx_task_project', 'project_id'),
        Index('idx_task_assigned', 'assigned_to'),
        Index('idx_task_status', 'status'),
        Index('idx_task_dynamic_key', 'dynamic_key'))
    
    def _get_default_title(self) -> str:
        return f"Task: {self.title}"
    
    def _render_to_pdf(self, story, doc):
        """Render task to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer
            
            styles = getSampleStyleSheet()
            
            story.append(Paragraph(f"Task: {self.title}", styles['Heading1']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Status: {self.status}", styles['Normal']))
            story.append(Paragraph(f"Priority: {self.priority}", styles['Normal']))
            
            if self.description:
                story.append(Spacer(1, 6))
                story.append(Paragraph(f"Description: {self.description}", styles['Normal']))
        except ImportError:
            pass
