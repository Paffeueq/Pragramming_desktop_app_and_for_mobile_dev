#!/usr/bin/env python3
"""
Test na NOWYCH (validation) obrazach - nie z training set
Porównanie performansu modelu na danych które nigdy nie widział
"""

import json
import requests
from pathlib import Path
from datetime import datetime

PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"
PROJECT_ID = "2d44e737-37e6-40a0-98db-6bee58ea8f56"
ITERATION = "Iteration1"
ENDPOINT = "https://eastus.api.cognitive.microsoft.com"

URL = f"{ENDPOINT}/customvision/v3.1/prediction/{PROJECT_ID}/classify/iterations/{ITERATION}/image"

HEADERS = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

# Categories with expected tags
CATEGORIES = {
    "koty": "e483b79e-06c9-431d-a2dc-f7771034a3ea",
    "traktory": "2f708736-db58-4ac1-803f-21c3ab46b1e0",
    "wydry": "1dabcd5e-50ff-47ca-8115-ff3d7a99913c"
}

def test_validation_images():
    """Test model on NEW (validation) images"""
    
    print("\n" + "="*70)
    print("CUSTOM VISION - VALIDATION TEST (NEW IMAGES)")
    print("="*70)
    
    test_dir = Path("test_images")
    
    if not test_dir.exists():
        print("ERROR: test_images folder not found!")
        print(f"Please create: {test_dir.absolute()}")
        return
    
    results = {
        "test_type": "validation_set",
        "timestamp": datetime.now().isoformat(),
        "categories": {}
    }
    
    total_tests = 0
    total_correct = 0
    
    # Test each category
    for category, tag_id in CATEGORIES.items():
        category_path = test_dir / category
        
        if not category_path.exists():
            print(f"\n[{category.upper()}] - No images found")
            continue
        
        # Get all image files
        images = sorted(list(category_path.glob("*.*")))
        
        if not images:
            print(f"\n[{category.upper()}] - No images in folder")
            continue
        
        print(f"\n[{category.upper()}]")
        results["categories"][category] = {
            "expected": category,
            "tag_id": tag_id,
            "images": []
        }
        
        category_correct = 0
        
        for image_path in images:
            try:
                # Read image
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
                # Send to API
                response = requests.post(URL, data=image_data, headers=HEADERS)
                
                if response.status_code != 200:
                    status = f"ERROR {response.status_code}"
                    print(f"  ❌ {image_path.name:20} => {status}")
                    results["categories"][category]["images"].append({
                        "image": image_path.name,
                        "error": status,
                        "correct": False
                    })
                    total_tests += 1
                    continue
                
                # Parse result
                result = response.json()
                predictions = result.get("predictions", [])
                
                if not predictions:
                    print(f"  ❌ {image_path.name:20} => No predictions")
                    results["categories"][category]["images"].append({
                        "image": image_path.name,
                        "error": "No predictions returned",
                        "correct": False
                    })
                    total_tests += 1
                    continue
                
                # Get top prediction
                top_pred = max(predictions, key=lambda x: x["probability"])
                predicted = top_pred["tagName"]
                confidence = top_pred["probability"]
                
                # Check if correct
                is_correct = (predicted == category)
                total_tests += 1
                
                if is_correct:
                    category_correct += 1
                    total_correct += 1
                    symbol = "✓"
                else:
                    symbol = "✗"
                
                conf_pct = confidence * 100
                status = f"{predicted:12} ({conf_pct:6.2f}%)"
                print(f"  {symbol} {image_path.name:20} => {status}")
                
                results["categories"][category]["images"].append({
                    "image": image_path.name,
                    "predicted": predicted,
                    "confidence": confidence,
                    "correct": is_correct
                })
                
            except Exception as e:
                print(f"  ❌ {image_path.name:20} => Exception: {str(e)[:40]}")
                results["categories"][category]["images"].append({
                    "image": image_path.name,
                    "error": str(e),
                    "correct": False
                })
                total_tests += 1
        
        category_accuracy = (category_correct / len(images) * 100) if images else 0
        print(f"  Result: {category_correct}/{len(images)} = {category_accuracy:.1f}%")
        results["categories"][category]["accuracy"] = category_accuracy
    
    # Summary
    print("\n" + "-"*70)
    print("SUMMARY:")
    print(f"  Total tests: {total_tests}")
    print(f"  Correct: {total_correct}/{total_tests}")
    if total_tests > 0:
        overall_accuracy = total_correct / total_tests * 100
        print(f"  Overall Accuracy: {overall_accuracy:.1f}%")
        results["overall_accuracy"] = overall_accuracy
    else:
        print("  No images found for testing!")
        return
    
    print("="*70 + "\n")
    
    # Save results
    output_file = Path("validation_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    test_validation_images()
