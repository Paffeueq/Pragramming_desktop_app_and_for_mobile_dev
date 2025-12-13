"""
Custom Vision - Testowanie modelu i publikowanie
"""
import json
import os
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

# Configuration
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"
PREDICTION_RESOURCE_ID = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVision"

# Load training results
with open("training_results.json") as f:
    training_results = json.load(f)

project_id = training_results["project_id"]
iteration_id = training_results["iteration_id"]
tags = training_results["tags"]

# Initialize clients
credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

print("="*60)
print("CUSTOM VISION - PUBLIKOWANIE I TESTOWANIE")
print("="*60)

# Step 1: Publish iteration
print("\n[1/3] Publikowanie modelu...")
try:
    trainer.publish_iteration(
        project_id, 
        iteration_id, 
        "Iteration1",
        PREDICTION_RESOURCE_ID
    )
    print(f"✅ Model opublikowany jako 'Iteration1'")
except Exception as e:
    if "already published" in str(e):
        print(f"✅ Model już opublikowany")
    else:
        print(f"⚠️  {e}")

# Step 2: Get prediction URL
print("\n[2/3] Pobieranie Prediction URL...")
try:
    # Get prediction endpoint
    prediction_endpoint = trainer.get_project(project_id).custom_vision_prediction_endpoint
    prediction_key = TRAINING_KEY  # Same key for prediction
    
    print(f"✅ Prediction Endpoint: {prediction_endpoint}")
    print(f"✅ API Key dostępny")
    
except Exception as e:
    print(f"⚠️  Błąd: {e}")

# Step 3: Test predictions on sample images
print("\n[3/3] Testowanie predykcji na obrazach...")

# Initialize prediction client
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": TRAINING_KEY})
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

test_results = {}
images_dir = "images"

for tag_name in os.listdir(images_dir):
    tag_path = os.path.join(images_dir, tag_name)
    
    if not os.path.isdir(tag_path):
        continue
    
    print(f"\n  Tag: {tag_name}")
    test_results[tag_name] = []
    
    image_files = [f for f in os.listdir(tag_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
    
    # Test first 3 images per tag
    for img_file in image_files[:3]:
        img_path = os.path.join(tag_path, img_file)
        
        try:
            with open(img_path, "rb") as f:
                image_data = f.read()
            
            # Make prediction
            results = predictor.classify_image(project_id, "Iteration1", image_data)
            
            # Get top prediction
            top_pred = max(results.predictions, key=lambda x: x.probability)
            confidence = top_pred.probability
            predicted_tag = top_pred.tag_name
            is_correct = (predicted_tag == tag_name)
            
            test_results[tag_name].append({
                "image": img_file,
                "predicted": predicted_tag,
                "confidence": confidence,
                "correct": is_correct
            })
            
            status = "✅" if is_correct else "❌"
            print(f"    {status} {img_file}: {predicted_tag} ({confidence:.1%})")
            
        except Exception as e:
            print(f"    ❌ {img_file}: {str(e)[:50]}")

# Calculate accuracy
total_tests = sum(len(results) for results in test_results.values())
correct_tests = sum(
    sum(1 for r in results if r["correct"]) 
    for results in test_results.values()
)
accuracy = (correct_tests / total_tests * 100) if total_tests > 0 else 0

print(f"\n{'='*60}")
print("WYNIKI TESTOWANIA:")
print(f"  Testów: {total_tests}")
print(f"  Poprawnych: {correct_tests}")
print(f"  Accuracy: {accuracy:.1f}%")
print(f"{'='*60}")

# Save test results
full_results = {
    "training": training_results,
    "prediction_endpoint": ENDPOINT,
    "published_iteration": "Iteration1",
    "test_results": test_results,
    "test_accuracy": accuracy
}

with open("prediction_results.json", "w") as f:
    json.dump(full_results, f, indent=2)

print(f"\n✅ Wyniki zapisane do prediction_results.json")
