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

print("Sprawdzanie publikowanych iteracji...")
print(f"Project ID: {project_id}")
print(f"Iteration ID: {iteration_id}\n")

# Get all iterations
iterations = trainer.get_iterations(project_id)
print(f"Wszystkie iteracje ({len(iterations)}):")
for i, it in enumerate(iterations):
    status = "PUBLISHED" if it.publish_name else "NOT PUBLISHED"
    print(f"{i+1}. {it.name} (ID: {it.id}) - {status}")
    if it.publish_name:
        print(f"   Published as: {it.publish_name}")
