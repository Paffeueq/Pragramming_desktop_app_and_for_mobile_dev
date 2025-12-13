#!/usr/bin/env python3
"""
Try using the Prediction Resource endpoint directly instead of training endpoint
"""

import json
import requests
from pathlib import Path

# Use the Prediction Resource endpoint instead
PREDICTION_KEY = "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe"

# Try different endpoints
endpoints_to_try = [
    "https://eastus.api.cognitive.microsoft.com/",
    "https://azCustomVisionPredOD.cognitiveservices.azure.com/",  # Prediction resource subdomain
]

project_id = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"
model_name = "ObjectDetectionModel"

test_image = Path("test_images/test_1.jpg")
with open(test_image, "rb") as f:
    image_data = f.read()

for endpoint in endpoints_to_try:
    print(f"\nTrying endpoint: {endpoint}")
    
    url = f"{endpoint}customvision/v3.0/prediction/{project_id}/detect/iterations/{model_name}/image"
    
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    try:
        response = requests.post(url, headers=headers, data=image_data, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:100]}")
        
        if response.status_code == 200:
            print(f"  ✓ SUCCESS with this endpoint!")
        else:
            try:
                error = response.json()
                print(f"  Error: {error['message']}")
            except:
                pass
    except Exception as e:
        print(f"  Failed: {str(e)[:80]}")
