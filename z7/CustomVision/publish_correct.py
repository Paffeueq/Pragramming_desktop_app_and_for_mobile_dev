import json
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

with open("training_results.json") as f:
    data = json.load(f)

project_id = data["project_id"]
iteration_id = data["iteration_id"]

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

print("Publikowanie iteracji z prediction_id...")

prediction_id = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVisionPred"

try:
    trainer.publish_iteration(
        project_id,
        iteration_id,
        publish_name="Iteration1",
        prediction_id=prediction_id
    )
    print("OK - Opublikowano!")
except Exception as e:
    print(f"ERROR: {e}")

# Check status
it = trainer.get_iteration(project_id, iteration_id)
print(f"\nIteration status:")
print(f"  Name: {it.name}")
print(f"  Published: {it.publish_name}")
print(f"  Status: {it.status}")
