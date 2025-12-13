#!/usr/bin/env python3
"""Debug OD API"""

import requests
from pathlib import Path

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"
PROJECT_ID = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"

url = f"{ENDPOINT}/customvision/v3.1/prediction/{PROJECT_ID}/detect/iterations/ObjectDetectionModel/image"

image = Path("test_images/test_1.jpg")

with open(image, "rb") as f:
    img_data = f.read()

headers = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

print(f"URL: {url}")
print(f"Image size: {len(img_data)} bytes")
print(f"Headers: {headers}")

response = requests.post(url, data=img_data, headers=headers)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text[:500]}")
