# API routes and endpoints
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from .database import get_db
from .models import (
    Pipeline, PipelineStateHistory, AuditLog,
    PipelineState, PipelineType,
    PipelineCreate, PipelineUpdate, PipelineResponse,
    PipelineStateHistoryResponse, AuditLogResponse
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["pipelines"])

# ==================== PIPELINE ENDPOINTS ====================

@router.post("/pipelines", response_model=PipelineResponse)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Create a new ML pipeline"""
    try:
        new_pipeline = Pipeline(
            name=pipeline_data.name,
            description=pipeline_data.description,
            pipeline_type=pipeline_data.pipeline_type,
            current_state=PipelineState.PENDING,
            metadata=pipeline_data.metadata or {},
            created_by=pipeline_data.created_by
        )
        db.add(new_pipeline)
        await db.flush()
        
        # Log the creation
        audit_log = AuditLog(
            pipeline_id=new_pipeline.id,
            action="CREATED",
            actor=pipeline_data.created_by,
            actor_role="admin",
            changes={"name": pipeline_data.name, "type": pipeline_data.pipeline_type},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        db.add(audit_log)
        await db.commit()
        
        return PipelineResponse.from_orm(new_pipeline)
    except Exception as e:
        logger.error(f"Error creating pipeline: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pipelines", response_model=list[PipelineResponse])
async def list_pipelines(
    skip: int = Query(0),
    limit: int = Query(10),
    state: PipelineState = Query(None),
    pipeline_type: PipelineType = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all pipelines with optional filtering"""
    try:
        query = select(Pipeline)
        
        if state:
            query = query.where(Pipeline.current_state == state)
        if pipeline_type:
            query = query.where(Pipeline.pipeline_type == pipeline_type)
        
        query = query.order_by(desc(Pipeline.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        pipelines = result.scalars().all()
        
        return [PipelineResponse.from_orm(p) for p in pipelines]
    except Exception as e:
        logger.error(f"Error listing pipelines: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific pipeline by ID"""
    try:
        query = select(Pipeline).where(Pipeline.id == pipeline_id)
        result = await db.execute(query)
        pipeline = result.scalar_one_or_none()
        
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        return PipelineResponse.from_orm(pipeline)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pipeline: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: str,
    update_data: PipelineUpdate,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Update pipeline state and metadata"""
    try:
        query = select(Pipeline).where(Pipeline.id == pipeline_id)
        result = await db.execute(query)
        pipeline = result.scalar_one_or_none()
        
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Record state transition
        if update_data.current_state and update_data.current_state != pipeline.current_state:
            state_history = PipelineStateHistory(
                pipeline_id=pipeline.id,
                from_state=pipeline.current_state,
                to_state=update_data.current_state,
                transition_reason=update_data.transition_reason,
                triggered_by=update_data.triggered_by or "SYSTEM",
                metadata={"previous_metadata": pipeline.metadata}
            )
            db.add(state_history)
            
            # Log the state change
            audit_log = AuditLog(
                pipeline_id=pipeline.id,
                action="STATE_CHANGED",
                actor=update_data.triggered_by or "SYSTEM",
                changes={
                    "previous_state": pipeline.current_state.value,
                    "new_state": update_data.current_state.value,
                    "reason": update_data.transition_reason
                },
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
            db.add(audit_log)
            
            pipeline.current_state = update_data.current_state
        
        # Update metadata
        if update_data.metadata:
            pipeline.metadata = {**pipeline.metadata, **update_data.metadata}
        
        pipeline.updated_at = datetime.utcnow()
        await db.commit()
        
        return PipelineResponse.from_orm(pipeline)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pipeline: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pipelines/{pipeline_id}/state-history", response_model=list[PipelineStateHistoryResponse])
async def get_state_history(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get state transition history for a pipeline"""
    try:
        query = select(PipelineStateHistory).where(
            PipelineStateHistory.pipeline_id == pipeline_id
        ).order_by(desc(PipelineStateHistory.created_at))
        
        result = await db.execute(query)
        history = result.scalars().all()
        
        return [PipelineStateHistoryResponse.from_orm(h) for h in history]
    except Exception as e:
        logger.error(f"Error fetching state history: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pipelines/{pipeline_id}/audit-logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs for a pipeline"""
    try:
        query = select(AuditLog).where(
            AuditLog.pipeline_id == pipeline_id
        ).order_by(desc(AuditLog.created_at))
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [AuditLogResponse.from_orm(log) for log in logs]
    except Exception as e:
        logger.error(f"Error fetching audit logs: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/pipelines/{pipeline_id}")
async def delete_pipeline(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Delete a pipeline (soft delete via CANCELLED state)"""
    try:
        query = select(Pipeline).where(Pipeline.id == pipeline_id)
        result = await db.execute(query)
        pipeline = result.scalar_one_or_none()
        
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Mark as cancelled instead of hard delete for audit trail
        pipeline.current_state = PipelineState.CANCELLED
        pipeline.updated_at = datetime.utcnow()
        
        state_history = PipelineStateHistory(
            pipeline_id=pipeline.id,
            from_state=pipeline.current_state,
            to_state=PipelineState.CANCELLED,
            transition_reason="Pipeline deleted by user",
            triggered_by="SYSTEM",
        )
        db.add(state_history)
        
        audit_log = AuditLog(
            pipeline_id=pipeline.id,
            action="DELETED",
            actor="SYSTEM",
            changes={"status": "cancelled"},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        db.add(audit_log)
        
        await db.commit()
        return {"message": "Pipeline cancelled", "id": str(pipeline.id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pipeline: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ==================== DASHBOARD ENDPOINTS ====================

@router.get("/dashboard/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Get pipeline summary for dashboard"""
    try:
        query = select(Pipeline)
        result = await db.execute(query)
        pipelines = result.scalars().all()
        
        summary = {
            "total": len(pipelines),
            "pending": sum(1 for p in pipelines if p.current_state == PipelineState.PENDING),
            "running": sum(1 for p in pipelines if p.current_state == PipelineState.RUNNING),
            "completed": sum(1 for p in pipelines if p.current_state == PipelineState.COMPLETED),
            "failed": sum(1 for p in pipelines if p.current_state == PipelineState.FAILED),
            "cancelled": sum(1 for p in pipelines if p.current_state == PipelineState.CANCELLED),
        }
        
        summary["success_rate"] = (
            (summary["completed"] / summary["total"] * 100)
            if summary["total"] > 0 else 0
        )
        
        return summary
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))