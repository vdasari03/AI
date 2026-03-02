"""LLM integration for damage analysis"""
import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze image and return assessment"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 Vision provider"""
    
    def __init__(self, api_key: str):
        """Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        try:
            import openai
            openai.api_key = api_key
            self.client = openai
        except ImportError:
            logger.warning("OpenAI library not installed")
            self.client = None
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze car damage image using GPT-4 Vision
        
        Args:
            image_path: Path to image file
            prompt: Prompt for analysis
            
        Returns:
            Analysis response from OpenAI
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        # Implementation would use openai.ChatCompletion.create with vision_prompt
        # For actual implementation, include base64 image encoding
        raise NotImplementedError("Real OpenAI implementation requires API credentialscals")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str):
        """Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logger.warning("Anthropic library not installed")
            self.client = None
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze car damage image using Claude
        
        Args:
            image_path: Path to image file
            prompt: Prompt for analysis
            
        Returns:
            Analysis response from Claude
        """
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")
        
        # Implementation would use claude-3-vision model
        raise NotImplementedError("Real Anthropic implementation requires API credentials")


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing"""
    
    def __init__(self, mock_responses: Optional[Dict[str, Any]] = None):
        """Initialize mock provider
        
        Args:
            mock_responses: Dictionary of mock responses
        """
        self.mock_responses = mock_responses or self._get_default_responses()
        self.call_count = 0
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Return mock response
        
        Args:
            image_path: Path to image file
            prompt: Prompt for analysis (not used in mock)
            
        Returns:
            Mock analysis response
        """
        self.call_count += 1
        
        # Rotate through mock responses
        response_key = f"response_{self.call_count % len(self.mock_responses)}"
        return self.mock_responses.get(response_key, self.mock_responses["response_0"])
    
    def _get_default_responses(self) -> Dict[str, Any]:
        """Get default mock responses"""
        return {
            "response_0": {
                "damages": [
                    {
                        "location": "front_bumper",
                        "severity": "moderate",
                        "estimated_size_inches": 2.5,
                        "description": "Moderate dent on front bumper with minor paint damage",
                        "repair_type": "repairable",
                        "repair_complexity": "medium",
                    }
                ],
                "additional_notes": "No structural damage detected",
            },
            "response_1": {
                "damages": [
                    {
                        "location": "door_panel",
                        "severity": "severe",
                        "estimated_size_inches": 4.0,
                        "description": "Deep dent on driver-side door with paint damage",
                        "repair_type": "replaceable",
                        "repair_complexity": "high",
                    }
                ],
                "additional_notes": "Recommend door replacement",
            },
            "response_2": {
                "damages": [
                    {
                        "location": "rear_fender",
                        "severity": "minor",
                        "estimated_size_inches": 0.75,
                        "description": "Small ding on rear fender",
                        "repair_type": "repairable",
                        "repair_complexity": "simple",
                    }
                ],
                "additional_notes": "Simple dent pull repair",
            },
            "response_3": {
                "damages": [
                    {
                        "location": "hood",
                        "severity": "moderate",
                        "estimated_size_inches": 3.0,
                        "description": "Multiple dents on hood with paint cracking",
                        "repair_type": "repairable",
                        "repair_complexity": "medium",
                    }
                ],
                "additional_notes": "Repaint required",
            },
            "response_4": {
                "damages": [
                    {
                        "location": "roof",
                        "severity": "severe",
                        "estimated_size_inches": 5.0,
                        "description": "Large dent on roof with structural concerns",
                        "repair_type": "total_loss",
                        "repair_complexity": "very_high",
                    }
                ],
                "additional_notes": "Vehicle may be total loss",
            },
        }


class LLMAnalyzer:
    """Orchestrator for LLM-based damage analysis"""
    
    ANALYSIS_PROMPT = """Analyze the car damage in this image and provide:
1. Location of damage (e.g., front_bumper, door_panel, hood)
2. Severity level (minor, moderate, severe)
3. Estimated size in inches
4. Detailed description
5. Repair type (repairable, replaceable, total_loss)
6. Repair complexity (simple, medium, complex, very_high)

Return response as valid JSON."""
    
    def __init__(self, provider: BaseLLMProvider):
        """Initialize analyzer with provider
        
        Args:
            provider: LLM provider instance
        """
        self.provider = provider
    
    def analyze(self, image_path: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze image using LLM provider
        
        Args:
            image_path: Path to image file
            custom_prompt: Optional custom prompt
            
        Returns:
            Analysis results
        """
        prompt = custom_prompt or self.ANALYSIS_PROMPT
        
        logger.info(f"Analyzing image: {image_path}")
        result = self.provider.analyze_image(image_path, prompt)
        logger.info(f"Analysis complete for: {image_path}")
        
        return result
