"""Unit tests for cost estimation module"""
import pytest

from src.cost_estimator import CostEstimator
from src.models import DamageAssessment, DentSeverity, RepairType


@pytest.fixture
def cost_estimator():
    """Create CostEstimator instance"""
    return CostEstimator()


@pytest.fixture
def minor_damage():
    """Create a minor damage assessment"""
    return DamageAssessment(
        location="rear_fender",
        severity=DentSeverity.MINOR,
        estimated_size_inches=0.75,
        description="Small ding on rear fender",
        repair_type=RepairType.REPAIRABLE,
        repair_complexity="simple",
    )


@pytest.fixture
def moderate_damage():
    """Create a moderate damage assessment"""
    return DamageAssessment(
        location="front_bumper",
        severity=DentSeverity.MODERATE,
        estimated_size_inches=2.5,
        description="Moderate dent on front bumper",
        repair_type=RepairType.REPAIRABLE,
        repair_complexity="medium",
    )


@pytest.fixture
def severe_damage():
    """Create a severe damage assessment"""
    return DamageAssessment(
        location="door_panel",
        severity=DentSeverity.SEVERE,
        estimated_size_inches=4.5,
        description="Deep dent on door panel",
        repair_type=RepairType.REPLACEABLE,
        repair_complexity="high",
    )


def test_cost_estimator_initialization(cost_estimator):
    """Test CostEstimator initialization"""
    assert cost_estimator.labor_rate == CostEstimator.LABOR_RATE_PER_HOUR
    assert cost_estimator.paint_cost == CostEstimator.PAINT_COST_PER_PANEL


def test_estimate_minor_damage(cost_estimator, minor_damage):
    """Test cost estimation for minor damage"""
    estimate = cost_estimator.estimate([minor_damage])
    
    assert estimate.labor_cost > 0
    assert estimate.materials_cost > 0
    assert estimate.total_estimated_cost > 0
    assert estimate.confidence_level == 0.85


def test_estimate_moderate_damage(cost_estimator, moderate_damage):
    """Test cost estimation for moderate damage"""
    estimate = cost_estimator.estimate([moderate_damage])
    
    assert estimate.labor_cost > 0
    assert estimate.paint_cost > 0
    assert estimate.total_estimated_cost > 0


def test_estimate_severe_damage(cost_estimator, severe_damage):
    """Test cost estimation for severe damage"""
    estimate = cost_estimator.estimate([severe_damage])
    
    assert estimate.labor_cost > 0
    assert estimate.materials_cost > 0
    assert estimate.confidence_level == 0.75  # Lower confidence for severe


def test_estimate_multiple_damages(cost_estimator, minor_damage, moderate_damage, severe_damage):
    """Test cost estimation for multiple damages"""
    damages = [minor_damage, moderate_damage, severe_damage]
    estimate = cost_estimator.estimate(damages)
    
    assert estimate.labor_cost > 0
    assert estimate.total_estimated_cost > 0


def test_estimate_empty_damages(cost_estimator):
    """Test cost estimation with no damages"""
    estimate = cost_estimator.estimate([])
    
    assert estimate.labor_cost == 0
    assert estimate.materials_cost == 0
    assert estimate.paint_cost == 0
    assert estimate.total_estimated_cost == 0
    assert estimate.confidence_level == 1.0


def test_get_labor_hours_minor(cost_estimator):
    """Test labor hours for minor damage"""
    hours = cost_estimator._get_labor_hours(DentSeverity.MINOR)
    assert hours == CostEstimator.MINOR_REPAIR_HOURS


def test_get_labor_hours_moderate(cost_estimator):
    """Test labor hours for moderate damage"""
    hours = cost_estimator._get_labor_hours(DentSeverity.MODERATE)
    assert hours == CostEstimator.MODERATE_REPAIR_HOURS


def test_get_labor_hours_severe(cost_estimator):
    """Test labor hours for severe damage"""
    hours = cost_estimator._get_labor_hours(DentSeverity.SEVERE)
    assert hours == CostEstimator.SEVERE_REPAIR_HOURS


def test_cost_calculation_accuracy(cost_estimator, moderate_damage):
    """Test accuracy of cost calculation"""
    estimate = cost_estimator.estimate([moderate_damage])
    
    # Expected: 3 hours * 75 per hour labor = 225 + 150 materials + 200 paint = 575
    expected_labor = CostEstimator.MODERATE_REPAIR_HOURS * CostEstimator.LABOR_RATE_PER_HOUR
    
    assert estimate.labor_cost == expected_labor
