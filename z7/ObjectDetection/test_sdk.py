#!/usr/bin/env python3
"""
Test Object Detection using SDK (nie HTTP API)
"""

import json
from pathlib import Path
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"
PROJECT_ID = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"

credentials = ApiKeyCredentials(in_headers={"Prediction-key": PREDICTION_KEY})
predictor = CustomVisionPredictionClient(ENDPOINT, credentials)

test_dir = Path("test_images")
test_images = sorted(list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png")))

print("\n" + "="*70)
print("OBJECT DETECTION - SDK TEST")
print("="*70)

results = {
    "model": "ObjectDetectionModel",
    "test_results": []
}

for image_path in test_images:
    print(f"\n{image_path.name}:")
    
    try:
        with open(image_path, "rb") as f:
            results_od = predictor.detect_image(
                PROJECT_ID,
                "ObjectDetectionModel",
                f
            )
        
        predictions = results_od.predictions
        print(f"  Detected {len(predictions)} objects:")
        
        for pred in predictions:
            print(f"    - {pred.tag_name}: {pred.probability*100:.1f}% @ ({pred.bounding_box.left:.2f}, {pred.bounding_box.top:.2f})")
        
        results["test_results"].append({
            "image": image_path.name,
            "detections": len(predictions),
            "predictions": [{
                "tag": p.tag_name,
                "probability": p.probability,
                "bbox": {
                    "left": p.bounding_box.left,
                    "top": p.bounding_box.top,
                    "width": p.bounding_box.width,
                    "height": p.bounding_box.height
                }
            } for p in predictions]
        })
        
    except Exception as e:
        print(f"  ERROR: {str(e)[:100]}")
        results["test_results"].append({
            "image": image_path.name,
            "error": str(e)
        })

# Save
with open("object_detection_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved")
print(f"Total detections: {sum(len(r.get('predictions', [])) for r in results['test_results'])}")
