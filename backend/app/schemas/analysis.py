"""
Pydantic schemas for analysis-related API models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class AnalysisType(str, Enum):
    """Analysis types"""
    LINEAR = "linear"
    NONLINEAR = "nonlinear"
    PDELTA = "p_delta"
    DYNAMIC = "dynamic"
    BUCKLING = "buckling"
    MODAL = "modal"

class SolverType(str, Enum):
    """Solver types"""
    DIRECT = "direct"
    ITERATIVE = "iterative"
    SPARSE = "sparse"

class AnalysisSettings(BaseModel):
    """Analysis settings schema"""
    analysis_type: AnalysisType = AnalysisType.LINEAR
    solver_type: SolverType = SolverType.SPARSE
    max_iterations: int = Field(default=100, ge=1, le=10000)
    convergence_tolerance: float = Field(default=1e-6, gt=0)
    include_pdelta: bool = False
    include_geometric_nonlinearity: bool = False
    include_material_nonlinearity: bool = False
    
    # Dynamic analysis settings
    time_step: Optional[float] = Field(None, gt=0)
    duration: Optional[float] = Field(None, gt=0)
    damping_ratio: Optional[float] = Field(None, ge=0, le=1)
    
    # Modal analysis settings
    num_modes: Optional[int] = Field(None, ge=1, le=1000)
    frequency_range: Optional[List[float]] = None
    
    # Advanced settings
    advanced_settings: Dict[str, Any] = Field(default_factory=dict)

class AnalysisRequest(BaseModel):
    """Analysis request schema"""
    model_id: str
    load_case_ids: List[str] = Field(..., min_items=1)
    settings: AnalysisSettings = Field(default_factory=AnalysisSettings)
    save_results: bool = True

class AnalysisStatus(str, Enum):
    """Analysis status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AnalysisJob(BaseModel):
    """Analysis job schema"""
    id: str
    model_id: str
    status: AnalysisStatus
    progress: float = Field(ge=0, le=100)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class NodeResult(BaseModel):
    """Node analysis results"""
    node_id: int
    displacements: Dict[str, float] = Field(default_factory=dict)  # dx, dy, dz, rx, ry, rz
    reactions: Dict[str, float] = Field(default_factory=dict)      # Fx, Fy, Fz, Mx, My, Mz

class ElementResult(BaseModel):
    """Element analysis results"""
    element_id: int
    forces: Dict[str, float] = Field(default_factory=dict)    # Axial, shear, moment
    stresses: Dict[str, float] = Field(default_factory=dict)  # Normal, shear stresses
    strains: Dict[str, float] = Field(default_factory=dict)   # Normal, shear strains

class AnalysisResults(BaseModel):
    """Complete analysis results"""
    model_id: str
    load_case_id: str
    analysis_type: str
    node_results: List[NodeResult] = Field(default_factory=list)
    element_results: List[ElementResult] = Field(default_factory=list)
    analysis_time: float
    convergence_info: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

class AnalysisResultSummary(BaseModel):
    """Analysis result summary"""
    id: str
    model_id: str
    analysis_type: str
    load_case_id: str
    analysis_time: float
    created_at: datetime
    
    # Summary statistics
    max_displacement: float
    max_stress: float
    max_reaction: float
    
    class Config:
        from_attributes = True
