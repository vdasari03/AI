"""Mock responses for testing"""
import json

MOCK_RESPONSES = {
    "image_1": {
        "damages": [
            {
                "location": "front_bumper",
                "severity": "moderate",
                "estimated_size_inches": 2.5,
                "description": "Moderate dent on front bumper with paint chipping",
                "repair_type": "repairable",
                "repair_complexity": "medium",
            }
        ],
        "additional_notes": "No structural damage, bumper can be restored",
    },
    "image_2": {
        "damages": [
            {
                "location": "driver_side_door",
                "severity": "severe",
                "estimated_size_inches": 4.5,
                "description": "Deep dent on driver-side door with significant paint damage",
                "repair_type": "replaceable",
                "repair_complexity": "high",
            }
        ],
        "additional_notes": "Recommend door panel replacement for safety",
    },
    "image_3": {
        "damages": [
            {
                "location": "rear_fender",
                "severity": "minor",
                "estimated_size_inches": 0.8,
                "description": "Small ding on rear fender, minor cosmetic damage",
                "repair_type": "repairable",
                "repair_complexity": "simple",
            }
        ],
        "additional_notes": "Simple PDR (Paintless Dent Repair) can fix this",
    },
    "image_4": {
        "damages": [
            {
                "location": "hood",
                "severity": "moderate",
                "estimated_size_inches": 3.2,
                "description": "Multiple small dents on hood with paint cracking",
                "repair_type": "repairable",
                "repair_complexity": "medium",
            },
            {
                "location": "front_bumper",
                "severity": "minor",
                "estimated_size_inches": 1.0,
                "description": "Minor damage to bumper corner",
                "repair_type": "repairable",
                "repair_complexity": "simple",
            },
        ],
        "additional_notes": "Hood repair with full repaint recommended",
    },
    "image_5": {
        "damages": [
            {
                "location": "roof",
                "severity": "severe",
                "estimated_size_inches": 5.5,
                "description": "Large dent on roof with creasing and paint loss",
                "repair_type": "total_loss",
                "repair_complexity": "very_high",
            }
        ],
        "additional_notes": "Vehicle may be classified as total loss due to roof damage",
    },
}
