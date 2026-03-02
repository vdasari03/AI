"""Main application orchestrator"""
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.models import (
    CarDamageAssessmentResult,
    DamageAssessment,
)
from src.image_processor import ImageProcessor
from src.llm_integration import LLMAnalyzer, MockLLMProvider
from src.cost_estimator import CostEstimator
from src.insurance_claimer import InsuranceClaimer

logger = logging.getLogger(__name__)


class CarDamageAssessmentApp:
    """Main application for car damage assessment"""
    
    def __init__(
        self,
        use_mock_llm: bool = True,
        labor_rate: float = 75,
        paint_cost: float = 200,
    ):
        """Initialize application
        
        Args:
            use_mock_llm: Use mock LLM provider
            labor_rate: Labor rate per hour
            paint_cost: Paint cost per panel
        """
        self.image_processor = ImageProcessor()
        
        # Initialize LLM provider
        if use_mock_llm:
            llm_provider = MockLLMProvider()
        else:
            raise ValueError("Real LLM providers require API keys")
        
        self.llm_analyzer = LLMAnalyzer(llm_provider)
        self.cost_estimator = CostEstimator(labor_rate, paint_cost)
        self.insurance_claimer = InsuranceClaimer()
    
    def assess_damage(self, image_path: str) -> Optional[CarDamageAssessmentResult]:
        """Assess car damage from image
        
        Args:
            image_path: Path to car image
            
        Returns:
            CarDamageAssessmentResult or None if assessment fails
        """
        logger.info(f"Starting damage assessment for: {image_path}")
        
        # Load and validate image
        image = self.image_processor.load_image(image_path)
        if not image:
            logger.error(f"Failed to load image: {image_path}")
            return None
        
        # Analyze image with LLM
        analysis_result = self.llm_analyzer.analyze(image_path)
        if not analysis_result:
            logger.error(f"LLM analysis failed for: {image_path}")
            return None
        
        # Parse damages from analysis
        damages = self._parse_damages(analysis_result)
        if not damages:
            logger.warning(f"No damages detected in: {image_path}")
            damages = []
        
        # Estimate costs
        cost_estimate = self.cost_estimator.estimate(damages)
        
        # Process insurance claim
        insurance_claim = self.insurance_claimer.process_claim(damages, cost_estimate)
        
        # Create result
        result = CarDamageAssessmentResult(
            image_id=Path(image_path).stem,
            image_path=image_path,
            timestamp=datetime.now().isoformat(),
            damages=damages,
            cost_estimate=cost_estimate,
            insurance_claim=insurance_claim,
            summary=self._generate_summary(damages, cost_estimate, insurance_claim),
            metadata=self.image_processor.get_image_metadata(image),
        )
        
        logger.info(f"Assessment complete for: {image_path}")
        return result
    
    def assess_multiple(self, image_paths: List[str]) -> List[CarDamageAssessmentResult]:
        """Assess multiple images
        
        Args:
            image_paths: List of image paths
            
        Returns:
            List of assessment results
        """
        results = []
        for image_path in image_paths:
            result = self.assess_damage(image_path)
            if result:
                results.append(result)
        
        logger.info(f"Assessed {len(results)} out of {len(image_paths)} images")
        return results
    
    def _parse_damages(self, analysis_result: Dict[str, Any]) -> List[DamageAssessment]:
        """Parse damages from LLM analysis result
        
        Args:
            analysis_result: Raw analysis result from LLM
            
        Returns:
            List of DamageAssessment objects
        """
        damages = []
        
        if "damages" not in analysis_result:
            return damages
        
        for damage_data in analysis_result["damages"]:
            try:
                damage = DamageAssessment(**damage_data)
                damages.append(damage)
            except Exception as e:
                logger.warning(f"Failed to parse damage: {damage_data}, Error: {str(e)}")
        
        return damages
    
    def _generate_summary(
        self,
        damages: List[DamageAssessment],
        cost_estimate,
        insurance_claim,
    ) -> str:
        """Generate assessment summary
        
        Args:
            damages: List of damage assessments
            cost_estimate: Cost estimate object
            insurance_claim: Insurance claim details
            
        Returns:
            Summary string
        """
        if not damages:
            return "No significant damage detected."
        
        damage_count = len(damages)
        total_cost = cost_estimate.total_estimated_cost
        payout = insurance_claim.estimated_payout
        
        summary = (
            f"Assessment identified {damage_count} damage(s). "
            f"Estimated repair cost: ${total_cost:.2f}. "
            f"Estimated insurance payout: ${payout:.2f}. "
            f"Claim status: {'Approved' if insurance_claim.is_covered else 'Not Covered'}."
        )
        
        return summary
