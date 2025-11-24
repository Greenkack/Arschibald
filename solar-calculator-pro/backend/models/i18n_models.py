"""
i18n Database Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class Translation(Base):
    """Translation model for storing all translations"""

    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, index=True)
    namespace = Column(String(100), nullable=False, index=True)
    language = Column(String(10), nullable=False, index=True)
    value = Column(Text, nullable=False)
    modified_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Composite index for fast lookups
    __table_args__ = (
        Index('idx_translation_lookup', 'key', 'namespace', 'language'),
        Index('idx_namespace_language', 'namespace', 'language'),
    )

    def __repr__(self):
        return f"<Translation {self.namespace}.{self.key} ({self.language})>"


class UserLanguagePreference(Base):
    """User language preference model"""

    __tablename__ = "user_language_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    language = Column(String(10), nullable=False, default="de")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship to user
    # user = relationship("User", back_populates="language_preference")

    def __repr__(self):
        return f"<UserLanguagePreference user_id={self.user_id} language={self.language}>"


class TranslationHistory(Base):
    """Translation history for audit trail"""

    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)
    translation_id = Column(Integer, ForeignKey("translations.id"), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text, nullable=False)
    modified_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime, default=datetime.now)

    # Relationship to translation
    translation = relationship("Translation")

    def __repr__(self):
        return f"<TranslationHistory id={self.id} translation_id={self.translation_id}>"
