#!/usr/bin/env python3
"""
Publish trained Object Detection model and test it
"""

import json
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials
import requests
from pathlib import Path

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"
PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"

with open("detection_config.json") as f:
    config = json.load(f)

with open("training_results_detection.json") as f:
    results = json.load(f)

project_id = config["project_id"]
iteration_id = results["iteration_id"]

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

# Get iteration details
iteration = trainer.get_iteration(project_id, iteration_id)

print("\n" + "="*70)
print("OBJECT DETECTION - TRAINING RESULTS")
print("="*70)

print(f"\nIteration: {iteration.name}")
print(f"Status: {iteration.status}")
print(f"Trained at: {iteration.trained_at}")

if hasattr(iteration, 'precision'):
    print(f"\nMetrics:")
    print(f"  Precision: {iteration.precision:.2%}")
    print(f"  Recall: {iteration.recall:.2%}")

if hasattr(iteration, 'average_precision'):
    print(f"  mAP: {iteration.average_precision:.2%}")

# Publish iteration
print(f"\nPublishing iteration...")

pred_id = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVisionPred"

try:
    trainer.publish_iteration(
        project_id,
        iteration.id,
        "ObjectDetectionModel",
        pred_id
    )
    print(f"OK - Model published as 'ObjectDetectionModel'")
except Exception as e:
    print(f"ERROR: {e}")

# Test on images
print(f"\n" + "="*70)
print("TESTING ON VALIDATION IMAGES")
print("="*70)

test_dir = Path("test_images")
test_images = sorted(list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png")))

url = f"{ENDPOINT}/customvision/v3.1/prediction/{project_id}/detect/iterations/ObjectDetectionModel/image"

headers = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

results = {
    "project_id": project_id,
    "model": "ObjectDetectionModel",
    "test_results": []
}

for image_path in test_images:
    print(f"\n{image_path.name}:")
    
    with open(image_path, "rb") as f:
        response = requests.post(url, data=f.read(), headers=headers)
    
    if response.status_code != 200:
        print(f"  ERROR {response.status_code}")
        continue
    
    data = response.json()
    predictions = data.get("predictions", [])
    
    print(f"  Detected {len(predictions)} objects:")
    
    for pred in predictions:
        tag = pred["tagName"]
        confidence = pred["probability"] * 100
        bbox = pred["boundingBox"]
        print(f"    - {tag}: {confidence:.1f}% @ ({bbox['left']:.2f}, {bbox['top']:.2f}) {bbox['width']:.2f}x{bbox['height']:.2f}")
    
    results["test_results"].append({
        "image": image_path.name,
        "detections": len(predictions),
        "predictions": predictions
    })

# Save results
with open("object_detection_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: object_detection_results.json")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Model: ObjectDetectionModel")
print(f"Status: Completed")
print(f"Total test images: {len(test_images)}")
print(f"Total detections: {sum(r['detections'] for r in results['test_results'])}")
