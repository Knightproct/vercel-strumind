"""
AISC 360 Steel Design Implementation
"""

import numpy as np
from typing import Dict, List, Any
import logging

from app.core.design.engine import DesignChecker
from app.schemas.design import DesignSettings, DesignCheckResult, ElementDesignResult, DesignCheckType

logger = logging.getLogger(__name__)

class AISCDesignChecker(DesignChecker):
    """
    AISC 360 Steel Design Checker
    
    Implements design checks according to AISC 360 specification:
    - Tension members
    - Compression members  
    - Flexural members
    - Combined loading
    - Shear design
    """
    
    def check_element(self, element_id: str, element_data: Dict[str, Any], 
                     settings: DesignSettings) -> ElementDesignResult:
        """Check element according to AISC 360"""
        
        # Get element properties
        material = self.get_material_properties(element_data['material_id'])
        section = self.get_section_properties(element_data['section_id'])
        forces = self.get_element_forces(element_id)
        
        # Initialize results
        design_checks = []
        recommendations = []
        
        # Extract key properties
        Fy = material.get('fy', 250.0)  # MPa
        Fu = material.get('fu', 400.0)  # MPa
        E = material.get('E', 200000.0)  # MPa
        
        A = section.get('A', 1.0)       # Area
        Zx = section.get('Zx', 1.0)     # Section modulus
        Zy = section.get('Zy', 1.0)     # Section modulus
        rx = section.get('rx', 1.0)     # Radius of gyration
        ry = section.get('ry', 1.0)     # Radius of gyration
        
        L = element_data.get('length', 1.0)  # Element length
        
        # Get effective length factors
        Kx = settings.effective_length_factors.get('Kx', 1.0)
        Ky = settings.effective_length_factors.get('Ky', 1.0)
        
        # Extract forces
        P = abs(forces.get('P', 0.0))    # Axial force
        Mx = abs(forces.get('Mx', 0.0))  # Moment about X
        My = abs(forces.get('My', 0.0))  # Moment about Y
        Vx = abs(forces.get('Vx', 0.0))  # Shear force
        Vy = abs(forces.get('Vy', 0.0))  # Shear force
        
        # Determine loading type
        is_tension = forces.get('P', 0.0) > 0
        is_compression = forces.get('P', 0.0) < 0
        has_moment = max(Mx, My) > 1e-6
        
        # Perform design checks based on loading
        if is_tension and not has_moment:
            # Pure tension
            design_checks.extend(self._check_tension(P, A, Fy, Fu, settings))
            
        elif is_compression and not has_moment:
            # Pure compression
            design_checks.extend(self._check_compression(P, A, Fy, E, L, Kx, Ky, rx, ry, settings))
            
        elif has_moment and abs(P) < 1e-6:
            # Pure flexure
            design_checks.extend(self._check_flexure(Mx, My, Zx, Zy, Fy, settings))
            
        else:
            # Combined loading
            design_checks.extend(self._check_combined(P, Mx, My, A, Zx, Zy, Fy, E, L, Kx, Ky, rx, ry, settings))
        
        # Shear checks
        if max(Vx, Vy) > 1e-6:
            design_checks.extend(self._check_shear(Vx, Vy, A, Fy, settings))
        
        # Determine overall status
        ratios = [check.ratio for check in design_checks]
        controlling_ratio = max(ratios) if ratios else 0.0
        controlling_check = None
        
        if ratios:
            max_idx = ratios.index(controlling_ratio)
            controlling_check = design_checks[max_idx].check_type
        
        overall_status = "PASS"
        if controlling_ratio > 1.0:
            overall_status = "FAIL"
            recommendations.append("Consider increasing section size")
        elif controlling_ratio > 0.9:
            overall_status = "WARNING"
            recommendations.append("Section utilization is high")
        
        return ElementDesignResult(
            element_id=element_id,
            element_type=element_data['type'],
            section_name=section.get('name', 'Unknown'),
            material_name=material.get('name', 'Unknown'),
            design_checks=design_checks,
            controlling_ratio=controlling_ratio,
            controlling_check=controlling_check,
            overall_status=overall_status,
            recommendations=recommendations
        )
    
    def _check_tension(self, P: float, A: float, Fy: float, Fu: float, 
                      settings: DesignSettings) -> List[DesignCheckResult]:
        """Check tension member according to AISC 360 Chapter D"""
        
        checks = []
        
        # Resistance factors
        phi_t = settings.resistance_factors.get('tension', 0.9)
        
        # Yielding of gross section (AISC 360 D2-1)
        Pn_yield = Fy * A
        Pr_yield = phi_t * Pn_yield
        
        check_yield = self.create_design_check(
            check_type=DesignCheckType.TENSION,
            demand=P,
            capacity=Pr_yield,
            equation="AISC 360 D2-1",
            details={
                'Pn': Pn_yield,
                'phi': phi_t,
                'limit_state': 'yielding_gross_section'
            }
        )
        checks.append(check_yield)
        
        # Rupture of net section (AISC 360 D2-2)
        # Simplified - assumes Ae = 0.85 * Ag for bolted connections
        Ae = 0.85 * A  # Effective net area
        Pn_rupture = Fu * Ae
        Pr_rupture = 0.75 * Pn_rupture  # phi = 0.75 for rupture
        
        check_rupture = self.create_design_check(
            check_type=DesignCheckType.TENSION,
            demand=P,
            capacity=Pr_rupture,
            equation="AISC 360 D2-2",
            details={
                'Pn': Pn_rupture,
                'phi': 0.75,
                'Ae': Ae,
                'limit_state': 'rupture_net_section'
            }
        )
        checks.append(check_rupture)
        
        return checks
    
    def _check_compression(self, P: float, A: float, Fy: float, E: float,
                          L: float, Kx: float, Ky: float, rx: float, ry: float,
                          settings: DesignSettings) -> List[DesignCheckResult]:
        """Check compression member according to AISC 360 Chapter E"""
        
        checks = []
        
        # Resistance factor
        phi_c = settings.resistance_factors.get('compression', 0.9)
        
        # Slenderness ratios
        KL_r_x = (Kx * L) / rx
        KL_r_y = (Ky * L) / ry
        KL_r = max(KL_r_x, KL_r_y)
        
        # Elastic buckling stress
        Fe = (np.pi**2 * E) / (KL_r**2)
        
        # Determine inelastic or elastic buckling
        lambda_c = np.sqrt(Fy / Fe)
        
        if lambda_c <= 1.5:
            # Inelastic buckling (AISC 360 E3-2)
            Fcr = (0.658**(lambda_c**2)) * Fy
        else:
            # Elastic buckling (AISC 360 E3-3)
            Fcr = 0.877 * Fe
        
        # Nominal compressive strength
        Pn = Fcr * A
        Pr = phi_c * Pn
        
        check_compression = self.create_design_check(
            check_type=DesignCheckType.COMPRESSION,
            demand=P,
            capacity=Pr,
            equation="AISC 360 E3",
            details={
                'Pn': Pn,
                'phi': phi_c,
                'Fcr': Fcr,
                'KL_r': KL_r,
                'lambda_c': lambda_c,
                'Fe': Fe,
                'buckling_mode': 'inelastic' if lambda_c <= 1.5 else 'elastic'
            }
        )
        checks.append(check_compression)
        
        return checks
    
    def _check_flexure(self, Mx: float, My: float, Zx: float, Zy: float,
                      Fy: float, settings: DesignSettings) -> List[DesignCheckResult]:
        """Check flexural member according to AISC 360 Chapter F"""
        
        checks = []
        
        # Resistance factor
        phi_b = settings.resistance_factors.get('flexure', 0.9)
        
        # Check moment about X-axis
        if Mx > 1e-6:
            # Simplified - assumes compact section
            Mn_x = Fy * Zx  # Plastic moment
            Mr_x = phi_b * Mn_x
            
            check_mx = self.create_design_check(
                check_type=DesignCheckType.FLEXURE,
                demand=Mx,
                capacity=Mr_x,
                equation="AISC 360 F2",
                details={
                    'Mn': Mn_x,
                    'phi': phi_b,
                    'axis': 'major',
                    'limit_state': 'yielding'
                }
            )
            checks.append(check_mx)
        
        # Check moment about Y-axis
        if My > 1e-6:
            Mn_y = Fy * Zy  # Plastic moment
            Mr_y = phi_b * Mn_y
            
            check_my = self.create_design_check(
                check_type=DesignCheckType.FLEXURE,
                demand=My,
                capacity=Mr_y,
                equation="AISC 360 F2",
                details={
                    'Mn': Mn_y,
                    'phi': phi_b,
                    'axis': 'minor',
                    'limit_state': 'yielding'
                }
            )
            checks.append(check_my)
        
        return checks
    
    def _check_combined(self, P: float, Mx: float, My: float, A: float,
                       Zx: float, Zy: float, Fy: float, E: float,
                       L: float, Kx: float, Ky: float, rx: float, ry: float,
                       settings: DesignSettings) -> List[DesignCheckResult]:
        """Check combined axial and flexural loading according to AISC 360 Chapter H"""
        
        checks = []
        
        # Get individual capacities
        if P > 0:  # Tension
            tension_checks = self._check_tension(P, A, Fy, 400.0, settings)  # Assume Fu = 400
            Pr = min(check.capacity for check in tension_checks)
        else:  # Compression
            compression_checks = self._check_compression(abs(P), A, Fy, E, L, Kx, Ky, rx, ry, settings)
            Pr = compression_checks[0].capacity if compression_checks else 0.0
        
        flexure_checks = self._check_flexure(Mx, My, Zx, Zy, Fy, settings)
        Mrx = flexure_checks[0].capacity if flexure_checks and Mx > 1e-6 else float('inf')
        Mry = flexure_checks[1].capacity if len(flexure_checks) > 1 and My > 1e-6 else float('inf')
        
        # Combined loading check
        if abs(P) / Pr >= 0.2:
            # AISC 360 H1-1a
            ratio = abs(P) / Pr + (8.0/9.0) * (Mx / Mrx + My / Mry)
            equation = "AISC 360 H1-1a"
        else:
            # AISC 360 H1-1b
            ratio = abs(P) / (2.0 * Pr) + (Mx / Mrx + My / Mry)
            equation = "AISC 360 H1-1b"
        
        # Create equivalent demand and capacity for ratio
        demand = ratio
        capacity = 1.0
        
        check_combined = self.create_design_check(
            check_type=DesignCheckType.COMBINED,
            demand=demand,
            capacity=capacity,
            equation=equation,
            details={
                'P': P,
                'Pr': Pr,
                'Mx': Mx,
                'Mrx': Mrx,
                'My': My,
                'Mry': Mry,
                'P_Pr': abs(P) / Pr if Pr > 0 else 0,
                'Mx_Mrx': Mx / Mrx if Mrx > 0 else 0,
                'My_Mry': My / Mry if Mry > 0 else 0
            }
        )
        checks.append(check_combined)
        
        return checks
    
    def _check_shear(self, Vx: float, Vy: float, A: float, Fy: float,
                    settings: DesignSettings) -> List[DesignCheckResult]:
        """Check shear according to AISC 360 Chapter G"""
        
        checks = []
        
        # Resistance factor
        phi_v = settings.resistance_factors.get('shear', 0.9)
        
        # Simplified shear check - assumes web controls
        # For more detailed check, would need web dimensions
        Cv = 1.0  # Web shear coefficient (simplified)
        Vn = 0.6 * Fy * A * Cv  # Nominal shear strength
        Vr = phi_v * Vn
        
        # Check resultant shear
        V_resultant = np.sqrt(Vx**2 + Vy**2)
        
        if V_resultant > 1e-6:
            check_shear = self.create_design_check(
                check_type=DesignCheckType.SHEAR,
                demand=V_resultant,
                capacity=Vr,
                equation="AISC 360 G2",
                details={
                    'Vn': Vn,
                    'phi': phi_v,
                    'Cv': Cv,
                    'Vx': Vx,
                    'Vy': Vy
                }
            )
            checks.append(check_shear)
        
        return checks
