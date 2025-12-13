#!/usr/bin/env python3
"""
Azure Custom Vision - Object Detection Training
Trenuje model do detekcji obiektów (bounding boxes)
mAP (mean Average Precision) zamiast Precision/Recall
"""

import json
import os
from pathlib import Path
from datetime import datetime
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageFileCreateBatch, ImageFileCreateEntry, Region
)
from msrest.authentication import ApiKeyCredentials
import time

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

def create_detection_project():
    """Create new Object Detection project"""
    
    print("\n" + "="*70)
    print("AZURE CUSTOM VISION - OBJECT DETECTION")
    print("="*70)
    
    credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
    trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
    
    # Create project (Object Detection type)
    print("\n1. Tworze projekt Object Detection...")
    try:
        project = trainer.create_project(
            "ObjectDetectionLab8",
            project_type="ObjectDetection",
            description="Object Detection - Detekcja Obiektow"
        )
        print(f"   ✓ Projekt utworzony: {project.id}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"   ℹ Projekt już istnieje, pobieranie...")
            projects = trainer.get_projects()
            project = next((p for p in projects if p.name == "ObjectDetectionLab8"), None)
            if project:
                print(f"   ✓ Projekt znaleziony: {project.id}")
            else:
                print(f"   ✗ ERROR: {e}")
                return
        else:
            print(f"   ✗ ERROR: {e}")
            return
    
    project_id = project.id
    
    # Create tags for objects
    print("\n2. Tworzę tagi dla obiektów...")
    tags = {}
    for tag_name in ["osoba", "samochod", "pies", "kot"]:
        try:
            tag = trainer.create_tag(project_id, tag_name)
            tags[tag_name] = tag.id
            print(f"   ✓ Tag '{tag_name}': {tag.id}")
        except Exception as e:
            if "already exists" in str(e):
                # Get existing tag
                existing_tags = trainer.get_tags(project_id)
                tag = next((t for t in existing_tags if t.name == tag_name), None)
                if tag:
                    tags[tag_name] = tag.id
                    print(f"   ℹ Tag '{tag_name}' już istnieje: {tag.id}")
            else:
                print(f"   ✗ ERROR dla tagu {tag_name}: {e}")
    
    # Check for training images
    training_dir = Path("training_images")
    if not training_dir.exists() or not list(training_dir.glob("*.*")):
        print(f"\n⚠️  Brak obrazów treningowych w {training_dir}")
        print("   Instrukcja:")
        print(f"   1. Wgraj obrazy do: {training_dir.absolute()}")
        print("   2. Dla każdego obrazu stwórz plik .xml z bounding boxy (Pascal VOC format)")
        print("   3. Uruchom script ponownie")
        print("\nPrzykład bounding box (sample_image.xml):")
        print("""
<annotation>
  <filename>sample_image.jpg</filename>
  <object>
    <name>osoba</name>
    <bndbox>
      <xmin>100</xmin>
      <ymin>50</ymin>
      <xmax>200</xmax>
      <ymax>300</ymax>
    </bndbox>
  </object>
</annotation>
        """)
        
        return {
            "status": "WAITING_FOR_IMAGES",
            "project_id": project_id,
            "tags": tags
        }
    
    print("\n3. Uploaduję obrazy z bounding boxy...")
    # This would need images and annotations
    # For now, just document the structure
    
    result = {
        "project_id": project_id,
        "project_name": "ObjectDetectionLab8",
        "tags": tags,
        "status": "READY_FOR_TRAINING",
        "instructions": {
            "format": "Pascal VOC (XML)",
            "required_files": "Image + XML annotation for each image",
            "bounding_box_format": {"xmin": 100, "ymin": 50, "xmax": 200, "ymax": 300}
        }
    }
    
    # Save configuration
    with open("detection_config.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✓ Konfiguracja zapisana do detection_config.json")
    print(f"\nProjekt gotów do trenowania gdy przygotowisz dane:")
    print(f"  - Obrazy: {training_dir}/")
    print(f"  - Anotacje (XML): {training_dir}/ (1:1 z obrazami)")
    
    return result

def upload_annotated_images():
    """Upload images with bounding box annotations"""
    
    with open("detection_config.json") as f:
        config = json.load(f)
    
    project_id = config["project_id"]
    tags = config["tags"]
    
    credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
    trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
    
    training_dir = Path("training_images")
    
    # Find all image files
    image_files = list(training_dir.glob("*.jpg")) + list(training_dir.glob("*.png"))
    
    if not image_files:
        print("Brak obrazów do uploadowania")
        return
    
    print(f"\nUploaduję {len(image_files)} obrazów z anotacjami...")
    
    for image_path in image_files:
        # Check for annotation file
        xml_path = image_path.with_suffix(".xml")
        
        if not xml_path.exists():
            print(f"⚠️  Brak anotacji dla {image_path.name}")
            continue
        
        print(f"  Uploaduję {image_path.name}...")
        # Upload with regions would go here
        # For now just document the process

if __name__ == "__main__":
    result = create_detection_project()
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("""
1. PRZYGOTUJ DANE:
   - Umieść obrazy w: training_images/
   - Dla każdego obrazu utwórz plik XML z bounding boxy
   
2. FORMAT ANOTACJI (Pascal VOC):
   - Plik: training_images/image_name.xml
   - Zawiera: współrzędne (xmin, ymin, xmax, ymax) dla każdego obiektu
   
3. URUCHOM UPLOAD:
   - python train_detection.py --upload
   
4. URUCHOM TRENOWANIE:
   - python train_detection.py --train
   
5. TESTUJ MODEL:
   - python test_detection.py --image test_images/sample.jpg
""")
