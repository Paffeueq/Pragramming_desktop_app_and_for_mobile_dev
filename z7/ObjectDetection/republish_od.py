#!/usr/bin/env python3
"""
Republish Object Detection model with dedicated Prediction Resource
"""

import json
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

with open("detection_config.json") as f:
    config = json.load(f)

with open("training_results_detection.json") as f:
    results = json.load(f)

project_id = config["project_id"]
iteration_id = results["iteration_id"]

# New OD-specific Prediction Resource
od_pred_id = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVisionPredOD"

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

print("Republishing iteration with OD Prediction Resource...")

try:
    trainer.publish_iteration(
        project_id,
        iteration_id,
        "ObjectDetectionModel",
        od_pred_id
    )
    print("OK - Published to AzCustomVisionPredOD")
except Exception as e:
    print(f"ERROR: {e}")

# Verify
iteration = trainer.get_iteration(project_id, iteration_id)
print(f"\nIteration status:")
print(f"  Name: {iteration.name}")
print(f"  Published: {iteration.publish_name}")
print(f"  Status: {iteration.status}")
