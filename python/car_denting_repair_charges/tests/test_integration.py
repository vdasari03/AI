"""Integration tests for the complete application"""
import pytest
import tempfile
import os
import json

from src.app import CarDamageAssessmentApp
from src.formatters import JSONFormatter
from tests.mocks.utils import save_mock_image


@pytest.fixture
def app():
    """Create application instance"""
    return CarDamageAssessmentApp(use_mock_llm=True)


@pytest.fixture
def test_images():
    """Create temporary test images"""
    with tempfile.TemporaryDirectory() as tmpdir:
        image_paths = []
        for i in range(5):
            image_path = os.path.join(tmpdir, f"car_damage_{i+1}.jpg")
            save_mock_image(image_path, 800, 600)
            image_paths.append(image_path)
        
        yield image_paths


def test_app_initialization():
    """Test application initialization"""
    app = CarDamageAssessmentApp(use_mock_llm=True)
    assert app is not None
    assert app.image_processor is not None
    assert app.llm_analyzer is not None
    assert app.cost_estimator is not None
    assert app.insurance_claimer is not None


def test_assess_single_image(app, test_images):
    """Test assessing a single image"""
    result = app.assess_damage(test_images[0])
    
    assert result is not None
    assert result.image_id is not None
    assert result.image_path is not None
    assert result.timestamp is not None
    assert result.damages is not None
    assert result.cost_estimate is not None
    assert result.insurance_claim is not None
    assert result.summary is not None


def test_assess_multiple_images(app, test_images):
    """Test assessing multiple images"""
    results = app.assess_multiple(test_images)
    
    assert len(results) == len(test_images)
    
    for result in results:
        assert result.image_id is not None
        assert result.cost_estimate.total_estimated_cost >= 0
        assert result.insurance_claim.estimated_payout >= 0


def test_json_formatting(app, test_images):
    """Test JSON formatting of results"""
    result = app.assess_damage(test_images[0])
    
    json_data = JSONFormatter.format_result(result)
    
    assert isinstance(json_data, dict)
    assert "image_id" in json_data
    assert "cost_estimate" in json_data
    assert "insurance_claim" in json_data


def test_json_formatting_multiple(app, test_images):
    """Test JSON formatting of multiple results"""
    results = app.assess_multiple(test_images)
    
    json_data = JSONFormatter.format_results(results)
    
    assert "total_assessments" in json_data
    assert json_data["total_assessments"] == len(test_images)
    assert "results" in json_data
    assert "summary" in json_data


def test_json_save_and_load(app, test_images):
    """Test saving and loading JSON results"""
    results = app.assess_multiple(test_images)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "results.json")
        
        # Save
        success = JSONFormatter.save_to_file(results, output_path)
        assert success is True
        assert os.path.exists(output_path)
        
        # Load
        loaded_data = JSONFormatter.load_from_file(output_path)
        assert loaded_data is not None
        assert loaded_data["total_assessments"] == len(test_images)


def test_assessment_result_json_conversion(app, test_images):
    """Test that assessment result can be converted to JSON"""
    result = app.assess_damage(test_images[0])
    json_data = result.to_json()
    
    # Should be JSON serializable
    json_str = json.dumps(json_data)
    assert json_str is not None
    assert len(json_str) > 0


def test_summary_generation(app, test_images):
    """Test summary generation"""
    result = app.assess_damage(test_images[0])
    
    summary = result.summary
    assert summary is not None
    assert len(summary) > 0
    assert "Assessment" in summary or "No significant" in summary


def test_multiple_images_summary(app, test_images):
    """Test summary for multiple assessments"""
    results = app.assess_multiple(test_images)
    json_data = JSONFormatter.format_results(results)
    
    summary = json_data["summary"]
    assert "total_cost" in summary
    assert "total_insurance_payout" in summary
    assert "average_confidence" in summary
