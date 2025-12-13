#!/usr/bin/env python3
"""
Test Object Detection model with CORRECT /classify endpoint
"""

import json
import requests
from pathlib import Path

PREDICTION_KEY = "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe"
PREDICTION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
project_id = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"
model_name = "ObjectDetectionModel"

test_images_dir = Path("test_images")
test_images = sorted(test_images_dir.glob("*.jpg"))

print(f"Testing OD with /classify endpoint (CORRECT)")
print(f"Project: {project_id}")
print(f"Model: {model_name}")
print(f"Test images: {len(test_images)}\n")

results = []
passed = 0
failed = 0

for i, image_path in enumerate(test_images, 1):
    print(f"\n[{i}/{len(test_images)}] {image_path.name}")
    
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # CORRECT URL with /classify
    url = f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/classify/iterations/{model_name}/image"
    
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        response = requests.post(url, headers=headers, data=image_data)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            predictions = response.json()
            
            print(f"  Response JSON keys: {list(predictions.keys())}")
            
            # The response might be structured differently
            if "predictions" in predictions:
                detections = predictions["predictions"]
            else:
                detections = predictions.get("results", [])
            
            print(f"  ✓ Got {len(detections) if isinstance(detections, list) else 1} predictions")
            print(f"  Full response: {json.dumps(predictions, indent=2)[:300]}...")
            
            results.append({
                "image": image_path.name,
                "status": "PASS",
                "response_keys": list(predictions.keys())
            })
            passed += 1
            
        else:
            error_text = response.text[:200]
            print(f"  ✗ ERROR: {error_text}")
            results.append({
                "image": image_path.name,
                "status": "FAIL",
                "error": error_text
            })
            failed += 1
            
    except Exception as e:
        print(f"  ✗ Exception: {str(e)[:100]}")
        results.append({
            "image": image_path.name,
            "status": "FAIL",
            "error": str(e)[:200]
        })
        failed += 1

# Summary
print(f"\n{'='*60}")
print(f"Results: {passed} passed, {failed} failed / {len(test_images)}")
print(f"{'='*60}")
