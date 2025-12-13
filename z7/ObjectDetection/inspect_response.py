#!/usr/bin/env python3
"""
Examine full response structure from OD model
"""

import json
import requests
from pathlib import Path

PREDICTION_KEY = "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe"
PREDICTION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
project_id = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"
model_name = "ObjectDetectionModel"

test_image = Path("test_images/test_1.jpg")
with open(test_image, "rb") as f:
    image_data = f.read()

url = f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/classify/iterations/{model_name}/image"

headers = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

response = requests.post(url, headers=headers, data=image_data)
response_json = response.json()

print("Full Response Structure:")
print(json.dumps(response_json, indent=2))

print("\n\nFirst Prediction Details:")
if response_json.get("predictions"):
    first_pred = response_json["predictions"][0]
    print(json.dumps(first_pred, indent=2))
    
    # Check for bounding box information
    if "boundingBox" in first_pred:
        print("\n✓ Has bounding box!")
    elif "bounds" in first_pred:
        print("\n✓ Has bounds!")
    else:
        print("\n✗ No bounding box found - checking keys:")
        print(f"  Keys: {list(first_pred.keys())}")
