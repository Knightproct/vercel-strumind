"""
Linear structural analysis implementation
"""

import numpy as np
from typing import Dict, List, Any
import time
import logging

from app.core.analysis.engine import AnalysisEngine
from app.schemas.analysis import AnalysisSettings

logger = logging.getLogger(__name__)

class LinearAnalysis:
    """
    Linear structural analysis implementation
    
    This class implements linear static analysis using the finite element method.
    It handles:
    - Linear elastic material behavior
    - Small displacement theory
    - Static loading conditions
    """
    
    def __init__(self, engine: AnalysisEngine):
        """Initialize linear analysis with analysis engine"""
        self.engine = engine
        self.results: Dict[str, Any] = {}
        
    async def run(self, load_case_ids: List[str], settings: AnalysisSettings) -> Dict[str, Any]:
        """
        Run linear analysis for specified load cases
        
        Args:
            load_case_ids: List of load case IDs to analyze
            settings: Analysis settings
            
        Returns:
            Dictionary containing analysis results for each load case
        """
        logger.info(f"Starting linear analysis for {len(load_case_ids)} load cases")
        start_time = time.time()
        
        try:
            # Prepare model
            self.engine.prepare_model()
            
            # Assemble global stiffness matrix
            K_global = self.engine.assemble_global_stiffness()
            
            # Analyze each load case
            results = {}
            
            for load_case_id in load_case_ids:
                logger.info(f"Analyzing load case: {load_case_id}")
                
                # Assemble load vector
                F_global = self.engine.assemble_load_vector(load_case_id)
                
                # Solve system
                displacements = self.engine.solve_system(K_global, F_global)
                
                # Calculate reactions
                reactions = self.engine.calculate_reactions(displacements)
                
                # Calculate element forces
                element_forces = self.engine.calculate_element_forces(displacements)
                
                # Process results
                node_results = self._process_node_results(displacements, reactions)
                element_results = self._process_element_results(element_forces)
                
                results[load_case_id] = {
                    'node_results': node_results,
                    'element_results': element_results,
                    'analysis_time': time.time() - start_time,
                    'convergence_info': {
                        'converged': True,
                        'iterations': 1,
                        'residual': 0.0
                    }
                }
            
            total_time = time.time() - start_time
            logger.info(f"Linear analysis completed in {total_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            logger.error(f"Linear analysis failed: {e}")
            raise
    
    def _process_node_results(self, displacements: np.ndarray, reactions: np.ndarray) -> Dict[str, Any]:
        """Process node results into structured format"""
        node_results = {}
        
        for node in self.engine.nodes.values():
            # Extract displacements
            node_displacements = {}
            node_reactions = {}
            
            dof_names = ['dx', 'dy', 'dz', 'rx', 'ry', 'rz']
            
            for i, dof_name in enumerate(dof_names):
                global_dof = node.dof_indices[i]
                
                if global_dof >= 0:
                    # Free DOF - has displacement
                    node_displacements[dof_name] = float(displacements[global_dof])
                    node_reactions[dof_name] = 0.0
                else:
                    # Restrained DOF - has reaction
                    node_displacements[dof_name] = 0.0
                    # Would need to calculate actual reaction force
                    node_reactions[dof_name] = 0.0
            
            node_results[str(node.node_id)] = {
                'displacements': node_displacements,
                'reactions': node_reactions
            }
        
        return node_results
    
    def _process_element_results(self, element_forces: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Process element results into structured format"""
        element_results = {}
        
        for element_id, forces in element_forces.items():
            element = self.engine.elements[element_id]
            
            element_results[str(element.element_id)] = {
                'forces': {
                    'axial': forces['axial'],
                    'shear_y': forces['shear_y'],
                    'shear_z': forces['shear_z'],
                    'torsion': forces['torsion'],
                    'moment_y': forces['moment_y'],
                    'moment_z': forces['moment_z']
                },
                'stresses': self._calculate_stresses(element, forces),
                'strains': {}  # Would calculate if needed
            }
        
        return element_results
    
    def _calculate_stresses(self, element, forces: Dict[str, Any]) -> Dict[str, float]:
        """Calculate element stresses from forces"""
        # Simplified stress calculation
        A = element.section.get('A', 1.0)
        Sy = element.section.get('Sy', 1.0)
        Sz = element.section.get('Sz', 1.0)
        
        stresses = {
            'axial': forces['axial'] / A if A > 0 else 0.0,
            'bending_y': forces['moment_y'] / Sy if Sy > 0 else 0.0,
            'bending_z': forces['moment_z'] / Sz if Sz > 0 else 0.0,
            'shear_y': forces['shear_y'] / A if A > 0 else 0.0,
            'shear_z': forces['shear_z'] / A if A > 0 else 0.0
        }
        
        # Combined stress (simplified)
        stresses['combined'] = abs(stresses['axial']) + abs(stresses['bending_y']) + abs(stresses['bending_z'])
        
        return stresses
