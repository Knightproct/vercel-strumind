"""
Core design engine for structural design checks
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import logging

from app.models.project import StructuralModel, Element, Material, Section
from app.schemas.design import DesignSettings, DesignCheckResult, ElementDesignResult

logger = logging.getLogger(__name__)

class DesignEngine:
    """
    Core structural design engine
    
    This class provides the foundation for all structural design checks.
    It handles design code implementation, safety factors, and design
    optimization.
    """
    
    def __init__(self, model: StructuralModel):
        """Initialize design engine with structural model"""
        self.model = model
        self.elements: Dict[str, Dict[str, Any]] = {}
        self.materials: Dict[str, Dict[str, Any]] = {}
        self.sections: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Initialized design engine for model {model.id}")
    
    def prepare_design_data(self, element_ids: List[str], analysis_results: Dict[str, Any]) -> None:
        """Prepare design data from analysis results"""
        logger.info("Preparing design data...")
        
        # Process elements
        for element in self.model.elements:
            if element.id in element_ids:
                self.elements[element.id] = {
                    'element_id': element.element_id,
                    'type': element.element_type,
                    'material_id': element.material_id,
                    'section_id': element.section_id,
                    'length': self._calculate_element_length(element),
                    'properties': element.properties or {}
                }
        
        # Process materials
        for material in self.model.materials:
            self.materials[material.id] = {
                'name': material.name,
                'type': material.material_type,
                'E': material.elastic_modulus or 200000.0,
                'fy': material.yield_strength or 250.0,
                'fu': material.ultimate_strength or 400.0,
                'properties': material.properties or {}
            }
        
        # Process sections
        for section in self.model.sections:
            self.sections[section.id] = {
                'name': section.name,
                'type': section.section_type,
                'A': section.area or 1.0,
                'Ix': section.moment_inertia_y or 1.0,
                'Iy': section.moment_inertia_z or 1.0,
                'Zx': section.section_modulus_y or 1.0,
                'Zy': section.section_modulus_z or 1.0,
                'rx': np.sqrt((section.moment_inertia_y or 1.0) / (section.area or 1.0)),
                'ry': np.sqrt((section.moment_inertia_z or 1.0) / (section.area or 1.0)),
                'J': section.torsional_constant or 1.0,
                'dimensions': section.dimensions or {},
                'properties': section.properties or {}
            }
        
        # Store analysis results
        self.analysis_results = analysis_results
        
        logger.info(f"Design data prepared for {len(self.elements)} elements")
    
    def _calculate_element_length(self, element) -> float:
        """Calculate element length from node coordinates"""
        # This would get node coordinates and calculate length
        # Simplified for now
        return 1.0
    
    def run_design_checks(self, settings: DesignSettings) -> List[ElementDesignResult]:
        """Run design checks for all elements"""
        logger.info(f"Running design checks using {settings.design_code}")
        
        results = []
        
        for element_id, element_data in self.elements.items():
            logger.info(f"Checking element {element_data['element_id']}")
            
            # Get design checker based on material type and design code
            checker = self._get_design_checker(element_data, settings)
            
            # Run design checks
            element_result = checker.check_element(element_id, element_data, settings)
            results.append(element_result)
        
        logger.info(f"Design checks completed for {len(results)} elements")
        return results
    
    def _get_design_checker(self, element_data: Dict[str, Any], settings: DesignSettings):
        """Get appropriate design checker based on material and code"""
        material_id = element_data['material_id']
        material = self.materials.get(material_id, {})
        material_type = material.get('type', 'steel')
        
        if material_type == 'steel':
            if settings.design_code.value.startswith('AISC'):
                from app.core.design.steel.aisc import AISCDesignChecker
                return AISCDesignChecker(self)
            elif settings.design_code.value == 'EC3':
                from app.core.design.steel.ec3 import EC3DesignChecker
                return EC3DesignChecker(self)
        elif material_type == 'concrete':
            if settings.design_code.value == 'ACI_318':
                from app.core.design.concrete.aci import ACIDesignChecker
                return ACIDesignChecker(self)
        
        # Default to AISC steel design
        from app.core.design.steel.aisc import AISCDesignChecker
        return AISCDesignChecker(self)

class DesignChecker(ABC):
    """Abstract base class for design checkers"""
    
    def __init__(self, engine: DesignEngine):
        self.engine = engine
    
    @abstractmethod
    def check_element(self, element_id: str, element_data: Dict[str, Any], 
                     settings: DesignSettings) -> ElementDesignResult:
        """Check a single element"""
        pass
    
    def get_element_forces(self, element_id: str) -> Dict[str, float]:
        """Get analysis forces for element"""
        # Extract forces from analysis results
        element_data = self.engine.elements[element_id]
        element_number = element_data['element_id']
        
        # Get from analysis results
        element_results = self.engine.analysis_results.get('element_results', {})
        forces = element_results.get(str(element_number), {}).get('forces', {})
        
        return {
            'P': forces.get('axial', 0.0),      # Axial force
            'Vx': forces.get('shear_y', 0.0),   # Shear force X
            'Vy': forces.get('shear_z', 0.0),   # Shear force Y
            'T': forces.get('torsion', 0.0),    # Torsion
            'Mx': forces.get('moment_y', 0.0),  # Moment about X
            'My': forces.get('moment_z', 0.0),  # Moment about Y
        }
    
    def get_material_properties(self, material_id: str) -> Dict[str, float]:
        """Get material properties"""
        return self.engine.materials.get(material_id, {})
    
    def get_section_properties(self, section_id: str) -> Dict[str, float]:
        """Get section properties"""
        return self.engine.sections.get(section_id, {})
    
    def create_design_check(self, check_type: str, demand: float, capacity: float,
                          equation: str = None, details: Dict[str, Any] = None) -> DesignCheckResult:
        """Create a design check result"""
        ratio = demand / capacity if capacity > 0 else float('inf')
        status = "PASS" if ratio <= 1.0 else "FAIL"
        
        if 0.9 <= ratio <= 1.0:
            status = "WARNING"
        
        return DesignCheckResult(
            check_type=check_type,
            demand=demand,
            capacity=capacity,
            ratio=ratio,
            status=status,
            governing_equation=equation,
            details=details or {}
        )
