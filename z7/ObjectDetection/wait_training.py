#!/usr/bin/env python3
"""
Wait for training to complete silently
"""

import json
import time
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

with open("detection_config_v2.json") as f:
    config = json.load(f)

with open("training_results_detection_v2.json") as f:
    results = json.load(f)

project_id = config["project_id"]
iteration_id = results["iteration_id"]

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

print(f"Waiting for training to complete...")
print(f"Project: {project_id}")
print(f"Iteration: {iteration_id}\n")

max_wait = 60 * 20  # 20 minutes
wait_time = 0

while wait_time < max_wait:
    iteration = trainer.get_iteration(project_id, iteration_id)
    
    if iteration.status == "Completed":
        print(f"\n✓ TRAINING COMPLETED!")
        print(f"  Status: {iteration.status}")
        
        # Publish
        print(f"\nPublishing model...")
        od_pred_id = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVisionPredOD"
        
        trainer.publish_iteration(
            project_id,
            iteration_id,
            "ObjectDetectionModel_v2",
            od_pred_id
        )
        
        print(f"✓ Published as 'ObjectDetectionModel_v2'")
        
        # Update config
        config["status"] = "TRAINED_AND_PUBLISHED"
        with open("detection_config_v2.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✓ Ready to test!")
        break
    elif iteration.status == "Failed":
        print(f"\n✗ Training failed!")
        break
    else:
        print(f"  Status: {iteration.status} ({wait_time}s)")
        time.sleep(5)
        wait_time += 5

if wait_time >= max_wait:
    print(f"\nTimeout waiting for training (>{max_wait}s)")
