#!/usr/bin/env python3
"""
Azure Custom Vision - Object Detection Testing
Testuje model na obrazach z wieloma obiektami
Wyświetla bounding boxy, confidence i mAP
"""

import json
import requests
from pathlib import Path
from datetime import datetime

PREDICTION_KEY = "Ypt2zxb4e2sDdOsJAiKEqmrkWcLEfRAR0L7Rb95FWt12QZYYJu6SJQQJ99BLACYeBjFXJ3w3AAAIACOGB2CM"
ENDPOINT = "https://eastus.api.cognitive.microsoft.com"

def test_object_detection():
    """Test Object Detection on images"""
    
    print("\n" + "="*70)
    print("CUSTOM VISION - OBJECT DETECTION TEST")
    print("="*70)
    
    # Load project config
    config_file = Path("detection_config.json")
    if not config_file.exists():
        print("❌ Brak detection_config.json - uruchom train_detection.py najpierw")
        return
    
    with open(config_file) as f:
        config = json.load(f)
    
    project_id = config.get("project_id")
    
    if not project_id:
        print("❌ Brak project_id w konfiguracji")
        return
    
    # Check for test images
    test_dir = Path("test_images")
    if not test_dir.exists() or not list(test_dir.glob("*.*")):
        print(f"\n⚠️  Brak obrazów testowych w {test_dir}")
        print("Instrukcja:")
        print(f"  1. Wgraj obrazy testowe do: {test_dir.absolute()}")
        print("  2. Idealne: obrazy z WIELOMA obiektami różnych kategorii")
        print("  3. Uruchom test ponownie: python test_detection.py")
        return
    
    print(f"\nProject ID: {project_id}")
    print(f"Prediction Key: {PREDICTION_KEY[:20]}...")
    
    # Build prediction URL
    # Note: iteration_name będzie znany po trenowaniu
    iteration_name = "Iteration1"
    
    url = f"{ENDPOINT}/customvision/v3.1/prediction/{project_id}/detect/iterations/{iteration_name}/image"
    
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    print(f"\nPrediction URL: {url}")
    print(f"\nTestuję obrazy...")
    
    test_images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
    
    if not test_images:
        print("  ❌ Brak obrazów do testowania")
        return
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "project_id": project_id,
        "test_images": []
    }
    
    for image_path in sorted(test_images):
        print(f"\n  📷 {image_path.name}")
        
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            response = requests.post(url, data=image_data, headers=headers)
            
            if response.status_code != 200:
                print(f"    ❌ HTTP {response.status_code}")
                print(f"       {response.text[:100]}")
                results["test_images"].append({
                    "image": image_path.name,
                    "status": "error",
                    "http_code": response.status_code
                })
                continue
            
            result = response.json()
            predictions = result.get("predictions", [])
            
            print(f"    ✓ Detected {len(predictions)} objects")
            
            for idx, pred in enumerate(predictions, 1):
                tag = pred.get("tagName", "unknown")
                confidence = pred.get("probability", 0) * 100
                bbox = pred.get("boundingBox", {})
                
                left = bbox.get("left", 0)
                top = bbox.get("top", 0)
                width = bbox.get("width", 0)
                height = bbox.get("height", 0)
                
                print(f"      [{idx}] {tag:12} ({confidence:5.2f}%) "
                      f"@ ({left:.2f}, {top:.2f}) {width:.2f}x{height:.2f}")
            
            results["test_images"].append({
                "image": image_path.name,
                "status": "success",
                "detected_objects": len(predictions),
                "predictions": predictions
            })
            
        except Exception as e:
            print(f"    ❌ Exception: {str(e)[:60]}")
            results["test_images"].append({
                "image": image_path.name,
                "status": "exception",
                "error": str(e)
            })
    
    # Save results
    results_file = Path("detection_test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    test_object_detection()
