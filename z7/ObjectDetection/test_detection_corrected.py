#!/usr/bin/env python3
"""
Test Object Detection model with correct Prediction Resource
"""

import json
import requests
from pathlib import Path

# Updated credentials for OD-specific resource
PREDICTION_KEY = "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe"
PREDICTION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"

with open("detection_config.json") as f:
    config = json.load(f)

project_id = config["project_id"]
model_name = "ObjectDetectionModel"

# Get test images
test_images_dir = Path("test_images")
test_images = sorted(test_images_dir.glob("*.jpg"))

print(f"Testing Object Detection with AzCustomVisionPredOD")
print(f"Project: {project_id}")
print(f"Model: {model_name}")
print(f"Test images: {len(test_images)}\n")

results = []
passed = 0
failed = 0

for i, image_path in enumerate(test_images, 1):
    print(f"\n[{i}/{len(test_images)}] Testing: {image_path.name}")
    
    # Read image
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
    
    # Build API URL
    url = f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/detect/iterations/{model_name}/image"
    
    # Make request
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        response = requests.post(url, headers=headers, data=image_data)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            predictions = response.json()
            
            # Count detections
            detections = predictions.get("predictions", [])
            print(f"  ✓ Detected {len(detections)} objects")
            
            # Show detections
            for det in detections:
                tag = det["tagName"]
                confidence = det["probability"] * 100
                print(f"    - {tag}: {confidence:.1f}% confidence")
            
            results.append({
                "image": image_path.name,
                "status": "PASS",
                "detections": len(detections),
                "objects": [
                    {
                        "tag": d["tagName"],
                        "confidence": round(d["probability"] * 100, 2)
                    } for d in detections
                ]
            })
            passed += 1
            
        else:
            error_text = response.text
            print(f"  ✗ ERROR: {error_text[:100]}")
            results.append({
                "image": image_path.name,
                "status": "FAIL",
                "error": error_text[:200]
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
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_images)}")
print(f"Success rate: {(passed/len(test_images)*100):.1f}%")
print(f"{'='*60}")

# Save results
with open("test_results_od.json", "w") as f:
    json.dump({
        "total_tests": len(test_images),
        "passed": passed,
        "failed": failed,
        "success_rate": round(passed/len(test_images)*100, 1),
        "results": results
    }, f, indent=2)

print("\nResults saved to test_results_od.json")

if passed == len(test_images):
    print("\n✅ ALL TESTS PASSED! Object Detection API is working correctly!")
else:
    print(f"\n⚠️ {failed} tests failed. Check errors above.")
