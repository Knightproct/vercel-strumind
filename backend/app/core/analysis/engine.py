"""
Core analysis engine for structural analysis
This module provides the foundation for all analysis types
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod

from app.models.project import StructuralModel, Node, Element, Material, Section, LoadCase

logger = logging.getLogger(__name__)

@dataclass
class AnalysisNode:
    """Analysis node representation"""
    id: str
    node_id: int
    coordinates: np.ndarray  # [x, y, z]
    restraints: Dict[str, bool]  # DOF restraints
    dof_indices: List[int]  # Global DOF indices

@dataclass
class AnalysisElement:
    """Analysis element representation"""
    id: str
    element_id: int
    element_type: str
    start_node: AnalysisNode
    end_node: AnalysisNode
    material: Dict[str, Any]
    section: Dict[str, Any]
    local_axes: np.ndarray  # Local coordinate system
    length: float
    stiffness_matrix: Optional[np.ndarray] = None

class AnalysisEngine:
    """
    Core structural analysis engine
    
    This class provides the foundation for all structural analysis types.
    It handles model preparation, DOF assignment, matrix assembly, and
    result processing.
    """
    
    def __init__(self, model: StructuralModel):
        """Initialize analysis engine with structural model"""
        self.model = model
        self.nodes: Dict[str, AnalysisNode] = {}
        self.elements: Dict[str, AnalysisElement] = {}
        self.materials: Dict[str, Dict[str, Any]] = {}
        self.sections: Dict[str, Dict[str, Any]] = {}
        self.load_cases: Dict[str, Dict[str, Any]] = {}
        
        # Analysis matrices
        self.global_stiffness: Optional[np.ndarray] = None
        self.global_mass: Optional[np.ndarray] = None
        self.global_damping: Optional[np.ndarray] = None
        
        # DOF management
        self.total_dofs = 0
        self.free_dofs: List[int] = []
        self.restrained_dofs: List[int] = []
        
        # Results storage
        self.displacements: Optional[np.ndarray] = None
        self.reactions: Optional[np.ndarray] = None
        
        logger.info(f"Initialized analysis engine for model {model.id}")
    
    def prepare_model(self) -> None:
        """
        Prepare the structural model for analysis
        
        This method:
        1. Processes nodes and assigns DOFs
        2. Processes elements and calculates properties
        3. Processes materials and sections
        4. Processes load cases
        """
        logger.info("Preparing structural model for analysis...")
        
        try:
            self._process_materials()
            self._process_sections()
            self._process_nodes()
            self._process_elements()
            self._process_load_cases()
            self._assign_dofs()
            
            logger.info(f"Model preparation complete. Total DOFs: {self.total_dofs}")
            
        except Exception as e:
            logger.error(f"Error preparing model: {e}")
            raise
    
    def _process_materials(self) -> None:
        """Process material properties"""
        for material in self.model.materials:
            self.materials[material.id] = {
                'name': material.name,
                'type': material.material_type,
                'E': material.elastic_modulus or 200000.0,  # Default steel E
                'G': material.shear_modulus or 80000.0,     # Default steel G
                'nu': material.poisson_ratio or 0.3,        # Default Poisson's ratio
                'density': material.density or 7850.0,      # Default steel density
                'fy': material.yield_strength or 250.0,     # Default yield strength
                'fu': material.ultimate_strength or 400.0,  # Default ultimate strength
                'properties': material.properties or {}
            }
    
    def _process_sections(self) -> None:
        """Process section properties"""
        for section in self.model.sections:
            self.sections[section.id] = {
                'name': section.name,
                'type': section.section_type,
                'A': section.area or 1.0,
                'Iy': section.moment_inertia_y or 1.0,
                'Iz': section.moment_inertia_z or 1.0,
                'J': section.torsional_constant or 1.0,
                'Sy': section.section_modulus_y or 1.0,
                'Sz': section.section_modulus_z or 1.0,
                'dimensions': section.dimensions or {},
                'properties': section.properties or {}
            }
    
    def _process_nodes(self) -> None:
        """Process structural nodes"""
        for node in self.model.nodes:
            coordinates = np.array([node.x, node.y, node.z])
            
            # Default restraints (all free)
            restraints = {
                'dx': False, 'dy': False, 'dz': False,
                'rx': False, 'ry': False, 'rz': False
            }
            restraints.update(node.restraints or {})
            
            analysis_node = AnalysisNode(
                id=node.id,
                node_id=node.node_id,
                coordinates=coordinates,
                restraints=restraints,
                dof_indices=[]  # Will be assigned later
            )
            
            self.nodes[node.id] = analysis_node
    
    def _process_elements(self) -> None:
        """Process structural elements"""
        for element in self.model.elements:
            start_node = self.nodes[element.start_node_id]
            end_node = self.nodes[element.end_node_id]
            
            # Calculate element length and local axes
            vector = end_node.coordinates - start_node.coordinates
            length = np.linalg.norm(vector)
            
            if length < 1e-6:
                raise ValueError(f"Element {element.element_id} has zero length")
            
            # Local coordinate system (simplified - assumes vertical Y-axis)
            local_x = vector / length
            local_z = np.array([0, 0, 1])
            
            # Handle vertical elements
            if abs(np.dot(local_x, local_z)) > 0.9:
                local_z = np.array([1, 0, 0])
            
            local_y = np.cross(local_z, local_x)
            local_y = local_y / np.linalg.norm(local_y)
            local_z = np.cross(local_x, local_y)
            
            local_axes = np.column_stack([local_x, local_y, local_z])
            
            # Get material and section properties
            material = self.materials.get(element.material_id, {})
            section = self.sections.get(element.section_id, {})
            
            analysis_element = AnalysisElement(
                id=element.id,
                element_id=element.element_id,
                element_type=element.element_type,
                start_node=start_node,
                end_node=end_node,
                material=material,
                section=section,
                local_axes=local_axes,
                length=length
            )
            
            self.elements[element.id] = analysis_element
    
    def _process_load_cases(self) -> None:
        """Process load cases"""
        for load_case in self.model.load_cases:
            self.load_cases[load_case.id] = {
                'name': load_case.name,
                'type': load_case.load_type,
                'loads': load_case.loads or [],
                'properties': load_case.properties or {}
            }
    
    def _assign_dofs(self) -> None:
        """Assign degrees of freedom to nodes"""
        dof_counter = 0
        
        # 6 DOFs per node (3 translations + 3 rotations)
        for node in self.nodes.values():
            node_dofs = []
            
            for dof_name in ['dx', 'dy', 'dz', 'rx', 'ry', 'rz']:
                if not node.restraints.get(dof_name, False):
                    # Free DOF
                    node_dofs.append(dof_counter)
                    self.free_dofs.append(dof_counter)
                else:
                    # Restrained DOF
                    node_dofs.append(-1)  # Mark as restrained
                    self.restrained_dofs.append(dof_counter)
                
                dof_counter += 1
            
            node.dof_indices = node_dofs
        
        self.total_dofs = len(self.free_dofs)
        logger.info(f"DOF assignment complete. Free DOFs: {self.total_dofs}")
    
    def assemble_global_stiffness(self) -> np.ndarray:
        """
        Assemble global stiffness matrix
        
        Returns:
            Global stiffness matrix for free DOFs only
        """
        logger.info("Assembling global stiffness matrix...")
        
        # Initialize global stiffness matrix
        K_global = np.zeros((self.total_dofs, self.total_dofs))
        
        for element in self.elements.values():
            # Calculate element stiffness matrix
            K_element = self._calculate_element_stiffness(element)
            
            # Get element DOF indices
            start_dofs = element.start_node.dof_indices
            end_dofs = element.end_node.dof_indices
            element_dofs = start_dofs + end_dofs
            
            # Assemble into global matrix
            for i, global_i in enumerate(element_dofs):
                if global_i >= 0:  # Free DOF
                    for j, global_j in enumerate(element_dofs):
                        if global_j >= 0:  # Free DOF
                            K_global[global_i, global_j] += K_element[i, j]
        
        self.global_stiffness = K_global
        logger.info("Global stiffness matrix assembled")
        
        return K_global
    
    def _calculate_element_stiffness(self, element: AnalysisElement) -> np.ndarray:
        """
        Calculate element stiffness matrix in global coordinates
        
        This is a simplified implementation for frame elements.
        Production code would have specialized methods for different element types.
        """
        # Material and section properties
        E = element.material.get('E', 200000.0)
        G = element.material.get('G', 80000.0)
        A = element.section.get('A', 1.0)
        Iy = element.section.get('Iy', 1.0)
        Iz = element.section.get('Iz', 1.0)
        J = element.section.get('J', 1.0)
        L = element.length
        
        # Local stiffness matrix for 3D frame element (12x12)
        K_local = np.zeros((12, 12))
        
        # Axial terms
        K_local[0, 0] = K_local[6, 6] = E * A / L
        K_local[0, 6] = K_local[6, 0] = -E * A / L
        
        # Torsional terms
        K_local[3, 3] = K_local[9, 9] = G * J / L
        K_local[3, 9] = K_local[9, 3] = -G * J / L
        
        # Bending terms (Y-axis)
        K_local[1, 1] = K_local[7, 7] = 12 * E * Iz / (L**3)
        K_local[1, 7] = K_local[7, 1] = -12 * E * Iz / (L**3)
        K_local[1, 5] = K_local[5, 1] = 6 * E * Iz / (L**2)
        K_local[1, 11] = K_local[11, 1] = 6 * E * Iz / (L**2)
        K_local[7, 5] = K_local[5, 7] = -6 * E * Iz / (L**2)
        K_local[7, 11] = K_local[11, 7] = -6 * E * Iz / (L**2)
        K_local[5, 5] = K_local[11, 11] = 4 * E * Iz / L
        K_local[5, 11] = K_local[11, 5] = 2 * E * Iz / L
        
        # Bending terms (Z-axis)
        K_local[2, 2] = K_local[8, 8] = 12 * E * Iy / (L**3)
        K_local[2, 8] = K_local[8, 2] = -12 * E * Iy / (L**3)
        K_local[2, 4] = K_local[4, 2] = -6 * E * Iy / (L**2)
        K_local[2, 10] = K_local[10, 2] = -6 * E * Iy / (L**2)
        K_local[8, 4] = K_local[4, 8] = 6 * E * Iy / (L**2)
        K_local[8, 10] = K_local[10, 8] = 6 * E * Iy / (L**2)
        K_local[4, 4] = K_local[10, 10] = 4 * E * Iy / L
        K_local[4, 10] = K_local[10, 4] = 2 * E * Iy / L
        
        # Transform to global coordinates
        T = self._get_transformation_matrix(element)
        K_global = T.T @ K_local @ T
        
        element.stiffness_matrix = K_global
        return K_global
    
    def _get_transformation_matrix(self, element: AnalysisElement) -> np.ndarray:
        """Get transformation matrix from local to global coordinates"""
        # 3x3 rotation matrix
        R = element.local_axes
        
        # 12x12 transformation matrix for 3D frame element
        T = np.zeros((12, 12))
        
        # Fill transformation matrix with rotation matrices
        for i in range(4):
            start_idx = i * 3
            end_idx = start_idx + 3
            T[start_idx:end_idx, start_idx:end_idx] = R
        
        return T
    
    def assemble_load_vector(self, load_case_id: str) -> np.ndarray:
        """
        Assemble global load vector for a specific load case
        
        Args:
            load_case_id: ID of the load case
            
        Returns:
            Global load vector for free DOFs
        """
        logger.info(f"Assembling load vector for load case {load_case_id}")
        
        F_global = np.zeros(self.total_dofs)
        
        load_case = self.load_cases.get(load_case_id)
        if not load_case:
            logger.warning(f"Load case {load_case_id} not found")
            return F_global
        
        # Process loads
        for load in load_case['loads']:
            load_type = load.get('type')
            
            if load_type == 'nodal':
                self._apply_nodal_load(F_global, load)
            elif load_type == 'element':
                self._apply_element_load(F_global, load)
            elif load_type == 'distributed':
                self._apply_distributed_load(F_global, load)
        
        return F_global
    
    def _apply_nodal_load(self, F_global: np.ndarray, load: Dict[str, Any]) -> None:
        """Apply nodal load to global load vector"""
        node_id = load.get('node_id')
        forces = load.get('forces', {})
        
        node = self.nodes.get(node_id)
        if not node:
            logger.warning(f"Node {node_id} not found for nodal load")
            return
        
        # Apply forces to corresponding DOFs
        dof_names = ['dx', 'dy', 'dz', 'rx', 'ry', 'rz']
        force_names = ['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']
        
        for i, (dof_name, force_name) in enumerate(zip(dof_names, force_names)):
            if force_name in forces:
                global_dof = node.dof_indices[i]
                if global_dof >= 0:  # Free DOF
                    F_global[global_dof] += forces[force_name]
    
    def _apply_element_load(self, F_global: np.ndarray, load: Dict[str, Any]) -> None:
        """Apply element load (converted to equivalent nodal loads)"""
        # Simplified implementation - would need more sophisticated load conversion
        pass
    
    def _apply_distributed_load(self, F_global: np.ndarray, load: Dict[str, Any]) -> None:
        """Apply distributed load (converted to equivalent nodal loads)"""
        # Simplified implementation - would need more sophisticated load conversion
        pass
    
    def solve_system(self, K: np.ndarray, F: np.ndarray) -> np.ndarray:
        """
        Solve the system of equations K * u = F
        
        Args:
            K: Global stiffness matrix
            F: Global load vector
            
        Returns:
            Displacement vector
        """
        logger.info("Solving system of equations...")
        
        try:
            # Check for singularity
            if np.linalg.cond(K) > 1e12:
                logger.warning("Stiffness matrix is ill-conditioned")
            
            # Solve using direct method
            displacements = np.linalg.solve(K, F)
            
            logger.info("System solved successfully")
            return displacements
            
        except np.linalg.LinAlgError as e:
            logger.error(f"Failed to solve system: {e}")
            raise
    
    def calculate_reactions(self, displacements: np.ndarray) -> np.ndarray:
        """Calculate reaction forces at supports"""
        logger.info("Calculating reaction forces...")
        
        # This would involve calculating forces at restrained DOFs
        # Simplified implementation
        reactions = np.zeros(len(self.restrained_dofs))
        
        return reactions
    
    def calculate_element_forces(self, displacements: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """Calculate internal forces in elements"""
        logger.info("Calculating element forces...")
        
        element_forces = {}
        
        for element in self.elements.values():
            # Get element displacements
            start_dofs = element.start_node.dof_indices
            end_dofs = element.end_node.dof_indices
            element_dofs = start_dofs + end_dofs
            
            # Extract element displacements
            u_element = np.zeros(12)
            for i, global_dof in enumerate(element_dofs):
                if global_dof >= 0:
                    u_element[i] = displacements[global_dof]
            
            # Transform to local coordinates
            T = self._get_transformation_matrix(element)
            u_local = T @ u_element
            
            # Calculate local forces
            K_local = self._calculate_local_stiffness(element)
            f_local = K_local @ u_local
            
            # Store results
            element_forces[element.id] = {
                'element_id': element.element_id,
                'axial': f_local[6] - f_local[0],  # Axial force
                'shear_y': f_local[7] - f_local[1],  # Shear force Y
                'shear_z': f_local[8] - f_local[2],  # Shear force Z
                'torsion': f_local[9] - f_local[3],  # Torsional moment
                'moment_y': f_local[10],  # Moment about Y
                'moment_z': f_local[11],  # Moment about Z
                'local_forces': f_local.tolist(),
                'local_displacements': u_local.tolist()
            }
        
        return element_forces
    
    def _calculate_local_stiffness(self, element: AnalysisElement) -> np.ndarray:
        """Calculate element stiffness matrix in local coordinates"""
        # Same as in _calculate_element_stiffness but without transformation
        E = element.material.get('E', 200000.0)
        G = element.material.get('G', 80000.0)
        A = element.section.get('A', 1.0)
        Iy = element.section.get('Iy', 1.0)
        Iz = element.section.get('Iz', 1.0)
        J = element.section.get('J', 1.0)
        L = element.length
        
        K_local = np.zeros((12, 12))
        
        # Fill local stiffness matrix (same as before)
        K_local[0, 0] = K_local[6, 6] = E * A / L
        K_local[0, 6] = K_local[6, 0] = -E * A / L
        
        K_local[3, 3] = K_local[9, 9] = G * J / L
        K_local[3, 9] = K_local[9, 3] = -G * J / L
        
        # Continue with other terms...
        
        return K_local
