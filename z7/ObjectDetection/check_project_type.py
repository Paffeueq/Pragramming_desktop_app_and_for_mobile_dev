#!/usr/bin/env python3
"""
Check project type and configuration
"""

import json
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

with open("detection_config.json") as f:
    config = json.load(f)

project_id = config["project_id"]

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

# Get project
project = trainer.get_project(project_id)

print("Project Details:")
print(f"  Name: {project.name}")
print(f"  ID: {project.id}")

print("\nAll attributes:")
for attr in dir(project):
    if not attr.startswith('_'):
        val = getattr(project, attr)
        if not callable(val):
            print(f"  {attr}: {val}")
