from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class DocumentStatus(enum.Enum):
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    REDLINE_READY = "redline_ready"
    FEEDBACK_RECEIVED = "feedback_received"
    CLEAN_READY = "clean_ready"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"))
    original_path = Column(String)
    redline_path = Column(String, nullable=True)
    clean_path = Column(String, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="documents")
    analysis_results = relationship("AnalysisResult", back_populates="document")
    feedback_history = relationship("Feedback", back_populates="document")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"))
    clause_text = Column(Text)
    original_text = Column(Text)
    suggested_text = Column(Text, nullable=True)
    confidence_score = Column(Integer)  # 0-100
    validation_score = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="analysis_results")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"))
    feedback_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="feedback_history") 