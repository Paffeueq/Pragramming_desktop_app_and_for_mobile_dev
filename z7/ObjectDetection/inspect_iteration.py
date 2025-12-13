#!/usr/bin/env python3
"""
Inspect Iteration object structure
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

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

iteration = trainer.get_iteration(project_id, iteration_id)

print("Iteration object attributes:")
print(f"  id: {iteration.id}")
print(f"  name: {iteration.name}")
print(f"  status: {iteration.status}")
print(f"  publish_name: {iteration.publish_name}")

print("\nAll attributes:")
for attr in dir(iteration):
    if not attr.startswith('_'):
        print(f"  {attr}")
