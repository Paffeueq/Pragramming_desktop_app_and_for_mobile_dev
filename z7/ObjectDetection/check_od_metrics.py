#!/usr/bin/env python3
"""
Sprawdź metryki modelu Object Detection - czy to OD czy klasyfikacja?
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

# Pobierz projekt
project = trainer.get_project(project_id)
print(f"Projekt: {project.name}")
print(f"ID: {project.id}\n")

# Pobierz wszystkie iteracje
iterations = trainer.get_iterations(project_id)
print(f"Iteracje ({len(iterations)}):\n")

for iteration in iterations:
    print(f"  Nazwa: {iteration.name}")
    print(f"  ID: {iteration.id}")
    print(f"  Status: {iteration.status}")
    print(f"  Opublikowana: {iteration.publish_name}")
    print(f"  Data treningu: {iteration.trained_at}")
    print(f"  Czas treningu (min): {iteration.training_time_in_minutes}")
    
    # Metryki OD powinny mieć:
    # - precision, recall, average_precision (AP) dla każdej klasy
    # - mean average precision (mAP)
    # Klasyfikacja ma: precision, recall, accuracy per class
    
    print(f"\n  Atrybuty iteracji:")
    for attr in dir(iteration):
        if not attr.startswith('_') and not callable(getattr(iteration, attr)):
            val = getattr(iteration, attr)
            if 'precision' in attr.lower() or 'recall' in attr.lower() or 'average' in attr.lower() or 'map' in attr.lower():
                print(f"    {attr}: {val}")
    
    print()
