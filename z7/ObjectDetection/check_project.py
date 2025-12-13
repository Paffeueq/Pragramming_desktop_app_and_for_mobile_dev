#!/usr/bin/env python3
"""
Check project images status
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

# Get images
images = trainer.get_tagged_images(project_id)
print(f"Total images in project: {len(images)}")

# Count by tag
tag_counts = {}
for img in images:
    for tag in img.tags:
        tag_name = tag.tag_name
        tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1

print("\nImages per tag:")
for tag, count in sorted(tag_counts.items()):
    print(f"  {tag}: {count}")

# Check tags
tags = trainer.get_tags(project_id)
print(f"\nTotal tags: {len(tags)}")
for tag in tags:
    print(f"  {tag.name}: {tag.id} - {tag.image_count} images")
