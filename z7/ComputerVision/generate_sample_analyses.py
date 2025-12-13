#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Computer Vision - Image Analysis
Generowanie przykładowych wyników analizy dla celów demo
"""

import json
from pathlib import Path

def create_sample_vision_analysis(image_name):
    """
    Tworzy przykładowy JSON wynik analizy Vision
    na podstawie nazwy pliku
    """
    
    samples = {
        "honda.jpg": {
            "description": {
                "tags": ["car", "vehicle", "automobile", "sedan", "red"],
                "captions": [
                    {
                        "text": "a red honda car parked on the street",
                        "confidence": 0.8234
                    }
                ]
            },
            "tags": [
                {"name": "car", "confidence": 0.9956},
                {"name": "vehicle", "confidence": 0.9873},
                {"name": "automobile", "confidence": 0.9712},
                {"name": "sedan", "confidence": 0.8534},
                {"name": "red", "confidence": 0.8234},
                {"name": "street", "confidence": 0.7856},
                {"name": "parked", "confidence": 0.7634},
                {"name": "asphalt", "confidence": 0.6234},
                {"name": "transportation", "confidence": 0.5923},
                {"name": "japanese", "confidence": 0.5123}
            ],
            "denseCaptions": {
                "values": [
                    {"text": "red honda sedan", "confidence": 0.8934, "boundingBox": {"x": 0.15, "y": 0.2, "w": 0.7, "h": 0.75}},
                    {"text": "parked on street", "confidence": 0.7834, "boundingBox": {"x": 0.05, "y": 0.3, "w": 0.9, "h": 0.5}},
                    {"text": "vehicle with wheels", "confidence": 0.6934, "boundingBox": {"x": 0.1, "y": 0.4, "w": 0.8, "h": 0.45}},
                    {"text": "sedan bodywork", "confidence": 0.6234, "boundingBox": {"x": 0.2, "y": 0.25, "w": 0.6, "h": 0.5}}
                ]
            },
            "readResult": {
                "blocks": [
                    {
                        "kind": "text",
                        "lines": [
                            {
                                "text": "HONDA",
                                "confidence": 0.9234,
                                "boundingBox": [0.4, 0.1, 0.6, 0.15]
                            }
                        ]
                    }
                ]
            }
        },
        "moza_lisa.jpg": {
            "description": {
                "tags": ["painting", "portrait", "mona lisa", "renaissance", "art"],
                "captions": [
                    {
                        "text": "the mona lisa painting by leonardo da vinci",
                        "confidence": 0.9234
                    }
                ]
            },
            "tags": [
                {"name": "painting", "confidence": 0.9987},
                {"name": "portrait", "confidence": 0.9876},
                {"name": "Mona Lisa", "confidence": 0.9456},
                {"name": "renaissance", "confidence": 0.8765},
                {"name": "artwork", "confidence": 0.8654},
                {"name": "woman", "confidence": 0.8234},
                {"name": "smile", "confidence": 0.7654},
                {"name": "oil painting", "confidence": 0.7456},
                {"name": "historical", "confidence": 0.7234},
                {"name": "famous", "confidence": 0.6234}
            ],
            "denseCaptions": {
                "values": [
                    {"text": "woman with enigmatic smile", "confidence": 0.9345, "boundingBox": {"x": 0.25, "y": 0.15, "w": 0.5, "h": 0.7}},
                    {"text": "renaissance portrait painting", "confidence": 0.8934, "boundingBox": {"x": 0.05, "y": 0.05, "w": 0.9, "h": 0.9}},
                    {"text": "da vinci masterpiece", "confidence": 0.8234, "boundingBox": {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.8}},
                    {"text": "famous artwork on display", "confidence": 0.7634, "boundingBox": {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}}
                ]
            },
            "readResult": None
        },
        "plaza_malo.jpg": {
            "description": {
                "tags": ["plaza", "square", "urban", "crowd", "city"],
                "captions": [
                    {
                        "text": "a crowded public plaza in a city",
                        "confidence": 0.7634
                    }
                ]
            },
            "tags": [
                {"name": "plaza", "confidence": 0.8756},
                {"name": "crowd", "confidence": 0.8234},
                {"name": "urban", "confidence": 0.8123},
                {"name": "square", "confidence": 0.7856},
                {"name": "city", "confidence": 0.7634},
                {"name": "people", "confidence": 0.7456},
                {"name": "public space", "confidence": 0.6934},
                {"name": "gathering", "confidence": 0.6234},
                {"name": "architecture", "confidence": 0.5956},
                {"name": "pavement", "confidence": 0.5234}
            ],
            "denseCaptions": {
                "values": [
                    {"text": "many people in public square", "confidence": 0.8123, "boundingBox": {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.8}},
                    {"text": "crowded plaza with buildings", "confidence": 0.7534, "boundingBox": {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}},
                    {"text": "urban gathering place", "confidence": 0.6934, "boundingBox": {"x": 0.15, "y": 0.2, "w": 0.7, "h": 0.6}}
                ]
            },
            "readResult": None
        },
        "plaza_polska.jpg": {
            "description": {
                "tags": ["plaza", "poland", "warsaw", "historic", "square"],
                "captions": [
                    {
                        "text": "historic plaza in warsaw poland with traditional architecture",
                        "confidence": 0.8456
                    }
                ]
            },
            "tags": [
                {"name": "plaza", "confidence": 0.8934},
                {"name": "historic", "confidence": 0.8723},
                {"name": "Warsaw", "confidence": 0.8456},
                {"name": "architecture", "confidence": 0.8234},
                {"name": "Poland", "confidence": 0.7956},
                {"name": "square", "confidence": 0.7834},
                {"name": "buildings", "confidence": 0.7456},
                {"name": "street", "confidence": 0.7123},
                {"name": "european", "confidence": 0.6934},
                {"name": "monument", "confidence": 0.6234}
            ],
            "denseCaptions": {
                "values": [
                    {"text": "warsaw old town square", "confidence": 0.8756, "boundingBox": {"x": 0.1, "y": 0.15, "w": 0.8, "h": 0.75}},
                    {"text": "historic polish architecture", "confidence": 0.8234, "boundingBox": {"x": 0.05, "y": 0.1, "w": 0.9, "h": 0.8}},
                    {"text": "european plaza with historic buildings", "confidence": 0.7634, "boundingBox": {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}},
                    {"text": "traditional polish square", "confidence": 0.7123, "boundingBox": {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.8}}
                ]
            },
            "readResult": {
                "blocks": [
                    {
                        "kind": "text",
                        "lines": [
                            {
                                "text": "Warszawa",
                                "confidence": 0.9456,
                                "boundingBox": [0.3, 0.05, 0.7, 0.12]
                            },
                            {
                                "text": "Rynek Starego Miasta",
                                "confidence": 0.8934,
                                "boundingBox": [0.25, 0.12, 0.75, 0.19]
                            }
                        ]
                    }
                ]
            }
        },
        "traktor.jpg": {
            "description": {
                "tags": ["tractor", "farm", "agriculture", "vehicle", "equipment"],
                "captions": [
                    {
                        "text": "a red tractor in a farm field",
                        "confidence": 0.8734
                    }
                ]
            },
            "tags": [
                {"name": "tractor", "confidence": 0.9845},
                {"name": "farm", "confidence": 0.9234},
                {"name": "agriculture", "confidence": 0.8956},
                {"name": "vehicle", "confidence": 0.8723},
                {"name": "machinery", "confidence": 0.8456},
                {"name": "field", "confidence": 0.8234},
                {"name": "red", "confidence": 0.7956},
                {"name": "equipment", "confidence": 0.7634},
                {"name": "harvest", "confidence": 0.7123},
                {"name": "soil", "confidence": 0.6234}
            ],
            "denseCaptions": {
                "values": [
                    {"text": "red farm tractor in field", "confidence": 0.9234, "boundingBox": {"x": 0.2, "y": 0.25, "w": 0.6, "h": 0.5}},
                    {"text": "agricultural machinery working", "confidence": 0.8634, "boundingBox": {"x": 0.1, "y": 0.2, "w": 0.8, "h": 0.6}},
                    {"text": "tractor wheels on soil", "confidence": 0.7934, "boundingBox": {"x": 0.15, "y": 0.5, "w": 0.7, "h": 0.45}},
                    {"text": "farming equipment in use", "confidence": 0.7234, "boundingBox": {"x": 0.05, "y": 0.1, "w": 0.9, "h": 0.8}}
                ]
            },
            "readResult": {
                "blocks": [
                    {
                        "kind": "text",
                        "lines": [
                            {
                                "text": "John Deere",
                                "confidence": 0.8734,
                                "boundingBox": [0.3, 0.1, 0.7, 0.18]
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    return samples.get(image_name, {})


def generate_all_sample_analyses():
    """Generuje sample JSON-y dla wszystkich obrazów"""
    
    image_files = ["honda.jpg", "moza_lisa.jpg", "plaza_malo.jpg", "plaza_polska.jpg", "traktor.jpg"]
    
    print("📋 Generowanie sample wyników analizy Vision...")
    print("="*80)
    
    for image_file in image_files:
        sample = create_sample_vision_analysis(image_file)
        
        if sample:
            output_file = Path(image_file).stem + "_analysis.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(sample, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Utworzono: {output_file}")
    
    print("="*80)
    print("✅ Wszystkie sample analizy zostały utworzone!")
    print("\nLe to są dane symulowane dla celów demonstracyjnych.")
    print("W produkcji należałoby użyć bezpośrednio Azure Vision API.")


if __name__ == "__main__":
    generate_all_sample_analyses()
