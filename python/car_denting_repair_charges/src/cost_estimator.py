"""Cost estimation module"""
import logging
from typing import List, Dict, Any
from src.models import DamageAssessment, CostEstimate, DentSeverity, RepairType

logger = logging.getLogger(__name__)


class CostEstimator:
    """Calculate repair costs based on damage assessment"""
    
    # Base costs in USD
    LABOR_RATE_PER_HOUR = 75
    PAINT_COST_PER_PANEL = 200
    MINOR_REPAIR_HOURS = 1.0
    MODERATE_REPAIR_HOURS = 3.0
    SEVERE_REPAIR_HOURS = 6.0
    
    # Material costs based on severity
    SEVERITY_MATERIAL_COSTS = {
        DentSeverity.MINOR: 50,
        DentSeverity.MODERATE: 150,
        DentSeverity.SEVERE: 350,
    }
    
    # Panel replacement costs (if needed)
    PANEL_REPLACEMENT_COSTS = {
        "front_bumper": 300,
        "rear_bumper": 280,
        "door_panel": 450,
        "hood": 400,
        "trunk": 350,
        "roof": 600,
        "fender": 350,
        "hood": 400,
    }
    
    def __init__(self, labor_rate: float = LABOR_RATE_PER_HOUR, paint_cost: float = PAINT_COST_PER_PANEL):
        """Initialize cost estimator
        
        Args:
            labor_rate: Labor rate per hour in USD
            paint_cost: Paint cost per panel in USD
        """
        self.labor_rate = labor_rate
        self.paint_cost = paint_cost
    
    def estimate(self, damages: List[DamageAssessment]) -> CostEstimate:
        """Estimate total repair cost
        
        Args:
            damages: List of damage assessments
            
        Returns:
            CostEstimate object
        """
        if not damages:
            return CostEstimate(
                labor_cost=0,
                materials_cost=0,
                paint_cost=0,
                total_estimated_cost=0,
                confidence_level=1.0,
            )
        
        total_labor_cost = 0
        total_materials_cost = 0
        total_paint_cost = 0
        
        for damage in damages:
            # Calculate labor cost
            labor_hours = self._get_labor_hours(damage.severity)
            damage_labor_cost = labor_hours * self.labor_rate
            total_labor_cost += damage_labor_cost
            
            # Calculate materials cost
            damage_materials_cost = self.SEVERITY_MATERIAL_COSTS.get(damage.severity, 100)
            if damage.repair_type == RepairType.REPLACEABLE:
                replacement_cost = self.PANEL_REPLACEMENT_COSTS.get(damage.location, 300)
                damage_materials_cost = replacement_cost
            total_materials_cost += damage_materials_cost
            
            # Calculate paint cost
            damage_paint_cost = self.paint_cost if damage.severity in [
                DentSeverity.MODERATE,
                DentSeverity.SEVERE
            ] else 0
            total_paint_cost += damage_paint_cost
        
        total_cost = total_labor_cost + total_materials_cost + total_paint_cost
        
        # Slightly reduce confidence for severe damage
        confidence = 0.85
        if any(d.severity == DentSeverity.SEVERE for d in damages):
            confidence = 0.75
        
        logger.info(f"Cost estimate calculated: ${total_cost:.2f}")
        
        return CostEstimate(
            labor_cost=round(total_labor_cost, 2),
            materials_cost=round(total_materials_cost, 2),
            paint_cost=round(total_paint_cost, 2),
            total_estimated_cost=round(total_cost, 2),
            confidence_level=confidence,
        )
    
    def _get_labor_hours(self, severity: DentSeverity) -> float:
        """Get labor hours based on severity
        
        Args:
            severity: Damage severity level
            
        Returns:
            Number of labor hours
        """
        switch = {
            DentSeverity.MINOR: self.MINOR_REPAIR_HOURS,
            DentSeverity.MODERATE: self.MODERATE_REPAIR_HOURS,
            DentSeverity.SEVERE: self.SEVERE_REPAIR_HOURS,
        }
        return switch.get(severity, self.MINOR_REPAIR_HOURS)
