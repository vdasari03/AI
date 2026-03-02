"""Data models for car damage assessment"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DentSeverity(str, Enum):
    """Enum for dent severity levels"""
    MINOR = "minor"  # Less than 1 inch
    MODERATE = "moderate"  # 1-3 inches
    SEVERE = "severe"  # More than 3 inches


class RepairType(str, Enum):
    """Enum for repair type"""
    REPAIRABLE = "repairable"
    REPLACEABLE = "replaceable"
    TOTAL_LOSS = "total_loss"


class DamageAssessment(BaseModel):
    """Damage assessment details"""
    location: str = Field(..., description="Location of damage on the vehicle")
    severity: DentSeverity = Field(..., description="Severity of the dent")
    estimated_size_inches: float = Field(..., description="Estimated size in inches")
    description: str = Field(..., description="Detailed description of damage")
    repair_type: RepairType = Field(..., description="Type of repair needed")
    repair_complexity: str = Field(default="medium", description="Complexity: simple, medium, complex")


class CostEstimate(BaseModel):
    """Cost estimation details"""
    labor_cost: float = Field(..., description="Labor cost in USD")
    materials_cost: float = Field(..., description="Materials cost in USD")
    paint_cost: float = Field(..., description="Paint cost in USD")
    total_estimated_cost: float = Field(..., description="Total estimated cost in USD")
    confidence_level: float = Field(default=0.85, description="Confidence level 0-1")


class InsuranceClaimDetails(BaseModel):
    """Insurance claim details"""
    claim_id: str = Field(..., description="Unique claim identifier")
    claim_type: str = Field(default="damage", description="Type of claim")
    is_covered: bool = Field(..., description="Whether claim is covered")
    deductible: float = Field(default=500, description="Insurance deductible")
    coverage_percentage: float = Field(default=0.80, description="Coverage percentage")
    estimated_payout: float = Field(..., description="Estimated insurance payout")
    notes: str = Field(default="", description="Additional notes")


class CarDamageAssessmentResult(BaseModel):
    """Complete assessment result"""
    image_id: str = Field(..., description="Unique image identifier")
    image_path: str = Field(..., description="Path to the image")
    timestamp: str = Field(..., description="Assessment timestamp")
    damages: List[DamageAssessment] = Field(..., description="List of damage assessments")
    cost_estimate: CostEstimate = Field(..., description="Cost estimation")
    insurance_claim: InsuranceClaimDetails = Field(..., description="Insurance claim details")
    summary: str = Field(..., description="Summary of assessment")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return self.dict()
