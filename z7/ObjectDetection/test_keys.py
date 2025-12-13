#!/usr/bin/env python3
"""
Test if the error message changes with different Prediction Keys
"""

import json
import requests
from pathlib import Path

# Test keys
keys_to_test = {
    "OD Resource (NEW)": "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe",
    "Classification Resource (OLD)": "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM",
}

PREDICTION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
project_id = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"
model_name = "ObjectDetectionModel"

test_image = Path("test_images/test_1.jpg")
with open(test_image, "rb") as f:
    image_data = f.read()

for key_name, key_value in keys_to_test.items():
    print(f"\nTesting with {key_name}:")
    
    url = f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/detect/iterations/{model_name}/image"
    
    headers = {
        "Prediction-Key": key_value,
        "Content-Type": "application/octet-stream"
    }
    
    response = requests.post(url, headers=headers, data=image_data)
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text}")
