"""
Custom Vision - Proste HTTP testy (bez SDK)
"""
import json
import os
import requests

PROJECT_ID = "2d44e737-37e6-40a0-98db-6bee58ea8f56"
ITERATION_NAME = "Iteration1"
PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"

print("="*70)
print("CUSTOM VISION - HTTP API TEST")
print("="*70)

# Test URL format
url = f"{ENDPOINT}customvision/v3.1/prediction/{PROJECT_ID}/classify/iterations/{ITERATION_NAME}/image"

headers = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

print(f"\nTesting URL: {url}\n")

test_results = {}
images_dir = "images"
total_correct = 0
total_tests = 0

for tag_name in sorted(os.listdir(images_dir)):
    tag_path = os.path.join(images_dir, tag_name)
    
    if not os.path.isdir(tag_path):
        continue
    
    print(f"[{tag_name.upper()}]")
    test_results[tag_name] = []
    
    image_files = sorted([f for f in os.listdir(tag_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))])
    
    for img_file in image_files:
        img_path = os.path.join(tag_path, img_file)
        
        try:
            with open(img_path, "rb") as f:
                image_data = f.read()
            
            # Make HTTP request
            response = requests.post(url, headers=headers, data=image_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Find top prediction
                top_pred = max(result.get("predictions", []), key=lambda x: x.get("probability", 0))
                predicted_tag = top_pred["tagName"]
                confidence = top_pred["probability"]
                is_correct = (predicted_tag == tag_name)
                
                if is_correct:
                    total_correct += 1
                total_tests += 1
                
                test_results[tag_name].append({
                    "image": img_file,
                    "predicted": predicted_tag,
                    "confidence": float(confidence),
                    "correct": is_correct
                })
                
                result_text = "OK" if is_correct else "FAIL"
                print(f"  {result_text} {img_file:15} => {predicted_tag:12} ({confidence*100:5.1f}%)")
            else:
                print(f"  ERROR {img_file:15} => HTTP {response.status_code}")
                print(f"         {response.text[:100]}")
                
        except Exception as e:
            print(f"  ERROR {img_file:15} => {str(e)[:70]}")

# Calculate accuracy
accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0

print(f"\n{'-'*70}")
print(f"WYNIKI:")
print(f"  Testow: {total_tests}")
print(f"  Poprawnych: {total_correct}")
print(f"  Accuracy: {accuracy:.1f}%")
print(f"{'='*70}\n")

# Save results
with open("training_results.json") as f:
    training_data = json.load(f)

full_results = {
    "training": training_data,
    "testing": {
        "endpoint": ENDPOINT,
        "prediction_url": url,
        "iteration_name": ITERATION_NAME,
        "test_results": test_results,
        "total_tests": total_tests,
        "correct_predictions": total_correct,
        "accuracy_percent": accuracy
    }
}

with open("real_test_results.json", "w") as f:
    json.dump(full_results, f, indent=2)

print(f"OK Wyniki zapisane do real_test_results.json")
