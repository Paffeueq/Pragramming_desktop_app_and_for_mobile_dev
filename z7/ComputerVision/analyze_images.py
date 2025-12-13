#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Computer Vision - Image Analysis
Analiza obrazów: tagi, opisy, Dense Captions, OCR, język
"""

import json
import requests
import base64
from pathlib import Path
from datetime import datetime

# Konfiguracja Azure Computer Vision
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"
API_KEY = "F4dlBsL5YqaX5UfXjGTRrQvcUMkbpStm061JDKR6WO9B7cqpCChsJQQJ99BLACYeBjFXJ3w3AAAFACOGyxWV"
REGION = "eastus"
API_VERSION = "2021-04-01"

# Parametry analizy
FEATURES = [
    "tags",           # Tagi obiektów
    "description",    # Opis całego obrazu
    "read",           # OCR - odczyt tekstu
    "dense-captions", # Gęste napisy (Dense Captions)
]

LANGUAGE = "en"  # Język analizy


def analyze_image_from_file(image_path):
    """
    Wysyła obraz z dysku do Azure Vision API
    """
    
    if not Path(image_path).exists():
        print(f"❌ Plik nie znaleziony: {image_path}")
        return None
    
    # Endpoint
    url = f"{ENDPOINT}vision/v3.2/analyze?api-version={API_VERSION}&features=Tags,Description,Faces,ImageType,Objects,Brands,Color,Categories"
    
    params = {
        "language": LANGUAGE,
        "details": "landmarks,celebrities",
    }
    
    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": API_KEY
    }
    
    # Odczyt pliku
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    print(f"\n📤 Wysyłam: {Path(image_path).name} ({len(image_data)} bytes)")
    
    try:
        response = requests.post(url, headers=headers, params=params, data=image_data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Analiza zakończona pomyślnie")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd API: {e}")
        return None


def extract_key_info(result):
    """
    Wyodrębnia kluczowe informacje z wyniku analizy
    """
    
    if not result:
        return None
    
    extracted = {
        "tags": result.get("tags", []),
        "description": result.get("description", {}),
        "captions": result.get("captions", []),
        "dense_captions": result.get("denseCaptions", []),
        "read_results": result.get("readResult", {}),
    }
    
    return extracted


def print_analysis_results(filename, result):
    """
    Wypisuje wyniki analizy w czytelnym formacie
    """
    
    print("\n" + "="*80)
    print(f"📷 WYNIKI ANALIZY: {filename}")
    print("="*80)
    
    if not result:
        print("❌ Nie udało się przeanalizować obrazu")
        return
    
    # ===== TAGI =====
    if "tags" in result and result["tags"]:
        print("\n📌 TAGI (Tags):")
        print("-" * 80)
        
        tags = result["tags"]
        print(f"Liczba tagów: {len(tags)}\n")
        
        for tag in tags[:10]:  # Pierwsze 10 tagów
            name = tag.get("name", "N/A")
            confidence = tag.get("confidence", 0.0)
            print(f"  • {name:30s} | Confidence: {confidence:6.2%}")
    
    # ===== OPIS KRÓTKI (Caption) =====
    if "description" in result:
        desc = result["description"]
        captions = desc.get("captions", [])
        
        if captions:
            print("\n\n📝 OPIS KRÓTKI (Caption):")
            print("-" * 80)
            
            caption = captions[0]
            text = caption.get("text", "N/A")
            confidence = caption.get("confidence", 0.0)
            
            print(f"\nTekst:\n  {text}")
            print(f"\nConfidence: {confidence:.2%}")
    
    # ===== DENSE CAPTIONS =====
    if "denseCaptions" in result:
        dense = result["denseCaptions"]
        
        if dense.get("values"):
            print("\n\n📍 DENSE CAPTIONS (Gęste napisy):")
            print("-" * 80)
            
            captions_list = dense["values"]
            print(f"Liczba dense captions: {len(captions_list)}\n")
            
            for idx, cap in enumerate(captions_list[:5], 1):  # Pierwsze 5
                text = cap.get("text", "N/A")
                confidence = cap.get("confidence", 0.0)
                bounds = cap.get("boundingBox", {})
                
                print(f"  Caption #{idx}:")
                print(f"    Tekst: {text}")
                print(f"    Confidence: {confidence:.2%}")
                if bounds:
                    print(f"    Lokalizacja: x={bounds.get('x')}, y={bounds.get('y')}, "
                          f"w={bounds.get('w')}, h={bounds.get('h')}")
                print()
    
    # ===== OCR (READ) =====
    if "readResult" in result:
        read = result["readResult"]
        
        if read and read.get("blocks"):
            print("\n\n🔤 OCR (Odczytany tekst):")
            print("-" * 80)
            
            blocks = read["blocks"]
            extracted_text = []
            
            for block in blocks:
                if block.get("kind") == "text":
                    for line in block.get("lines", []):
                        text = line.get("text", "")
                        confidence = line.get("confidence", 0.0)
                        
                        if text:
                            extracted_text.append(text)
                            print(f"  {text}")
                            print(f"    └─ Confidence: {confidence:.2%}\n")
            
            if not extracted_text:
                print("  (Brak tekstu do odczytania)")
    
    # ===== METADATA =====
    print("\n\n📊 METADATA:")
    print("-" * 80)
    print(f"Model ID: {result.get('modelVersion', 'N/A')}")
    print(f"Request ID: {result.get('requestId', 'N/A')}")
    
    print("\n" + "="*80 + "\n")


def save_json_results(filename, result):
    """
    Zapisuje pełny JSON rezultat do pliku
    """
    
    output_file = Path(filename).stem + "_analysis.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Wynik zapisany: {output_file}")
    return output_file


def get_image_file_size(image_path):
    """
    Zwraca rozmiar pliku w KB
    """
    return round(Path(image_path).stat().st_size / 1024, 2)


def compare_image_qualities(results_summary):
    """
    Porównanie jakości wyników dla różnych obrazów
    """
    
    print("\n\n" + "="*80)
    print("📊 PORÓWNANIE WYNIKÓW ANALIZY")
    print("="*80)
    
    print("\n{:<20} {:<12} {:<8} {:<15} {:<15} {:<15}".format(
        "Plik", "Rozmiar", "Tagi", "Avg Tag Conf", "Caption Conf", "Dense Caps"
    ))
    print("-" * 80)
    
    for result_info in results_summary:
        filename = result_info["file"]
        file_size = result_info["size_kb"]
        result = result_info["result"]
        
        if not result:
            continue
        
        # Liczba tagów
        num_tags = len(result.get("tags", []))
        
        # Średnie confidence tagów
        if result.get("tags"):
            avg_tag_conf = sum(t.get("confidence", 0) for t in result["tags"]) / len(result["tags"])
        else:
            avg_tag_conf = 0
        
        # Confidence caption
        caption_conf = 0
        if result.get("description", {}).get("captions"):
            caption_conf = result["description"]["captions"][0].get("confidence", 0)
        
        # Liczba dense captions
        num_dense = len(result.get("denseCaptions", {}).get("values", []))
        
        print("{:<20} {:<12} {:<8} {:<15.1%} {:<15.1%} {:<15}".format(
            filename[:19],
            f"{file_size} KB",
            num_tags,
            avg_tag_conf,
            caption_conf,
            num_dense
        ))
    
    print("="*80 + "\n")


def main():
    """
    Główna funkcja - analiza wszystkich obrazów
    """
    
    print("\n🔍 Azure Computer Vision - Image Analysis")
    print("="*80)
    
    # Lista obrazów do analizy
    image_files = list(Path(".").glob("*.jpg")) + list(Path(".").glob("*.png"))
    image_files = [str(f) for f in image_files]
    
    if not image_files:
        print("⚠️  Nie znaleziono obrazów (*.jpg, *.png)")
        return
    
    print(f"Znaleziono {len(image_files)} obrazów do analizy\n")
    
    results_summary = []
    
    for image_file in image_files:
        image_path = Path(image_file)
        file_size = get_image_file_size(image_file)
        
        # Analiza obrazu
        result = analyze_image_from_file(image_file)
        
        if result:
            # Wyświetlenie wyników
            print_analysis_results(image_file, result)
            
            # Zapis JSON
            json_file = save_json_results(image_file, result)
            
            # Dodanie do podsumowania
            results_summary.append({
                "file": image_path.name,
                "size_kb": file_size,
                "result": result
            })
    
    # Porównanie wyników
    if results_summary:
        compare_image_qualities(results_summary)
    
    print("✅ Analiza zakończona!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
