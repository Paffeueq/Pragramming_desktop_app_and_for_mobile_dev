"""
Custom Vision - Wgrywanie obrazów i trenowanie modelu
"""
import os
import sys
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import json

# Azure Custom Vision Configuration
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
TRAINING_KEY = "BxqCSFSTuBEUi62E254er6zl05fgDoDW7DCGQmusb2nSQoo6jdeRJQQJ99BLACYeBjFXJ3w3AAAJACOGG47V"
PROJECT_NAME = "ImageClassificationLab7"
PUBLISH_ITERATION_NAME = "Iteration1"

# Initialize training client
credentials = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

print("="*60)
print("AZURE CUSTOM VISION - AUTOMATYCZNE TRENOWANIE")
print("="*60)

# Step 1: Create project
print("\n[1/4] Tworzenie projektu Custom Vision...")
try:
    project = trainer.create_project(
        name=PROJECT_NAME,
        project_type="Multiclass",
        classification_type="Multiclass",
        domain_id="general"
    )
    project_id = project.id
    print(f"✅ Projekt utworzony: {project.name} (ID: {project_id})")
except Exception as e:
    print(f"⚠️  Projekt już istnieje, użycie istniejącego...")
    projects = trainer.get_projects()
    project = next((p for p in projects if p.name == PROJECT_NAME), None)
    if project:
        project_id = project.id
        print(f"✅ Projekt znaleziony: {project.name} (ID: {project_id})")
    else:
        print(f"❌ Błąd: {e}")
        sys.exit(1)

# Step 2: Create tags and collect image paths
print("\n[2/4] Tworzenie tagów i przygotowanie obrazów...")
tags = {}
images_dir = "images"

for tag_name in os.listdir(images_dir):
    tag_path = os.path.join(images_dir, tag_name)
    
    if not os.path.isdir(tag_path):
        continue
    
    # Create tag
    try:
        tag = trainer.create_tag(project_id, tag_name)
        tags[tag_name] = tag
        print(f"✅ Tag utworzony: {tag_name} (ID: {tag.id})")
    except Exception as e:
        # Tag już istnieje
        all_tags = trainer.get_tags(project_id)
        tag = next((t for t in all_tags if t.name == tag_name), None)
        if tag:
            tags[tag_name] = tag
            print(f"✅ Tag znaleziony: {tag_name} (ID: {tag.id})")
        else:
            print(f"❌ Błąd przy tagu {tag_name}: {e}")

# Step 3: Upload images
print("\n[3/4] Wgrywanie obrazów...")
total_uploaded = 0

for tag_name, tag in tags.items():
    tag_path = os.path.join(images_dir, tag_name)
    image_files = [f for f in os.listdir(tag_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
    
    print(f"\n  Tag: {tag_name} ({len(image_files)} obrazów)")
    
    for img_file in image_files:
        img_path = os.path.join(tag_path, img_file)
        
        try:
            with open(img_path, "rb") as f:
                image_data = f.read()
            
            # Upload image
            trainer.create_images_from_data(
                project_id,
                image_data,
                tag_ids=[tag.id]
            )
            print(f"    ✅ {img_file}")
            total_uploaded += 1
        except Exception as e:
            print(f"    ❌ {img_file}: {str(e)[:50]}")

print(f"\n✅ Wgrano łącznie: {total_uploaded} obrazów")

# Step 4: Train model
print("\n[4/4] Trenowanie modelu...")
print("  ⏳ Czekam na trenowanie (może potrwać 1-5 minut)...", end="", flush=True)

try:
    iteration = trainer.train_project(project_id)
    
    # Wait for training to complete
    import time
    iteration_id = iteration.id
    while iteration.status == "Training":
        time.sleep(5)
        iteration = trainer.get_iteration(project_id, iteration_id)
        print(".", end="", flush=True)
    
    print(f"\n✅ Trenowanie ukończone!")
    print(f"   Status: {iteration.status}")
    print(f"   Iteration ID: {iteration_id}")
    
    # Get performance metrics
    try:
        performance = trainer.get_iteration_performance(project_id, iteration_id)
        precision = performance.precision if hasattr(performance, 'precision') else 0
        recall = performance.recall if hasattr(performance, 'recall') else 0
        print(f"   Precision: {precision:.2%}" if precision else "   Precision: N/A")
        print(f"   Recall: {recall:.2%}" if recall else "   Recall: N/A")
    except:
        precision = 0
        recall = 0
        print(f"   Metryki: Niedostępne w Quick Training")
    
    # Save results
    results = {
        "project_id": str(project_id),
        "project_name": PROJECT_NAME,
        "iteration_id": str(iteration_id),
        "status": iteration.status,
        "precision": float(precision) if precision else 0,
        "recall": float(recall) if recall else 0,
        "trained_at": str(iteration.created),
        "tags": {name: str(tag.id) for name, tag in tags.items()},
        "total_images": total_uploaded
    }
    
    with open("training_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Wyniki zapisane do training_results.json")
    print(f"\n{'='*60}")
    print("PODSUMOWANIE:")
    print(f"  Projekt: {PROJECT_NAME}")
    print(f"  Obrazy: {total_uploaded}")
    print(f"  Tagi: {', '.join(tags.keys())}")
    if precision:
        print(f"  Precision: {precision:.2%}")
        print(f"  Recall: {recall:.2%}")
    print(f"{'='*60}")
    
except Exception as e:
    print(f"\n❌ Błąd trenowania: {e}")
    sys.exit(1)
