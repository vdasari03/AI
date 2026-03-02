"""Unit tests for insurance claimer module"""
import pytest

from src.insurance_claimer import InsuranceClaimer
from src.cost_estimator import CostEstimator
from src.models import (
    DamageAssessment,
    CostEstimate,
    DentSeverity,
    RepairType,
)


@pytest.fixture
def insurance_claimer():
    """Create InsuranceClaimer instance"""
    return InsuranceClaimer()


@pytest.fixture
def sample_damages():
    """Create sample damages"""
    return [
        DamageAssessment(
            location="front_bumper",
            severity=DentSeverity.MODERATE,
            estimated_size_inches=2.5,
            description="Moderate dent on front bumper",
            repair_type=RepairType.REPAIRABLE,
            repair_complexity="medium",
        )
    ]


@pytest.fixture
def sample_cost_estimate():
    """Create sample cost estimate"""
    return CostEstimate(
        labor_cost=225,
        materials_cost=150,
        paint_cost=200,
        total_estimated_cost=575,
        confidence_level=0.85,
    )


def test_insurance_claimer_initialization(insurance_claimer):
    """Test InsuranceClaimer initialization"""
    assert insurance_claimer.deductible == InsuranceClaimer.DEFAULT_DEDUCTIBLE
    assert insurance_claimer.coverage_percentage == InsuranceClaimer.DEFAULT_COVERAGE_PERCENTAGE


def test_process_claim(insurance_claimer, sample_damages, sample_cost_estimate):
    """Test claim processing"""
    claim = insurance_claimer.process_claim(sample_damages, sample_cost_estimate)
    
    assert claim.claim_id is not None
    assert claim.is_covered is True
    assert claim.deductible == 500
    assert claim.coverage_percentage == 0.80
    assert claim.estimated_payout > 0


def test_process_claim_with_deductible(insurance_claimer, sample_damages, sample_cost_estimate):
    """Test claim payout calculation with deductible"""
    claim = insurance_claimer.process_claim(sample_damages, sample_cost_estimate)
    
    # Expected: (575 - 500) * 0.80 = 60
    expected_payout = (sample_cost_estimate.total_estimated_cost - insurance_claimer.deductible) * insurance_claimer.coverage_percentage
    
    assert claim.estimated_payout == expected_payout


def test_process_claim_below_deductible(insurance_claimer, sample_damages):
    """Test claim with cost below deductible"""
    low_cost_estimate = CostEstimate(
        labor_cost=50,
        materials_cost=50,
        paint_cost=0,
        total_estimated_cost=100,
        confidence_level=1.0,
    )
    
    claim = insurance_claimer.process_claim(sample_damages, low_cost_estimate)
    
    # No payout since cost < deductible
    assert claim.estimated_payout == 0


def test_determine_claim_type_minor(insurance_claimer):
    """Test claim type determination for minor damage"""
    minor_estimate = CostEstimate(
        labor_cost=50, materials_cost=50, paint_cost=0, total_estimated_cost=100, confidence_level=1.0
    )
    
    claim_type = insurance_claimer._determine_claim_type([], minor_estimate)
    assert claim_type == "minor_damage"


def test_determine_claim_type_damage(insurance_claimer):
    """Test claim type determination for damage"""
    damage_estimate = CostEstimate(
        labor_cost=500,
        materials_cost=500,
        paint_cost=200,
        total_estimated_cost=1200,
        confidence_level=0.85,
    )
    
    claim_type = insurance_claimer._determine_claim_type([], damage_estimate)
    assert claim_type == "damage"


def test_determine_claim_type_major(insurance_claimer):
    """Test claim type determination for major damage"""
    major_estimate = CostEstimate(
        labor_cost=1000,
        materials_cost=1500,
        paint_cost=500,
        total_estimated_cost=3000,
        confidence_level=0.85,
    )
    
    claim_type = insurance_claimer._determine_claim_type([], major_estimate)
    assert claim_type == "major_damage"


def test_determine_claim_type_total_loss(insurance_claimer):
    """Test claim type determination for total loss"""
    total_loss_estimate = CostEstimate(
        labor_cost=2000,
        materials_cost=5000,
        paint_cost=1000,
        total_estimated_cost=12000,
        confidence_level=0.75,
    )
    
    damages = [
        DamageAssessment(
            location="roof",
            severity=DentSeverity.SEVERE,
            estimated_size_inches=5.0,
            description="Severe damage",
            repair_type=RepairType.TOTAL_LOSS,
            repair_complexity="very_high",
        )
    ]
    
    claim_type = insurance_claimer._determine_claim_type(damages, total_loss_estimate)
    assert claim_type == "total_loss"


def test_is_covered(insurance_claimer, sample_damages):
    """Test coverage determination"""
    assert insurance_claimer._is_covered(sample_damages) is True


def test_is_not_covered(insurance_claimer):
    """Test excluded damage types"""
    excluded_damages = [
        DamageAssessment(
            location="intentional_damage",
            severity=DentSeverity.MODERATE,
            estimated_size_inches=2.0,
            description="Intentional damage",
            repair_type=RepairType.REPAIRABLE,
            repair_complexity="medium",
        )
    ]
    
    assert insurance_claimer._is_covered(excluded_damages) is False
