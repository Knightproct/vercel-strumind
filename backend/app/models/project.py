"""
Project and structural model database models
"""

from sqlalchemy import Column, String, Text, ForeignKey, JSON, Float, Integer, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Project(BaseModel):
    """Project model"""
    __tablename__ = "projects"
    
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_type = Column(String, default="building")  # building, bridge, industrial
    units = Column(String, default="metric")  # metric, imperial
    design_code = Column(String, default="AISC")  # AISC, EC3, etc.
    
    # Project settings
    settings = Column(JSON, default={})
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    structural_models = relationship("StructuralModel", back_populates="project")

class StructuralModel(BaseModel):
    """Structural model containing nodes, elements, etc."""
    __tablename__ = "structural_models"
    
    name = Column(String, nullable=False)
    description = Column(Text)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # Model properties
    model_type = Column(String, default="3d_frame")  # 3d_frame, 2d_frame, truss, shell
    analysis_type = Column(String, default="linear")  # linear, nonlinear, dynamic
    
    # Model data (JSON storage for flexibility)
    geometry_data = Column(JSON, default={})
    analysis_settings = Column(JSON, default={})
    
    # Relationships
    project = relationship("Project", back_populates="structural_models")
    nodes = relationship("Node", back_populates="model")
    elements = relationship("Element", back_populates="model")
    materials = relationship("Material", back_populates="model")
    sections = relationship("Section", back_populates="model")
    load_cases = relationship("LoadCase", back_populates="model")
    analysis_results = relationship("AnalysisResult", back_populates="model")

class Node(BaseModel):
    """Structural node/joint"""
    __tablename__ = "nodes"
    
    model_id = Column(String, ForeignKey("structural_models.id"), nullable=False)
    node_id = Column(Integer, nullable=False)  # User-defined node number
    
    # Coordinates
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    
    # Boundary conditions
    restraints = Column(JSON, default={})  # {dx: True, dy: False, ...}
    
    # Properties
    properties = Column(JSON, default={})
    
    # Relationships
    model = relationship("StructuralModel", back_populates="nodes")

class Element(BaseModel):
    """Structural element (beam, column, brace, etc.)"""
    __tablename__ = "elements"
    
    model_id = Column(String, ForeignKey("structural_models.id"), nullable=False)
    element_id = Column(Integer, nullable=False)  # User-defined element number
    
    # Connectivity
    start_node_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    end_node_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    
    # Element type
    element_type = Column(String, nullable=False)  # beam, column, brace, shell, etc.
    
    # Material and section
    material_id = Column(String, ForeignKey("materials.id"))
    section_id = Column(String, ForeignKey("sections.id"))
    
    # Element properties
    properties = Column(JSON, default={})
    
    # Local coordinate system
    orientation = Column(JSON, default={})
    
    # Relationships
    model = relationship("StructuralModel", back_populates="elements")
    material = relationship("Material")
    section = relationship("Section")
    start_node = relationship("Node", foreign_keys=[start_node_id])
    end_node = relationship("Node", foreign_keys=[end_node_id])

class Material(BaseModel):
    """Material properties"""
    __tablename__ = "materials"
    
    model_id = Column(String, ForeignKey("structural_models.id"), nullable=False)
    name = Column(String, nullable=False)
    material_type = Column(String, nullable=False)  # steel, concrete, composite, etc.
    
    # Mechanical properties
    elastic_modulus = Column(Float)  # E
    shear_modulus = Column(Float)   # G
    poisson_ratio = Column(Float)   # ν
    density = Column(Float)         # ρ
    
    # Strength properties
    yield_strength = Column(Float)   # Fy
    ultimate_strength = Column(Float) # Fu
    compressive_strength = Column(Float) # f'c (concrete)
    
    # Additional properties
    properties = Column(JSON, default={})
    
    # Relationships
    model = relationship("StructuralModel", back_populates="materials")

class Section(BaseModel):
    """Cross-section properties"""
    __tablename__ = "sections"
    
    model_id = Column(String, ForeignKey("structural_models.id"), nullable=False)
    name = Column(String, nullable=False)
    section_type = Column(String, nullable=False)  # I-beam, HSS, angle, etc.
    
    # Geometric properties
    area = Column(Float)           # A
    moment_inertia_y = Column(Float) # Iy
    moment_inertia_z = Column(Float) # Iz
    torsional_constant = Column(Float) # J
    section_modulus_y = Column(Float) # Sy
    section_modulus_z = Column(Float) # Sz
    
    # Dimensions (varies by section type)
    dimensions = Column(JSON, default={})
    
    # Additional properties
    properties = Column(JSON, default={})
    
    # Relationships
    model = relationship("StructuralModel", back_populates="sections")

class LoadCase(BaseModel):
    """Load case definition"""
    __tablename__ = "load_cases"
    
    model_id = Column(String, ForeignKey("structural_models.id"), nullable=False)
    name = Column(String, nullable=False)
    load_type = Column(String, nullable=False)  # dead, live, wind, seismic, etc.
    
    # Load data
    loads = Column(JSON, default=[])  # Array of load definitions
    
    # Load case properties
    properties = Column(JSON, default={})
    
    # Relationships
    model = relationship("StructuralModel", back_populates="load_cases")

class AnalysisResult(BaseModel):
    """Analysis results storage"""
    __tablename__ = "analysis_results"
    
    model_id = Column(String, ForeignKey("structural_models.id"), nullable=False)
    analysis_type = Column(String, nullable=False)
    load_case_id = Column(String, ForeignKey("load_cases.id"))
    
    # Results data
    node_results = Column(JSON, default={})     # Displacements, reactions
    element_results = Column(JSON, default={})  # Forces, moments, stresses
    
    # Analysis metadata
    analysis_time = Column(Float)
    convergence_info = Column(JSON, default={})
    
    # Relationships
    model = relationship("StructuralModel", back_populates="analysis_results")
    load_case = relationship("LoadCase")
