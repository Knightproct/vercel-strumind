"""
Pydantic schemas for design-related API models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class DesignCode(str, Enum):
    """Design codes"""
    AISC_360 = "AISC_360"
    AISC_341 = "AISC_341"
    EC3 = "EC3"
    AS4100 = "AS4100"
    CSA_S16 = "CSA_S16"
    ACI_318 = "ACI_318"
    EC2 = "EC2"

class MaterialType(str, Enum):
    """Material types for design"""
    STEEL = "steel"
    CONCRETE = "concrete"
    COMPOSITE = "composite"
    TIMBER = "timber"

class DesignSettings(BaseModel):
    """Design settings schema"""
    design_code: DesignCode = DesignCode.AISC_360
    material_type: MaterialType = MaterialType.STEEL
    
    # Safety factors
    load_factors: Dict[str, float] = Field(default_factory=dict)
    resistance_factors: Dict[str, float] = Field(default_factory=dict)
    
    # Design parameters
    effective_length_factors: Dict[str, float] = Field(default_factory=dict)
    lateral_torsional_buckling: bool = True
    local_buckling: bool = True
    
    # Deflection limits
    deflection_limits: Dict[str, float] = Field(default_factory=dict)
    
    # Advanced settings
    advanced_settings: Dict[str, Any] = Field(default_factory=dict)

class DesignRequest(BaseModel):
    """Design request schema"""
    model_id: str
    element_ids: List[str] = Field(..., min_items=1)
    analysis_result_id: str
    settings: DesignSettings = Field(default_factory=DesignSettings)

class DesignCheckType(str, Enum):
    """Design check types"""
    TENSION = "tension"
    COMPRESSION = "compression"
    FLEXURE = "flexure"
    SHEAR = "shear"
    COMBINED = "combined"
    DEFLECTION = "deflection"
    VIBRATION = "vibration"

class DesignCheckResult(BaseModel):
    """Individual design check result"""
    check_type: DesignCheckType
    demand: float
    capacity: float
    ratio: float = Field(ge=0)
    status: str  # "PASS", "FAIL", "WARNING"
    governing_equation: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class ElementDesignResult(BaseModel):
    """Design results for a single element"""
    element_id: str
    element_type: str
    section_name: str
    material_name: str
    
    # Design checks
    design_checks: List[DesignCheckResult] = Field(default_factory=list)
    
    # Overall results
    controlling_ratio: float = Field(ge=0)
    controlling_check: Optional[str] = None
    overall_status: str  # "PASS", "FAIL", "WARNING"
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)

class DesignResults(BaseModel):
    """Complete design results"""
    model_id: str
    analysis_result_id: str
    design_code: str
    element_results: List[ElementDesignResult] = Field(default_factory=list)
    
    # Summary
    total_elements: int
    passed_elements: int
    failed_elements: int
    warning_elements: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True

class SectionOptimization(BaseModel):
    """Section optimization request"""
    element_ids: List[str]
    target_ratio: float = Field(default=0.9, ge=0.1, le=1.0)
    available_sections: List[str] = Field(default_factory=list)
    optimize_weight: bool = True
    optimize_cost: bool = False

class OptimizationResult(BaseModel):
    """Section optimization result"""
    element_id: str
    original_section: str
    optimized_section: str
    weight_savings: float
    cost_savings: Optional[float] = None
    design_ratio: float
