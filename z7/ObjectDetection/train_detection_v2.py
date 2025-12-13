#!/usr/bin/env python3
"""
Azure Custom Vision - Object Detection Training v2
Upload images with bounding boxes and train the model
"""

import json
import time
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageFileCreateBatch, ImageFileCreateEntry, Region
)
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

def load_config():
    """Load project configuration"""
    with open("detection_config.json") as f:
        return json.load(f)

def parse_xml_annotation(xml_path, image_width=640, image_height=480):
    """Parse Pascal VOC XML annotation"""
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        regions = []
        
        for obj in root.findall('object'):
            name = obj.find('name').text
            bndbox = obj.find('bndbox')
            
            xmin = int(bndbox.find('xmin').text)
            ymin = int(bndbox.find('ymin').text)
            xmax = int(bndbox.find('xmax').text)
            ymax = int(bndbox.find('ymax').text)
            
            # Convert to normalized coordinates (0-1)
            left = xmin / image_width
            top = ymin / image_height
            width = (xmax - xmin) / image_width
            height = (ymax - ymin) / image_height
            
            # Clamp to [0, 1]
            left = max(0, min(1, left))
            top = max(0, min(1, top))
            width = max(0, min(1, width))
            height = max(0, min(1, height))
            
            regions.append({
                'tag_name': name,
                'left': left,
                'top': top,
                'width': width,
                'height': height
            })
        
        return regions
    except Exception as e:
        print(f"    ⚠️  Error parsing {xml_path}: {e}")
        return []

def upload_and_train():
    """Upload images and train model"""
    
    print("\n" + "="*70)
    print("OBJECT DETECTION - UPLOAD & TRAIN")
    print("="*70)
    
    config = load_config()
    project_id = config["project_id"]
    tags = config["tags"]
    
    credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
    trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
    
    training_dir = Path("training_images")
    
    # Find all image files
    image_files = sorted(list(training_dir.glob("*.jpg")) + list(training_dir.glob("*.png")))
    
    if not image_files:
        print("❌ Brak obrazów w training_images/")
        return
    
    print(f"\nUploading {len(image_files)} images with annotations...")
    
    for image_path in image_files:
        xml_path = image_path.with_suffix(".xml")
        
        if not xml_path.exists():
            print(f"  NO ANNOTATION: {image_path.name}")
            continue
        
        print(f"  Uploading {image_path.name}...", end="")
        
        try:
            # Parse annotation
            regions = parse_xml_annotation(xml_path)
            
            if not regions:
                print(" (no objects)")
                continue
            
            # Read image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Create image entries with regions
            batch = ImageFileCreateBatch()
            batch.images = []
            
            entry = ImageFileCreateEntry(
                name=image_path.name,
                contents=image_data
            )
            
            # Create regions list
            entry.regions = []
            
            # Add regions to entry
            for region in regions:
                tag_id = tags.get(region['tag_name'])
                if tag_id:
                    from azure.cognitiveservices.vision.customvision.training.models import Region
                    r = Region(
                        tag_id=tag_id,
                        left=region['left'],
                        top=region['top'],
                        width=region['width'],
                        height=region['height']
                    )
                    entry.regions.append(r)
            
            batch.images.append(entry)
            
            # Upload
            result = trainer.create_images_from_files(project_id, batch)
            
            if result.is_batch_successful:
                print(f" OK ({len(regions)} objects)")
            else:
                print(f" PARTIAL")
                for image_result in result.images:
                    if not image_result.status == "OK":
                        print(f"      {image_result.status}: {image_result.error}")
        
        except Exception as e:
            print(f" ERROR: {str(e)[:50]}")
    
    # Train model
    print("\n" + "-"*70)
    print("TRAINING MODEL...")
    print("-"*70)
    
    try:
        iteration = trainer.train_project(project_id)
        print(f"OK - Training started: {iteration.id}")
        
        # Wait for training to complete
        print("Waiting for training to complete...", end="", flush=True)
        
        max_wait = 60  # Max 60 seconds
        start_time = time.time()
        
        while iteration.status == "Training":
            time.sleep(5)
            print(".", end="", flush=True)
            iteration = trainer.get_iteration(project_id, iteration.id)
            
            if time.time() - start_time > max_wait:
                print("\n⏱️  Training timeout - may still be running")
                break
        
        print()
        
        # Get results
        print(f"\nTraining Complete!")
        print(f"  Status: {iteration.status}")
        print(f"  Precision: {iteration.precision:.2%}" if hasattr(iteration, 'precision') else "  Precision: N/A")
        print(f"  Recall: {iteration.recall:.2%}" if hasattr(iteration, 'recall') else "  Recall: N/A")
        print(f"  mAP: {iteration.average_precision:.2%}" if hasattr(iteration, 'average_precision') else "  mAP: N/A")
        
        # Publish iteration
        print("\nPublishing iteration...")
        
        config_pred_id = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVisionPred"
        
        try:
            trainer.publish_iteration(
                project_id,
                iteration.id,
                "ObjectDetectionModel",
                config_pred_id
            )
            print("OK - Iteration published")
        except Exception as e:
            print(f"WARNING: Publish error: {e}")
        
        # Save results
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "iteration_id": iteration.id,
            "status": iteration.status,
            "trained_at": str(iteration.trained_at) if hasattr(iteration, 'trained_at') else None
        }
        
        with open("training_results_detection.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"OK - Results saved to training_results_detection.json")
        
    except Exception as e:
        print(f"ERROR: Training error: {e}")

if __name__ == "__main__":
    upload_and_train()
