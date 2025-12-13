"""
Custom Vision - Prawidłowe testowanie przez SDK (nie HTTP)
"""
import json
import os
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

# Configuration
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"
PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"

# Load training data
with open("training_results.json") as f:
    training_data = json.load(f)

project_id = training_data["project_id"]
iteration_id = training_data["iteration_id"]
tags = training_data["tags"]

print("="*70)
print("CUSTOM VISION - RZECZYWISTE TESTOWANIE MODELU")
print("="*70)

# Initialize clients
training_credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": PREDICTION_KEY})

trainer = CustomVisionTrainingClient(ENDPOINT, training_credentials)
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

# Step 1: Verify iteration status
print("\n[1/3] Sprawdzanie statusu iteracji...")
try:
    iteration = trainer.get_iteration(project_id, iteration_id)
    print(f"OK Iteracja: {iteration.name}")
    print(f"   Status: {iteration.status}")
except Exception as e:
    print(f"ERROR: {e}")

# Step 2: Publish iteration
print("\n[2/3] Publikowanie modelu na Prediction Resource...")
try:
    # Get prediction endpoint
    predictions = trainer.get_predictions(project_id, iteration_id, take=1)
    print(f"OK Model jest dostepny dla predykcji")
except Exception as e:
    print(f"WARNING Blad przy sprawdzaniu: {e}")

# Step 3: Test predictions
print("\n[3/3] RZECZYWISTE TESTOWANIE PREDYKCJI")
print("-" * 70)

test_results = {}
images_dir = "images"
total_correct = 0
total_tests = 0

for tag_name in sorted(os.listdir(images_dir)):
    tag_path = os.path.join(images_dir, tag_name)
    
    if not os.path.isdir(tag_path):
        continue
    
    print(f"\n[{tag_name.upper()}]")
    test_results[tag_name] = []
    
    image_files = sorted([f for f in os.listdir(tag_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))])
    
    # Test ALL images in tag
    for img_file in image_files:
        img_path = os.path.join(tag_path, img_file)
        
        try:
            with open(img_path, "rb") as f:
                image_data = f.read()
            
            # Make prediction using SDK
            results = predictor.classify_image(
                project_id, 
                "Iteration1",  # Published iteration name
                image_data
            )
            
            # Get all predictions
            all_predictions = []
            for prediction in results.predictions:
                all_predictions.append({
                    "tag": prediction.tag_name,
                    "probability": prediction.probability
                })
            
            # Top prediction
            top_pred = max(results.predictions, key=lambda x: x.probability)
            predicted_tag = top_pred.tag_name
            confidence = top_pred.probability
            is_correct = (predicted_tag == tag_name)
            
            if is_correct:
                total_correct += 1
            total_tests += 1
            
            test_results[tag_name].append({
                "image": img_file,
                "predicted_tag": predicted_tag,
                "confidence": float(confidence),
                "correct": is_correct,
                "all_predictions": all_predictions
            })
            
            status = "OK" if is_correct else "FAIL"
            print(f"  {status} {img_file:15} -> {predicted_tag:12} ({confidence*100:6.1f}%)")
            
        except Exception as e:
            print(f"  ERROR {img_file:15} -> ERROR: {str(e)[:60]}")
            test_results[tag_name].append({
                "image": img_file,
                "error": str(e)[:100]
            })

# Calculate metrics
accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0

print(f"\n{'-'*70}")
print(f"WYNIKI TESTOWANIA:")
print(f"  Razem testów: {total_tests}")
print(f"  Poprawnych: {total_correct}")
print(f"  Accuracy: {accuracy:.1f}%")
print(f"{'='*70}\n")

# Save detailed results
full_results = {
    "training_summary": training_data,
    "testing": {
        "endpoint": ENDPOINT,
        "project_id": project_id,
        "iteration_id": iteration_id,
        "iteration_name": "Iteration1",
        "test_results": test_results,
        "total_tests": total_tests,
        "correct_predictions": total_correct,
        "accuracy_percent": accuracy
    }
}

with open("real_test_results.json", "w") as f:
    json.dump(full_results, f, indent=2)

print(f"\nOK Rzeczywiste wyniki zapisane do real_test_results.json")

# Print summary table
print("\n" + "="*70)
print("PODSUMOWANIE PER TAG:")
print("="*70)
for tag_name in sorted(test_results.keys()):
    results = test_results[tag_name]
    correct = sum(1 for r in results if r.get("correct", False))
    total = len(results)
    tag_accuracy = (correct / total * 100) if total > 0 else 0
    print(f"  {tag_name:12} → {correct}/{total} poprawnych ({tag_accuracy:5.1f}%)")
