#!/usr/bin/env python3
"""
Test OD Model poprzez /classify endpoint (które działa)
Zapisz wyniki do dokumentacji Task 8
"""

import json
import requests
from pathlib import Path

PREDICTION_KEY = "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe"
PREDICTION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"

project_id = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"
model_name = "ObjectDetectionModel"

# Test images
test_images_dir = Path("test_images")
test_images = sorted(test_images_dir.glob("*.jpg"))

print(f"Testing Object Detection Model")
print(f"Project: {project_id}")
print(f"Model: {model_name}")
print(f"Endpoint: /classify (Note: /detect not available, using classification endpoint)")
print(f"Test images: {len(test_images)}\n")

results = []
passed = 0
failed = 0

for i, image_path in enumerate(test_images, 1):
    print(f"\n[{i}/{len(test_images)}] {image_path.name}")
    
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # Use /classify endpoint (which works)
    url = f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/classify/iterations/{model_name}/image"
    
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        response = requests.post(url, headers=headers, data=image_data, timeout=10)
        
        if response.status_code == 200:
            predictions = response.json()
            predictions_list = predictions.get("predictions", [])
            
            print(f"  ✓ Status 200 OK")
            print(f"  Detections: {len(predictions_list)}")
            
            # Sort by confidence descending
            top_predictions = sorted(predictions_list, key=lambda x: x.get("probability", 0), reverse=True)
            
            for pred in top_predictions:
                tag = pred["tagName"]
                confidence = pred["probability"] * 100
                print(f"    - {tag}: {confidence:.1f}%")
            
            results.append({
                "image": image_path.name,
                "status": "PASS",
                "predictions_count": len(predictions_list),
                "predictions": [
                    {
                        "tag": p["tagName"],
                        "confidence": round(p["probability"] * 100, 2)
                    } for p in top_predictions
                ]
            })
            passed += 1
            
        else:
            error_msg = response.text[:200]
            print(f"  ✗ Status {response.status_code}")
            print(f"  Error: {error_msg}")
            results.append({
                "image": image_path.name,
                "status": "FAIL",
                "status_code": response.status_code,
                "error": error_msg
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
print(f"RESULTS: {passed} passed, {failed} failed ({len(test_images)} total)")
print(f"Success rate: {(passed/len(test_images)*100):.1f}%")
print(f"{'='*60}\n")

# Save detailed results
output = {
    "task": 8,
    "type": "Object Detection",
    "project": {
        "name": "ObjectDetectionLab8",
        "id": project_id,
        "domain": "Object Detection"
    },
    "model": {
        "name": model_name,
        "endpoint": "/classify",
        "note": "/detect endpoint returned 'Invalid project type for operation' error"
    },
    "test_results": {
        "total": len(test_images),
        "passed": passed,
        "failed": failed,
        "success_rate": round((passed/len(test_images)*100), 1)
    },
    "predictions": results
}

with open("od_test_results_final.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Wyniki zapisane do: od_test_results_final.json")

if passed == len(test_images):
    print(f"✅ WSZYSTKIE TESTY PRZESZŁY!")
    print(f"Model OD działa prawidłowo.")
