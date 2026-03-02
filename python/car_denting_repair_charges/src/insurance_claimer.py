"""Insurance claim processing module"""
import logging
import uuid
from typing import List, Dict, Any
from datetime import datetime
from src.models import (
    DamageAssessment,
    CostEstimate,
    InsuranceClaimDetails,
    RepairType,
)

logger = logging.getLogger(__name__)


class InsuranceClaimer:
    """Process insurance claims for car damage"""
    
    DEFAULT_DEDUCTIBLE = 500
    DEFAULT_COVERAGE_PERCENTAGE = 0.80
    TOTAL_LOSS_THRESHOLD = 10000  # Vehicle is total loss if repair cost exceeds this
    
    def __init__(
        self,
        deductible: float = DEFAULT_DEDUCTIBLE,
        coverage_percentage: float = DEFAULT_COVERAGE_PERCENTAGE,
    ):
        """Initialize insurance claimer
        
        Args:
            deductible: Insurance deductible in USD
            coverage_percentage: Coverage percentage (0-1)
        """
        self.deductible = deductible
        self.coverage_percentage = coverage_percentage
    
    def process_claim(
        self,
        damages: List[DamageAssessment],
        cost_estimate: CostEstimate,
    ) -> InsuranceClaimDetails:
        """Process insurance claim
        
        Args:
            damages: List of damage assessments
            cost_estimate: Cost estimate for repairs
            
        Returns:
            InsuranceClaimDetails object
        """
        claim_id = str(uuid.uuid4())[:8].upper()
        
        # Check if damage is covered
        is_covered = self._is_covered(damages)
        
        # Calculate payout
        payout = 0
        if is_covered:
            # Apply deductible
            cost_after_deductible = max(0, cost_estimate.total_estimated_cost - self.deductible)
            # Apply coverage percentage
            payout = cost_after_deductible * self.coverage_percentage
        
        # Determine claim type
        claim_type = self._determine_claim_type(damages, cost_estimate)
        
        logger.info(f"Claim processed: {claim_id}, Payout: ${payout:.2f}")
        
        return InsuranceClaimDetails(
            claim_id=claim_id,
            claim_type=claim_type,
            is_covered=is_covered,
            deductible=self.deductible,
            coverage_percentage=self.coverage_percentage,
            estimated_payout=round(payout, 2),
            notes=self._generate_claim_notes(damages, cost_estimate, is_covered),
        )
    
    def _is_covered(self, damages: List[DamageAssessment]) -> bool:
        """Determine if claim is covered
        
        Args:
            damages: List of damage assessments
            
        Returns:
            True if covered, False otherwise
        """
        # Exclude certain types of damage
        excluded_locations = ["intentional_damage", "wear_and_tear"]
        
        for damage in damages:
            if damage.location.lower() in excluded_locations:
                return False
        
        return True
    
    def _determine_claim_type(
        self, damages: List[DamageAssessment], cost_estimate: CostEstimate
    ) -> str:
        """Determine type of claim
        
        Args:
            damages: List of damage assessments
            cost_estimate: Cost estimate
            
        Returns:
            Claim type as string
        """
        # Check for total loss
        if (
            cost_estimate.total_estimated_cost > self.TOTAL_LOSS_THRESHOLD
            or any(d.repair_type == RepairType.TOTAL_LOSS for d in damages)
        ):
            return "total_loss"
        
        # Check for major claim
        if cost_estimate.total_estimated_cost > 2000:
            return "major_damage"
        
        # Check for minor claim
        if cost_estimate.total_estimated_cost > 500:
            return "damage"
        
        return "minor_damage"
    
    def _generate_claim_notes(
        self,
        damages: List[DamageAssessment],
        cost_estimate: CostEstimate,
        is_covered: bool,
    ) -> str:
        """Generate claim notes
        
        Args:
            damages: List of damage assessments
            cost_estimate: Cost estimate
            is_covered: Whether claim is covered
            
        Returns:
            Notes as string
        """
        notes = []
        
        if not is_covered:
            notes.append("Claim not covered under policy.")
        
        # Add damage summary
        damage_locations = [d.location for d in damages]
        notes.append(f"Damage locations: {', '.join(damage_locations)}")
        
        # Add cost breakdown
        notes.append(
            f"Labor: ${cost_estimate.labor_cost:.2f}, "
            f"Materials: ${cost_estimate.materials_cost:.2f}, "
            f"Paint: ${cost_estimate.paint_cost:.2f}"
        )
        
        # Add approval notes
        if any(d.repair_type == RepairType.REPLACEABLE for d in damages):
            notes.append("Component replacement recommended.")
        
        return " | ".join(notes)
