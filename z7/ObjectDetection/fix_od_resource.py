#!/usr/bin/env python3
"""
Fix Object Detection resource by unpublishing and republishing with correct resource
"""

import json
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials
import time

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

print(f"Project ID: {project_id}")
print(f"Iteration ID: {iteration_id}")

# Step 1: Check current status
print("\n[STEP 1] Checking current iteration status...")
iteration = trainer.get_iteration(project_id, iteration_id)
print(f"  Status: {iteration.status}")
print(f"  Published as: {iteration.publish_name}")
print(f"  Published resource: {iteration.original_publish_resource_id}")

# Step 2: Unpublish
print("\n[STEP 2] Unpublishing iteration...")
try:
    trainer.unpublish_iteration(project_id, iteration_id)
    print("  ✓ Unpublished successfully")
    time.sleep(2)  # Wait for unpublish to complete
except Exception as e:
    print(f"  ERROR during unpublish: {e}")

# Step 3: Verify unpublished
print("\n[STEP 3] Verifying unpublished status...")
iteration = trainer.get_iteration(project_id, iteration_id)
print(f"  Published as: {iteration.publish_name}")
print(f"  Published resource: {iteration.original_publish_resource_id}")

# Step 4: Republish with OD resource
print(f"\n[STEP 4] Republishing with OD Prediction Resource...")
print(f"  Resource ID: {od_pred_id}")

try:
    result = trainer.publish_iteration(
        project_id,
        iteration_id,
        "ObjectDetectionModel",
        od_pred_id
    )
    print("  ✓ Published successfully")
except Exception as e:
    print(f"  ERROR during republish: {e}")
    raise

# Step 5: Verify republished
print("\n[STEP 5] Verifying republished status...")
time.sleep(2)
iteration = trainer.get_iteration(project_id, iteration_id)
print(f"  Name: {iteration.name}")
print(f"  Published as: {iteration.publish_name}")
print(f"  Published resource: {iteration.original_publish_resource_id}")

if iteration.original_publish_resource_id and "AzCustomVisionPredOD" in iteration.original_publish_resource_id:
    print("\n✅ SUCCESS - Model is now linked to AzCustomVisionPredOD!")
else:
    print("\n⚠️ WARNING - Resource might not be properly linked")

print("\nWaiting 30 seconds for Azure to propagate changes...")
time.sleep(30)
print("Ready to test API calls!")
