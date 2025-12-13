"""
Custom Vision - Proste testowanie przez HTTP API
"""
import json
import requests
import os

# Configuration
PROJECT_ID = "2d44e737-37e6-40a0-98db-6bee58ea8f56"
ITERATION_NAME = "Iteration1"
PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"

print("="*60)
print("CUSTOM VISION - HTTP API PREDICTION TEST")
print("="*60)

# Test URL
base_url = f"{ENDPOINT}customvision/v3.1/prediction/{PROJECT_ID}/classify/iterations/{ITERATION_NAME}/image"

headers = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

test_results = {}
images_dir = "images"

print("\n[Testowanie predykcji na obrazach]\n")

for tag_name in sorted(os.listdir(images_dir)):
    tag_path = os.path.join(images_dir, tag_name)
    
    if not os.path.isdir(tag_path):
        continue
    
    print(f"Tag: {tag_name}")
    test_results[tag_name] = []
    
    image_files = sorted([f for f in os.listdir(tag_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))])
    
    # Test first 3 images per tag
    for img_file in image_files[:3]:
        img_path = os.path.join(tag_path, img_file)
        
        try:
            with open(img_path, "rb") as f:
                image_data = f.read()
            
            # Make prediction
            response = requests.post(base_url, headers=headers, data=image_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Find top prediction
                top_pred = max(result["predictions"], key=lambda x: x["probability"])
                predicted_tag = top_pred["tagName"]
                confidence = top_pred["probability"]
                is_correct = (predicted_tag == tag_name)
                
                test_results[tag_name].append({
                    "image": img_file,
                    "predicted": predicted_tag,
                    "confidence": float(confidence),
                    "correct": is_correct
                })
                
                status = "✅" if is_correct else "❌"
                print(f"  {status} {img_file:20} → {predicted_tag:15} ({confidence*100:5.1f}%)")
            else:
                print(f"  ❌ {img_file}: HTTP {response.status_code}")
                print(f"     {response.text[:100]}")
                
        except Exception as e:
            print(f"  ❌ {img_file}: {str(e)[:80]}")

# Calculate metrics
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

# Save results
with open("training_results.json") as f:
    training_data = json.load(f)

full_results = {
    "training": training_data,
    "testing": {
        "prediction_endpoint": base_url,
        "iteration_name": ITERATION_NAME,
        "test_results": test_results,
        "accuracy": accuracy,
        "total_tests": total_tests,
        "correct_predictions": correct_tests
    }
}

with open("final_results.json", "w") as f:
    json.dump(full_results, f, indent=2)

print(f"\n✅ Wyniki zapisane do final_results.json")
