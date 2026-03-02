"""Unit tests for LLM integration module"""
import pytest
from unittest.mock import Mock, patch

from src.llm_integration import (
    BaseLLMProvider,
    MockLLMProvider,
    LLMAnalyzer,
)


@pytest.fixture
def mock_provider():
    """Create MockLLMProvider instance"""
    return MockLLMProvider()


@pytest.fixture
def llm_analyzer(mock_provider):
    """Create LLMAnalyzer with mock provider"""
    return LLMAnalyzer(mock_provider)


def test_mock_llm_provider_initialization(mock_provider):
    """Test MockLLMProvider initialization"""
    assert mock_provider.call_count == 0
    assert len(mock_provider.mock_responses) == 5


def test_mock_llm_provider_analyze_response_rotation(mock_provider):
    """Test that mock provider rotates through responses"""
    response1 = mock_provider.analyze_image("image1.jpg", "prompt")
    assert "damages" in response1
    assert mock_provider.call_count == 1
    
    response2 = mock_provider.analyze_image("image2.jpg", "prompt")
    assert "damages" in response2
    assert mock_provider.call_count == 2


def test_llm_analyzer_initialization(llm_analyzer):
    """Test LLMAnalyzer initialization"""
    assert llm_analyzer.provider is not None
    assert llm_analyzer.ANALYSIS_PROMPT is not None


def test_llm_analyzer_analyze(llm_analyzer):
    """Test LLMAnalyzer analyze method"""
    result = llm_analyzer.analyze("test_image.jpg")
    
    assert result is not None
    assert isinstance(result, dict)
    assert "damages" in result


def test_llm_analyzer_analyze_with_custom_prompt(llm_analyzer):
    """Test LLMAnalyzer with custom prompt"""
    custom_prompt = "Custom analysis prompt"
    result = llm_analyzer.analyze("test_image.jpg", custom_prompt)
    
    assert result is not None


def test_mock_llm_provider_default_responses():
    """Test default mock responses"""
    provider = MockLLMProvider()
    
    assert "response_0" in provider.mock_responses
    assert "response_1" in provider.mock_responses
    assert "response_2" in provider.mock_responses
    assert "response_3" in provider.mock_responses
    assert "response_4" in provider.mock_responses


def test_mock_responses_structure():
    """Test structure of mock responses"""
    provider = MockLLMProvider()
    
    for key, response in provider.mock_responses.items():
        assert "damages" in response
        assert isinstance(response["damages"], list)
        
        for damage in response["damages"]:
            assert "location" in damage
            assert "severity" in damage
            assert "estimated_size_inches" in damage
            assert "description" in damage
            assert "repair_type" in damage
            assert "repair_complexity" in damage
