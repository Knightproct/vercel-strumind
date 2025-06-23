"""
Seed database with common structural materials
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from sqlalchemy.orm import sessionmaker
from app.db.database import engine
from app.models.project import Material
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_materials():
    """Seed database with common structural materials"""
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Steel materials
        steel_materials = [
            {
                'name': 'A992 Grade 50',
                'material_type': 'steel',
                'elastic_modulus': 200000.0,  # MPa
                'shear_modulus': 80000.0,     # MPa
                'poisson_ratio': 0.3,
                'density': 7850.0,            # kg/m³
                'yield_strength': 345.0,      # MPa
                'ultimate_strength': 450.0,   # MPa
                'properties': {
                    'grade': 'A992',
                    'specification': 'ASTM A992',
                    'type': 'structural_steel'
                }
            },
            {
                'name': 'A36',
                'material_type': 'steel',
                'elastic_modulus': 200000.0,
                'shear_modulus': 80000.0,
                'poisson_ratio': 0.3,
                'density': 7850.0,
                'yield_strength': 250.0,
                'ultimate_strength': 400.0,
                'properties': {
                    'grade': 'A36',
                    'specification': 'ASTM A36',
                    'type': 'structural_steel'
                }
            },
            {
                'name': 'A572 Grade 50',
                'material_type': 'steel',
                'elastic_modulus': 200000.0,
                'shear_modulus': 80000.0,
                'poisson_ratio': 0.3,
                'density': 7850.0,
                'yield_strength': 345.0,
                'ultimate_strength': 450.0,
                'properties': {
                    'grade': 'A572',
                    'specification': 'ASTM A572',
                    'type': 'high_strength_steel'
                }
            }
        ]
        
        # Concrete materials
        concrete_materials = [
            {
                'name': 'Normal Weight Concrete f\'c = 25 MPa',
                'material_type': 'concrete',
                'elastic_modulus': 25000.0,   # MPa
                'shear_modulus': 10400.0,     # MPa
                'poisson_ratio': 0.2,
                'density': 2400.0,            # kg/m³
                'compressive_strength': 25.0, # MPa
                'properties': {
                    'fc_prime': 25.0,
