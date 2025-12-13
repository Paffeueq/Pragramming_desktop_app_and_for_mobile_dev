#!/usr/bin/env python3
"""
Test with detailed error analysis
"""

import json
import requests
from pathlib import Path

PREDICTION_KEY = "7hPPZWDw7oI2UVj2HZ9ZFc2Tlf4MTKes4cC7ygwIU436biSk7dgIJQQJ99BLACYeBjFXJ3w3AAAIACOGTFpe"
PREDICTION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"

project_id = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"
model_name = "ObjectDetectionModel"

test_image = Path("test_images/test_1.jpg")

# Read test image
with open(test_image, "rb") as f:
    image_data = f.read()

# Build correct endpoint for OD detect
url = f"{PREDICTION_ENDPOINT}customvision/v3.0/prediction/{project_id}/detect/iterations/{model_name}/image"

print(f"URL: {url}\n")

headers = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

print("Headers:")
for k, v in headers.items():
    print(f"  {k}: {v[:30]}..." if len(v) > 30 else f"  {k}: {v}")

print(f"\nImage size: {len(image_data)} bytes")

response = requests.post(url, headers=headers, data=image_data)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Body:\n{response.text}")

# Parse error if any
try:
    error_json = response.json()
    print(f"\nError Details:")
    print(json.dumps(error_json, indent=2))
except:
    pass
