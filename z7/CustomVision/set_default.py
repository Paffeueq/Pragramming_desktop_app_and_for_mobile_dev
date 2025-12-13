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

print("Ustawiam domyslna iteracje dla predykcji...")

try:
    # Set as default iteration for prediction
    trainer.update_iteration(
        project_id,
        iteration_id,
        is_default=True
    )
    print("OK - Iteracja ustawiona jako domyslna")
except Exception as e:
    print(f"ERROR: {e}")

# Check status
it = trainer.get_iteration(project_id, iteration_id)
print(f"Iteration status:")
print(f"  Name: {it.name}")
print(f"  Published: {it.publish_name}")
print(f"  Status: {it.status}")
