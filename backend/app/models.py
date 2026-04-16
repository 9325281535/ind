# Data models definition
from sqlalchemy import (
    Column, String, Text, DateTime, Index, ForeignKey, 
    Enum, TIMESTAMP, func, INET, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base

# Enums
class PipelineType(str, PyEnum):
    DATA_INGESTION = "data_ingestion"
    TRAINING = "training"
    DEPLOYMENT = "deployment"

class PipelineState(str, PyEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

# Table 1: Pipelines
class Pipeline(Base):
    __tablename__ = "pipelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    pipeline_type = Column(Enum(PipelineType), nullable=False)
    current_state = Column(Enum(PipelineState), nullable=False, default=PipelineState.PENDING)
    
    # FIXED: Use JSONB and dict callable
    metadata_col = Column("metadata", JSONB, default=dict) 
    
    # NEW: Soft delete flag to protect audit history
    is_deleted = Column(Boolean, default=False, nullable=False) 
    
    created_by = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    # Relationships
    state_history = relationship("PipelineStateHistory", back_populates="pipeline")
    audit_logs = relationship("AuditLog", back_populates="pipeline")
    
    # Indexes
    __table_args__ = (
        Index("idx_pipelines_state", "current_state"),
        Index("idx_pipelines_type", "pipeline_type"),
        Index("idx_pipelines_created", "created_at", postgresql_using="btree", postgresql_desc=True),
        Index("idx_pipelines_deleted", "is_deleted"),
    )

# Table 2: Pipeline State History (IMMUTABLE)
class PipelineStateHistory(Base):
    __tablename__ = "pipeline_state_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.id"), nullable=False)
    from_state = Column(Enum(PipelineState))
    to_state = Column(Enum(PipelineState), nullable=False)
    transition_reason = Column(Text)
    triggered_by = Column(String(100), nullable=False)
    
    metadata_col = Column("metadata", JSONB, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationship
    pipeline = relationship("Pipeline", back_populates="state_history")
    
    # Indexes
    __table_args__ = (
        Index("idx_history_pipeline", "pipeline_id"),
        Index("idx_history_created", "created_at", postgresql_using="btree", postgresql_desc=True),
    )

# Table 3: Audit Logs (IMMUTABLE - append only)
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.id"), nullable=False)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), nullable=False)
    actor_role = Column(String(50))
    
    changes = Column(JSONB, default=dict)
    metadata_col = Column("metadata", JSONB, default=dict)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationship
    pipeline = relationship("Pipeline", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index("idx_audit_pipeline", "pipeline_id"),
        Index("idx_audit_created", "created_at", postgresql_using="btree", postgresql_desc=True),
        Index("idx_audit_actor", "actor"),
    )

# Pydantic Schemas
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PipelineStateHistoryResponse(BaseModel):
    id: uuid.UUID # FIXED: Strict UUID typing
    from_state: Optional[str]
    to_state: str
    transition_reason: Optional[str]
    triggered_by: str
    metadata_col: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    action: str
    actor: str
    actor_role: Optional[str]
    changes: Dict[str, Any]
    metadata_col: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    pipeline_type: PipelineType
    created_by: str
    metadata_col: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PipelineUpdate(BaseModel):
    current_state: Optional[PipelineState] = None
    metadata_col: Optional[Dict[str, Any]] = None
    transition_reason: Optional[str] = None
    triggered_by: Optional[str] = None

class PipelineResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    pipeline_type: str
    current_state: str
    metadata_col: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool
    state_history: List[PipelineStateHistoryResponse] = []
    audit_logs: List[AuditLogResponse] = []
    
    class Config:
        from_attributes = True
