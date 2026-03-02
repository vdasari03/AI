"""JSON output formatting and utilities"""
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from src.models import CarDamageAssessmentResult

logger = logging.getLogger(__name__)


class JSONFormatter:
    """Format assessment results as JSON"""
    
    @staticmethod
    def format_result(result: CarDamageAssessmentResult) -> Dict[str, Any]:
        """Format single result as JSON-serializable dict
        
        Args:
            result: Assessment result
            
        Returns:
            JSON-serializable dictionary
        """
        return result.to_json()
    
    @staticmethod
    def format_results(results: List[CarDamageAssessmentResult]) -> Dict[str, Any]:
        """Format multiple results as JSON
        
        Args:
            results: List of assessment results
            
        Returns:
            JSON-serializable dictionary
        """
        return {
            "total_assessments": len(results),
            "results": [result.to_json() for result in results],
            "summary": JSONFormatter._get_overall_summary(results),
        }
    
    @staticmethod
    def save_to_file(results: List[CarDamageAssessmentResult], output_path: str) -> bool:
        """Save results to JSON file
        
        Args:
            results: List of assessment results
            output_path: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_data = JSONFormatter.format_results(results)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Results saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save results to {output_path}: {str(e)}")
            return False
    
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """Load results from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Loaded JSON data
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded results from: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load results from {file_path}: {str(e)}")
            return {}
    
    @staticmethod
    def print_result(result: CarDamageAssessmentResult, pretty: bool = True) -> str:
        """Print result as formatted JSON
        
        Args:
            result: Assessment result
            pretty: Use pretty printing
            
        Returns:
            JSON string
        """
        data = result.to_json()
        if pretty:
            return json.dumps(data, indent=2)
        return json.dumps(data)
    
    @staticmethod
    def _get_overall_summary(results: List[CarDamageAssessmentResult]) -> Dict[str, Any]:
        """Generate overall summary for multiple results
        
        Args:
            results: List of assessment results
            
        Returns:
            Summary dictionary
        """
        if not results:
            return {
                "total_cost": 0,
                "total_insurance_payout": 0,
                "average_confidence": 0,
                "covered_claims": 0,
                "uncovered_claims": 0,
            }
        
        total_cost = sum(r.cost_estimate.total_estimated_cost for r in results)
        total_payout = sum(r.insurance_claim.estimated_payout for r in results)
        avg_confidence = sum(r.cost_estimate.confidence_level for r in results) / len(results)
        covered_claims = sum(1 for r in results if r.insurance_claim.is_covered)
        uncovered_claims = len(results) - covered_claims
        
        return {
            "total_cost": round(total_cost, 2),
            "total_insurance_payout": round(total_payout, 2),
            "average_confidence": round(avg_confidence, 3),
            "covered_claims": covered_claims,
            "uncovered_claims": uncovered_claims,
            "average_cost_per_claim": round(total_cost / len(results), 2) if results else 0,
        }
