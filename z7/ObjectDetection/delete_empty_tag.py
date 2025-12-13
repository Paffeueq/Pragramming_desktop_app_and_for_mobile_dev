#!/usr/bin/env python3
"""
Delete unused tags
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

# Delete tag "kot" (0 images)
tags = trainer.get_tags(project_id)
for tag in tags:
    if tag.name == "kot" and tag.image_count == 0:
        trainer.delete_tag(project_id, tag.id)
        print(f"Deleted tag: {tag.name}")

print("\nRemaining tags:")
tags = trainer.get_tags(project_id)
for tag in tags:
    print(f"  {tag.name}: {tag.image_count} images")
