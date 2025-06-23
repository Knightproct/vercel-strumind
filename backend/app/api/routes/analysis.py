"""
Structural analysis API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from datetime import datetime

from app.db.database import get_db
from app.models.project import StructuralModel, AnalysisResult
from app.models.user import User
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisJob,
    AnalysisResults,
    AnalysisResultSummary,
    AnalysisStatus
)
from app.api.dependencies import get_current_user
from app.core.analysis.engine import AnalysisEngine
from app.core.analysis.linear import LinearAnalysis
from app.core.analysis.nonlinear import NonlinearAnalysis

router = APIRouter()

# In-memory job tracking (in production, use Redis or database)
analysis_jobs: Dict[str, Dict[str, Any]] = {}

@router.post("/run", response_model=AnalysisJob)
async def run_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start structural analysis"""
    
    # Verify model exists and user has access
    model = db.query(StructuralModel).filter(
        StructuralModel.id == request.model_id,
        StructuralModel.is_active == True
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structural model not found"
        )
    
    # Verify project ownership
    if model.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Create analysis job
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "model_id": request.model_id,
        "status": AnalysisStatus.PENDING,
        "progress": 0.0,
        "started_at": None,
        "completed_at": None,
        "error_message": None,
        "request": request
    }
    
    analysis_jobs[job_id] = job
    
    # Start analysis in background
    background_tasks.add_task(
        run_analysis_task,
        job_id,
        request,
        db
    )
    
    return AnalysisJob(**job)

async def run_analysis_task(
    job_id: str,
    request: AnalysisRequest,
    db: Session
):
    """Background task to run analysis"""
    
    job = analysis_jobs[job_id]
    
    try:
        # Update job status
        job["status"] = AnalysisStatus.RUNNING
        job["started_at"] = datetime.utcnow()
        job["progress"] = 10.0
        
        # Get model data
        model = db.query(StructuralModel).filter(
            StructuralModel.id == request.model_id
        ).first()
        
        # Initialize analysis engine
        engine = AnalysisEngine(model)
        job["progress"] = 20.0
        
        # Run analysis based on type
        if request.settings.analysis_type == "linear":
            analyzer = LinearAnalysis(engine)
        elif request.settings.analysis_type == "nonlinear":
            analyzer = NonlinearAnalysis(engine)
        else:
            raise ValueError(f"Unsupported analysis type: {request.settings.analysis_type}")
        
        job["progress"] = 30.0
        
        # Execute analysis
        results = await analyzer.run(request.load_case_ids, request.settings)
        job["progress"] = 90.0
        
        # Save results if requested
        if request.save_results:
            for load_case_id, result in results.items():
                db_result = AnalysisResult(
                    model_id=request.model_id,
                    analysis_type=request.settings.analysis_type,
                    load_case_id=load_case_id,
                    node_results=result["node_results"],
                    element_results=result["element_results"],
                    analysis_time=result["analysis_time"],
                    convergence_info=result["convergence_info"]
                )
                db.add(db_result)
            
            db.commit()
        
        # Update job completion
        job["status"] = AnalysisStatus.COMPLETED
        job["completed_at"] = datetime.utcnow()
        job["progress"] = 100.0
        job["results"] = results
        
    except Exception as e:
        job["status"] = AnalysisStatus.FAILED
        job["error_message"] = str(e)
        job["completed_at"] = datetime.utcnow()

@router.get("/jobs/{job_id}", response_model=AnalysisJob)
async def get_analysis_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get analysis job status"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found"
        )
    
    job = analysis_jobs[job_id]
    return AnalysisJob(**job)

@router.get("/models/{model_id}/results", response_model=List[AnalysisResultSummary])
async def get_analysis_results(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analysis results for a model"""
    
    # Verify model access
    model = db.query(StructuralModel).filter(
        StructuralModel.id == model_id,
        StructuralModel.is_active == True
    ).first()
    
    if not model or model.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found or access denied"
        )
    
    results = db.query(AnalysisResult).filter(
        AnalysisResult.model_id == model_id
    ).all()
    
    # Convert to summary format
    summaries = []
    for result in results:
        # Calculate summary statistics
        max_displacement = 0.0
        max_stress = 0.0
        max_reaction = 0.0
        
        # Extract max values from results
        if result.node_results:
            for node_result in result.node_results.values():
                if isinstance(node_result, dict):
                    displacements = node_result.get("displacements", {})
                    reactions = node_result.get("reactions", {})
                    
                    max_displacement = max(max_displacement, 
                                         max(abs(v) for v in displacements.values() if isinstance(v, (int, float))))
                    max_reaction = max(max_reaction,
                                     max(abs(v) for v in reactions.values() if isinstance(v, (int, float))))
        
        if result.element_results:
            for elem_result in result.element_results.values():
                if isinstance(elem_result, dict):
                    stresses = elem_result.get("stresses", {})
                    max_stress = max(max_stress,
                                   max(abs(v) for v in stresses.values() if isinstance(v, (int, float))))
        
        summary = AnalysisResultSummary(
            id=result.id,
            model_id=result.model_id,
            analysis_type=result.analysis_type,
            load_case_id=result.load_case_id,
            analysis_time=result.analysis_time or 0.0,
            created_at=result.created_at,
            max_displacement=max_displacement,
            max_stress=max_stress,
            max_reaction=max_reaction
        )
        summaries.append(summary)
    
    return summaries

@router.get("/results/{result_id}", response_model=AnalysisResults)
async def get_analysis_result_detail(
    result_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analysis results"""
    
    result = db.query(AnalysisResult).filter(
        AnalysisResult.id == result_id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found"
        )
    
    # Verify access
    if result.model.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return AnalysisResults(
        model_id=result.model_id,
        load_case_id=result.load_case_id,
        analysis_type=result.analysis_type,
        node_results=[],  # Convert from JSON storage
        element_results=[],  # Convert from JSON storage
        analysis_time=result.analysis_time or 0.0,
        convergence_info=result.convergence_info or {}
    )

@router.delete("/jobs/{job_id}")
async def cancel_analysis_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a running analysis job"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found"
        )
    
    job = analysis_jobs[job_id]
    
    if job["status"] in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or failed job"
        )
    
    job["status"] = AnalysisStatus.CANCELLED
    job["completed_at"] = datetime.utcnow()
    
    return {"message": "Analysis job cancelled"}
