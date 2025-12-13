#!/usr/bin/env python3
"""
Create a fresh Object Detection project with explicit configuration
This time we'll ensure everything is set up correctly from the start
"""

import json
import time
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

# Get OD domain
domains = trainer.get_domains()
od_domain = None
for domain in domains:
    if "general" in domain.name.lower() and not "compact" in domain.name.lower():
        print(f"Found domain: {domain.name} ({domain.id})")
        od_domain = domain
        break

if not od_domain:
    # Use specific OD domain ID
    od_domain_id = "ee85a74c-405e-4adc-bb47-ffa8ca0c9f31"
    print(f"Using OD domain: {od_domain_id}")
else:
    od_domain_id = od_domain.id
    print(f"Using OD domain: {od_domain.name}")

# Delete old project if it exists
old_project_id = "2eb84c36-4e64-4a0e-9880-5c0b9805d618"
try:
    trainer.delete_project(old_project_id)
    print(f"✓ Deleted old project {old_project_id}")
    time.sleep(2)
except Exception as e:
    print(f"Could not delete old project: {e}")

# Create new OD project
print("\nCreating fresh Object Detection project...")
try:
    project = trainer.create_project(
        name="ObjectDetectionLab8_v2",
        description="Object Detection - Detekcja Obiektów (Fresh Start)",
        domain_id=od_domain_id,
        classification_type="Multilabel",  # This might need to be different for OD
        project_type="ObjectDetection"  # EXPLICIT OD type
    )
    print(f"✓ Project created: {project.id}")
    print(f"  Name: {project.name}")
    print(f"  Domain: {project.settings.domain_id if project.settings else 'N/A'}")
except TypeError as e:
    # project_type parameter might not exist, try without it
    print(f"Note: project_type parameter not available, creating without it: {e}")
    project = trainer.create_project(
        name="ObjectDetectionLab8_v2",
        description="Object Detection - Detekcja Obiektów (Fresh Start)",
        domain_id=od_domain_id,
        classification_type="Multilabel"
    )
    print(f"✓ Project created: {project.id}")

# Save config
config = {
    "project_id": project.id,
    "project_name": project.name,
    "old_project_id": old_project_id,
    "status": "READY_FOR_IMAGES"
}

with open("detection_config_v2.json", "w") as f:
    json.dump(config, f, indent=2)

print(f"\nConfig saved to detection_config_v2.json")
print(f"Next: Re-upload training images with bounding boxes")
