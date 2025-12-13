#!/usr/bin/env python3
"""
Check training status
"""

import json
import time
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

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

print("Checking training status...")

for i in range(12):  # Check for 2 minutes
    iteration = trainer.get_iteration(project_id, iteration_id)
    
    print(f"\nAttempt {i+1}: Status = {iteration.status}")
    
    if hasattr(iteration, 'precision'):
        print(f"  Precision: {iteration.precision:.2%}")
        print(f"  Recall: {iteration.recall:.2%}")
    
    if hasattr(iteration, 'average_precision'):
        print(f"  mAP: {iteration.average_precision:.2%}")
    
    if iteration.status != "Training":
        print(f"\nTraining Complete!")
        print(f"Final Status: {iteration.status}")
        break
    
    time.sleep(10)
    print(f"  (waiting...)")

print("\nIterationdetails:")
print(f"  ID: {iteration.id}")
print(f"  Name: {iteration.name}")
print(f"  Status: {iteration.status}")
