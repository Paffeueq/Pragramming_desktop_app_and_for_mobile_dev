#!/usr/bin/env python3
"""
Check if project needs to be recreated as Object Detection
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

# Check current project
project = trainer.get_project(project_id)

print("Current Project:")
print(f"  Name: {project.name}")
print(f"  ID: {project.id}")
print(f"  Created: {project.created}")
print(f"  Status: {project.status}")

# List available domains
print("\nAvailable domains (first 10):")
domains = trainer.get_domains()
for i, domain in enumerate(domains[:10]):
    print(f"  {domain.name} ({domain.id})")
    if "detect" in domain.name.lower() or "object" in domain.name.lower():
        print(f"    ^ This looks like OD domain!")

# Check settings
if project.settings:
    settings = project.settings
    print(f"\nProject Settings:")
    print(f"  Domain ID: {settings.domain_id if hasattr(settings, 'domain_id') else 'N/A'}")
    print(f"  Classification Type: {settings.classification_type if hasattr(settings, 'classification_type') else 'N/A'}")
    
    # Check if domain ID matches OD
    od_domain = "ee85a74c-405e-4adc-bb47-ffa8ca0c9f31"
    if hasattr(settings, 'domain_id') and settings.domain_id == od_domain:
        print(f"\n✓ Domain is correctly set to Object Detection")
    else:
        domain_id = settings.domain_id if hasattr(settings, 'domain_id') else 'UNKNOWN'
        print(f"\n✗ Domain is NOT Object Detection!")
        print(f"  Current: {domain_id}")
        print(f"  Expected: {od_domain}")
