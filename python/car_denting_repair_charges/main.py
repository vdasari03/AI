#!/usr/bin/env python3
"""Main entry point for car damage assessment application"""
import logging
import argparse
import json
import sys
from pathlib import Path

from src.app import CarDamageAssessmentApp
from src.formatters import JSONFormatter
from src.logger import configure_logging


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Car Damage Assessment and Insurance Claiming Application"
    )
    
    parser.add_argument(
        "images",
        nargs="+",
        help="Path(s) to car damage image(s)",
    )
    
    parser.add_argument(
        "-o", "--output",
        default="assessment_results.json",
        help="Output JSON file path (default: assessment_results.json)",
    )
    
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Don't save results to JSON file",
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print results",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = "DEBUG" if args.verbose else "INFO"
    configure_logging(log_level=log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Car Damage Assessment Application")
    logger.info(f"Processing {len(args.images)} image(s)")
    
    # Initialize application
    try:
        app = CarDamageAssessmentApp(use_mock_llm=True)
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        return 1
    
    # Process images
    try:
        results = app.assess_multiple(args.images)
        
        if not results:
            logger.warning("No valid assessments completed")
            return 1
        
        logger.info(f"Successfully assessed {len(results)} image(s)")
        
        # Save to JSON if requested
        if not args.no_json:
            success = JSONFormatter.save_to_file(results, args.output)
            if success:
                logger.info(f"Results saved to: {args.output}")
            else:
                logger.warning(f"Failed to save results to: {args.output}")
        
        # Print results
        if args.pretty:
            for i, result in enumerate(results, 1):
                print(f"\n{'='*80}")
                print(f"Assessment #{i}")
                print('='*80)
                print(JSONFormatter.print_result(result, pretty=True))
        else:
            print(JSONFormatter.print_result(results[0], pretty=False))
        
        return 0
    
    except Exception as e:
        logger.error(f"Error during assessment: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
