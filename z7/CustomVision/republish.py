"""
Republish iteration with correct Prediction Resource ID
"""
import json
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"
PREDICTION_RESOURCE_ID = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVisionPred"

with open("training_results.json") as f:
    data = json.load(f)

project_id = data["project_id"]
iteration_id = data["iteration_id"]

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

print("Republishing iteration with correct Prediction Resource...")
print(f"Project: {project_id}")
print(f"Iteration: {iteration_id}")
print(f"Resource: {PREDICTION_RESOURCE_ID}\n")

try:
    # First unpublish if already published
    try:
        trainer.unpublish_iteration(project_id, iteration_id)
        print("OK Unpublished old iteration")
    except:
        print("OK No previous publish to remove")
    
    # Now publish with correct resource
    result = trainer.publish_iteration(
        project_id,
        iteration_id,
        publish_name="Iteration1",
        prediction_resource_id=PREDICTION_RESOURCE_ID
    )
    
    print(f"\nOK Republished iteration 'Iteration1'")
    print(f"   Published to: {PREDICTION_RESOURCE_ID}")
    print(f"\nWait 30-60 seconds for propagation, then test API...")
    
except Exception as e:
    print(f"ERROR: {e}")
