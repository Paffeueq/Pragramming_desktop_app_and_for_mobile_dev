#!/usr/bin/env python3
"""
Try different URL patterns for object detection predict
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

# Try different URL patterns
urls_to_try = [
    # Current (wrong?)
    f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/detect/iterations/{model_name}/image",
    
    # Maybe no "iterations"?
    f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/detect/{model_name}/image",
    
    # Maybe "predict" not "detect"?
    f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/predict/iterations/{model_name}/image",
    
    # Try with publishName directly
    f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/classify/iterations/{model_name}/image",
]

for url in urls_to_try:
    print(f"\nURL: {url}")
    
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        response = requests.post(url, headers=headers, data=image_data, timeout=5)
        print(f"  Status: {response.status_code}")
        resp_text = response.text[:80]
        print(f"  Response: {resp_text}")
        
        if response.status_code == 200:
            print("  ✓✓✓ SUCCESS!")
    except Exception as e:
        print(f"  Error: {str(e)[:50]}")
