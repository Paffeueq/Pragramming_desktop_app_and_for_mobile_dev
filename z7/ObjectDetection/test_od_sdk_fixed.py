#!/usr/bin/env python3
"""
Test OD using SDK (which handles endpoints correctly)
"""

import json
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from pathlib import Path

# OD Prediction credentials
PREDICTION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
PREDICTION_KEY = "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe"

with open("detection_config.json") as f:
    config = json.load(f)

project_id = config["project_id"]
model_name = "ObjectDetectionModel"

# Create SDK client
credentials = ApiKeyCredentials(in_headers={"Prediction-key": PREDICTION_KEY})
predictor = CustomVisionPredictionClient(PREDICTION_ENDPOINT, credentials)

# Get test images
test_images_dir = Path("test_images")
test_images = sorted(test_images_dir.glob("*.jpg"))

print(f"Testing OD with SDK (correct endpoint handling)")
print(f"Project: {project_id}")
print(f"Model: {model_name}\n")

results = []
passed = 0
failed = 0

for i, image_path in enumerate(test_images, 1):
    print(f"\n[{i}/{len(test_images)}] {image_path.name}")
    
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
    
    try:
        # Use SDK detect method for Object Detection
        predictions = predictor.detect_image(project_id, model_name, image_data)
        
        detections = predictions.predictions
        print(f"  ✓ Detected {len(detections)} objects")
        
        for det in detections:
            tag = det.tag_name
            conf = det.probability * 100
            print(f"    - {tag}: {conf:.1f}%")
        
        results.append({
            "image": image_path.name,
            "status": "PASS",
            "detections": len(detections)
        })
        passed += 1
        
    except Exception as e:
        error_msg = str(e)
        print(f"  ✗ Error: {error_msg[:80]}")
        results.append({
            "image": image_path.name,
            "status": "FAIL",
            "error": error_msg[:200]
        })
        failed += 1

# Summary
print(f"\n{'='*60}")
print(f"Results: {passed} passed, {failed} failed / {len(test_images)}")
print(f"{'='*60}")

with open("test_results_od_sdk.json", "w") as f:
    json.dump({
        "method": "SDK",
        "total": len(test_images),
        "passed": passed,
        "failed": failed,
        "results": results
    }, f, indent=2)

if passed == len(test_images):
    print("✅ ALL TESTS PASSED!")
