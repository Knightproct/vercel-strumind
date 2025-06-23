"""
Pydantic schemas for project-related API models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    project_type: str = Field(default="building")
    units: str = Field(default="metric")
    design_code: str = Field(default="AISC")
    settings: Dict[str, Any] = Field(default_factory=dict)

class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    project_type: Optional[str] = None
    units: Optional[str] = None
    design_code: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class Project(ProjectBase):
    """Schema for project response"""
    id: str
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class StructuralModelBase(BaseModel):
    """Base structural model schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    model_type: str = Field(default="3d_frame")
    analysis_type: str = Field(default="linear")
    geometry_data: Dict[str, Any] = Field(default_factory=dict)
    analysis_settings: Dict[str, Any] = Field(default_factory=dict)

class StructuralModelCreate(StructuralModelBase):
    """Schema for creating a structural model"""
    project_id: str

class StructuralModelUpdate(BaseModel):
    """Schema for updating a structural model"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    model_type: Optional[str] = None
    analysis_type: Optional[str] = None
    geometry_data: Optional[Dict[str, Any]] = None
    analysis_settings: Optional[Dict[str, Any]] = None

class StructuralModel(StructuralModelBase):
    """Schema for structural model response"""
    id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class NodeBase(BaseModel):
    """Base node schema"""
    node_id: int
    x: float
    y: float
    z: float
    restraints: Dict[str, bool] = Field(default_factory=dict)
    properties: Dict[str, Any] = Field(default_factory=dict)

class NodeCreate(NodeBase):
    """Schema for creating a node"""
    model_id: str

class Node(NodeBase):
    """Schema for node response"""
    id: str
    model_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ElementBase(BaseModel):
    """Base element schema"""
    element_id: int
    element_type: str
    start_node_id: str
    end_node_id: str
    material_id: Optional[str] = None
    section_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    orientation: Dict[str, Any] = Field(default_factory=dict)

class ElementCreate(ElementBase):
    """Schema for creating an element"""
    model_id: str

class Element(ElementBase):
    """Schema for element response"""
    id: str
    model_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MaterialBase(BaseModel):
    """Base material schema"""
    name: str
    material_type: str
    elastic_modulus: Optional[float] = None
    shear_modulus: Optional[float] = None
    poisson_ratio: Optional[float] = None
    density: Optional[float] = None
    yield_strength: Optional[float] = None
    ultimate_strength: Optional[float] = None
    compressive_strength: Optional[float] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

class MaterialCreate(MaterialBase):
    """Schema for creating a material"""
    model_id: str

class Material(MaterialBase):
    """Schema for material response"""
    id: str
    model_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoadCaseBase(BaseModel):
    """Base load case schema"""
    name: str
    load_type: str
    loads: List[Dict[str, Any]] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)

class LoadCaseCreate(LoadCaseBase):
    """Schema for creating a load case"""
    model_id: str

class LoadCase(LoadCaseBase):
    """Schema for load case response"""
    id: str
    model_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
