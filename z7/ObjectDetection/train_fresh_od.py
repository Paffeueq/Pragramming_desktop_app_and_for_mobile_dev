#!/usr/bin/env python3
"""
Re-train Object Detection on the fresh project
"""

import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageFileCreateBatch, ImageFileCreateEntry, Region
)
from msrest.authentication import ApiKeyCredentials

ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"

# Load new project ID
with open("detection_config_v2.json") as f:
    config = json.load(f)

project_id = config["project_id"]

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
            left = max(0, min(1, xmin / image_width))
            top = max(0, min(1, ymin / image_height))
            width = max(0.01, min(1, (xmax - xmin) / image_width))
            height = max(0.01, min(1, (ymax - ymin) / image_height))
            
            regions.append({
                "tag_id": name,  # Will resolve tag name later
                "left": left,
                "top": top,
                "width": width,
                "height": height
            })
        
        return regions
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
        return []

credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

# Create tags in new project
print(f"Creating tags in project {project_id}...")
tag_names = ["osoba", "samochod", "pies"]
tags = {}

for tag_name in tag_names:
    tag = trainer.create_tag(project_id, tag_name)
    tags[tag_name] = tag.id
    print(f"  Created tag: {tag_name} ({tag.id})")

# Get training images
training_dir = Path("training_images")
xml_files = sorted(training_dir.glob("*.xml"))

print(f"\nFound {len(xml_files)} training images with annotations\n")

# Prepare batch uploads
batch_size = 64  # Max per batch
batches = []
current_batch = []

for xml_file in xml_files:
    jpg_file = xml_file.with_suffix(".jpg")
    
    if not jpg_file.exists():
        print(f"Warning: {jpg_file} not found")
        continue
    
    # Parse annotations
    regions = parse_xml_annotation(xml_file)
    
    # Convert tag names to tag IDs
    region_list = []
    for region in regions:
        tag_id = tags.get(region["tag_id"])
        if tag_id:
            region_list.append(Region(
                tag_id=tag_id,
                left=region["left"],
                top=region["top"],
                width=region["width"],
                height=region["height"]
            ))
    
    # Read image
    with open(jpg_file, "rb") as f:
        image_data = f.read()
    
    # Create entry
    entry = ImageFileCreateEntry(
        name=jpg_file.name,
        contents=image_data,
        regions=region_list
    )
    
    current_batch.append(entry)
    
    if len(current_batch) >= batch_size:
        batches.append(current_batch)
        current_batch = []

if current_batch:
    batches.append(current_batch)

print(f"Prepared {len(batches)} batch(es) for upload")

# Upload batches
for batch_num, batch in enumerate(batches, 1):
    print(f"\n[Batch {batch_num}/{len(batches)}] Uploading {len(batch)} images...")
    
    batch_obj = ImageFileCreateBatch(images=batch)
    
    try:
        upload_result = trainer.create_images_from_files(project_id, batch_obj)
        
        if upload_result.is_batch_successful:
            print(f"  ✓ Batch {batch_num} uploaded successfully")
        else:
            print(f"  ⚠ Batch {batch_num} had issues:")
            for image_result in upload_result.images:
                if not image_result.status == "OK":
                    print(f"    {image_result.source_url}: {image_result.status}")
    except Exception as e:
        print(f"  ✗ Error uploading batch: {e}")

print(f"\n✓ Image upload complete!")

# Train the model
print(f"\nTraining Object Detection model...")
print(f"This may take 5-15 minutes...")

try:
    iteration = trainer.train_project(project_id)
    iteration_id = iteration.id
    
    print(f"✓ Training started!")
    print(f"  Iteration ID: {iteration_id}")
    print(f"  Status: {iteration.status}")
    
    # Wait for training to complete
    max_wait = 60 * 10  # 10 minutes
    wait_time = 0
    
    while wait_time < max_wait:
        iteration = trainer.get_iteration(project_id, iteration_id)
        
        if iteration.status == "Completed":
            print(f"\n✓ Training completed!")
            print(f"  Status: {iteration.status}")
            break
        elif iteration.status == "Failed":
            print(f"\n✗ Training failed!")
            break
        else:
            print(f"  Status: {iteration.status} (waited {wait_time}s)")
            time.sleep(10)
            wait_time += 10
    
    # Save results
    results = {
        "project_id": project_id,
        "iteration_id": iteration_id,
        "status": iteration.status,
        "trained_at": str(datetime.now()),
        "training_result": {
            "name": iteration.name,
            "status": iteration.status,
            "created": str(iteration.created),
            "last_modified": str(iteration.last_modified),
        }
    }
    
    with open("training_results_detection_v2.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to training_results_detection_v2.json")
    
    # Publish
    print(f"\nPublishing model...")
    od_pred_id = "/subscriptions/b9f41aa0-df59-4201-a0d4-5cd6cd193c72/resourceGroups/zad_7/providers/Microsoft.CognitiveServices/accounts/AzCustomVisionPredOD"
    
    trainer.publish_iteration(
        project_id,
        iteration_id,
        "ObjectDetectionModel_v2",
        od_pred_id
    )
    
    print(f"✓ Published as 'ObjectDetectionModel_v2'")
    
except Exception as e:
    print(f"Error during training: {e}")
    import traceback
    traceback.print_exc()
