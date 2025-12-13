#!/usr/bin/env python3
"""
Generate sample images for Object Detection training with bounding box annotations
Tworzy obrazy z różnymi obiektami i generuje XML anotacje (Pascal VOC format)
"""

from PIL import Image, ImageDraw, ImageFont
import random
from pathlib import Path
import xml.etree.ElementTree as ET

def create_sample_image_with_objects(filename, width=640, height=480):
    """Create a sample image with multiple objects"""
    
    # Create blank image
    img = Image.new('RGB', (width, height), color=(200, 220, 240))
    draw = ImageDraw.Draw(img)
    
    objects = []
    
    # Draw random rectangles for different objects
    # Object 1: OSOBA (person) - vertical rectangle
    x1_person, y1_person = random.randint(50, 150), random.randint(30, 80)
    x2_person, y2_person = x1_person + random.randint(60, 100), y1_person + random.randint(150, 200)
    
    # Head
    draw.ellipse([x1_person+10, y1_person, x1_person+50, y1_person+40], fill=(255, 200, 160), outline=(0,0,0))
    # Body
    draw.rectangle([x1_person+15, y1_person+40, x1_person+45, y1_person+120], fill=(0, 100, 200), outline=(0,0,0))
    # Legs
    draw.rectangle([x1_person+18, y1_person+120, x1_person+30, y1_person+180], fill=(50, 50, 50), outline=(0,0,0))
    draw.rectangle([x1_person+32, y1_person+120, x1_person+42, y1_person+180], fill=(50, 50, 50), outline=(0,0,0))
    
    # Draw bounding box around person
    draw.rectangle([x1_person, y1_person, x2_person, y2_person], outline=(255, 0, 0), width=2)
    
    objects.append({
        'name': 'osoba',
        'xmin': x1_person,
        'ymin': y1_person,
        'xmax': x2_person,
        'ymax': y2_person
    })
    
    # Object 2: SAMOCHOD (car)
    x1_car, y1_car = random.randint(250, 400), random.randint(200, 300)
    x2_car, y2_car = x1_car + random.randint(150, 200), y1_car + random.randint(80, 120)
    
    # Car body
    draw.rectangle([x1_car, y1_car+30, x2_car, y1_car+80], fill=(200, 0, 0), outline=(0,0,0), width=2)
    # Car top
    draw.rectangle([x1_car+30, y1_car, x2_car-30, y1_car+30], fill=(180, 0, 0), outline=(0,0,0), width=2)
    # Wheels
    draw.ellipse([x1_car+20, y1_car+75, x1_car+50, y1_car+105], fill=(30, 30, 30), outline=(0,0,0))
    draw.ellipse([x2_car-50, y1_car+75, x2_car-20, y1_car+105], fill=(30, 30, 30), outline=(0,0,0))
    # Windows
    draw.rectangle([x1_car+35, y1_car+5, x1_car+55, y1_car+25], fill=(100, 150, 200), outline=(0,0,0))
    
    # Draw bounding box around car
    draw.rectangle([x1_car, y1_car, x2_car, y2_car], outline=(0, 255, 0), width=2)
    
    objects.append({
        'name': 'samochod',
        'xmin': x1_car,
        'ymin': y1_car,
        'xmax': x2_car,
        'ymax': y2_car
    })
    
    # Object 3: PIES (dog)
    x1_dog, y1_dog = random.randint(100, 250), random.randint(300, 400)
    x2_dog, y2_dog = x1_dog + random.randint(80, 120), y1_dog + random.randint(60, 100)
    
    # Dog body
    draw.ellipse([x1_dog+10, y1_dog+20, x2_dog-10, y1_dog+60], fill=(139, 69, 19), outline=(0,0,0), width=2)
    # Dog head
    draw.ellipse([x2_dog-50, y1_dog, x2_dog, y1_dog+40], fill=(160, 82, 45), outline=(0,0,0), width=2)
    # Ears
    draw.polygon([x2_dog-45, y1_dog, x2_dog-35, y1_dog-20, x2_dog-25, y1_dog], fill=(139, 69, 19))
    draw.polygon([x2_dog-10, y1_dog, x2_dog, y1_dog-20, x2_dog+10, y1_dog], fill=(139, 69, 19))
    # Tail
    draw.arc([x1_dog-40, y1_dog+30, x1_dog+10, y1_dog+70], 0, 180, fill=(139, 69, 19), width=8)
    # Legs
    draw.rectangle([x1_dog+15, y1_dog+55, x1_dog+25, y2_dog], fill=(100, 50, 0), outline=(0,0,0))
    draw.rectangle([x1_dog+35, y1_dog+55, x1_dog+45, y2_dog], fill=(100, 50, 0), outline=(0,0,0))
    draw.rectangle([x2_dog-35, y1_dog+55, x2_dog-25, y2_dog], fill=(100, 50, 0), outline=(0,0,0))
    draw.rectangle([x2_dog-15, y1_dog+55, x2_dog-5, y2_dog], fill=(100, 50, 0), outline=(0,0,0))
    
    # Draw bounding box around dog
    draw.rectangle([x1_dog, y1_dog, x2_dog, y2_dog], outline=(0, 0, 255), width=2)
    
    objects.append({
        'name': 'pies',
        'xmin': x1_dog,
        'ymin': y1_dog,
        'xmax': x2_dog,
        'ymax': y2_dog
    })
    
    # Add labels to image
    try:
        font = ImageFont.load_default()
        draw.text((10, 10), f"Objects: osoba, samochod, pies", fill=(0, 0, 0), font=font)
    except:
        pass
    
    return img, objects

def create_xml_annotation(filename, objects, width=640, height=480):
    """Create Pascal VOC XML annotation"""
    
    annotation = ET.Element('annotation')
    
    # Filename
    fn_elem = ET.SubElement(annotation, 'filename')
    fn_elem.text = filename
    
    # Size
    size_elem = ET.SubElement(annotation, 'size')
    width_elem = ET.SubElement(size_elem, 'width')
    width_elem.text = str(width)
    height_elem = ET.SubElement(size_elem, 'height')
    height_elem.text = str(height)
    depth_elem = ET.SubElement(size_elem, 'depth')
    depth_elem.text = '3'
    
    # Objects
    for obj in objects:
        obj_elem = ET.SubElement(annotation, 'object')
        
        name_elem = ET.SubElement(obj_elem, 'name')
        name_elem.text = obj['name']
        
        bndbox_elem = ET.SubElement(obj_elem, 'bndbox')
        
        xmin = ET.SubElement(bndbox_elem, 'xmin')
        xmin.text = str(int(obj['xmin']))
        
        ymin = ET.SubElement(bndbox_elem, 'ymin')
        ymin.text = str(int(obj['ymin']))
        
        xmax = ET.SubElement(bndbox_elem, 'xmax')
        xmax.text = str(int(obj['xmax']))
        
        ymax = ET.SubElement(bndbox_elem, 'ymax')
        ymax.text = str(int(obj['ymax']))
    
    return annotation

def generate_dataset(num_images=10):
    """Generate sample dataset with images and annotations"""
    
    print("="*70)
    print("GENEROWANIE PRZYKŁADOWEGO DATASETU - OBJECT DETECTION")
    print("="*70)
    
    training_dir = Path("training_images")
    training_dir.mkdir(exist_ok=True)
    
    print(f"\nTworzę {num_images} obrazów treningowych z anotacjami...")
    
    for i in range(num_images):
        # Generate image with objects
        img, objects = create_sample_image_with_objects(f"sample_{i+1}.jpg")
        
        # Save image
        img_path = training_dir / f"sample_{i+1}.jpg"
        img.save(img_path)
        print(f"  OK {img_path.name} - {len(objects)} obiekty")
        
        # Create and save XML annotation
        annotation = create_xml_annotation(f"sample_{i+1}.jpg", objects)
        xml_path = training_dir / f"sample_{i+1}.xml"
        tree = ET.ElementTree(annotation)
        tree.write(xml_path, encoding='utf-8', xml_declaration=True)
    
    print(f"\nOK - Dataset wygenerowany w: {training_dir.absolute()}")
    print(f"  - {num_images} obrazów JPG")
    print(f"  - {num_images} plików XML (anotacje)")
    
    # Create test images
    print(f"\nTworzę obrazy testowe...")
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    for i in range(3):
        img, objects = create_sample_image_with_objects(f"test_{i+1}.jpg")
        test_path = test_dir / f"test_{i+1}.jpg"
        img.save(test_path)
        print(f"  OK {test_path.name}")
    
    print(f"\nOK - Test set wygenerowany w: {test_dir.absolute()}")
    
    print("\n" + "="*70)
    print("NASTĘPNE KROKI:")
    print("="*70)
    print("""
1. Dataset jest gotowy do trenowania!
2. Uruchom: python train_detection_v2.py
3. Model zostanie wytrenowany na 10 obrazach
4. Potem testujesz na 3 obrazach testowych
""")

if __name__ == "__main__":
    generate_dataset(num_images=30)
