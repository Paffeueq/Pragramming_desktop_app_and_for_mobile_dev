#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Computer Vision - Image Analysis Display
Wyświetlanie wyników analizy Vision z JSON files
"""

import json
from pathlib import Path


def print_analysis_results(filename, result):
    """
    Wypisuje wyniki analizy w czytelnym formacie
    """
    
    print("\n" + "="*90)
    print(f"📷 WYNIKI ANALIZY: {filename}")
    print("="*90)
    
    if not result:
        print("❌ Nie udało się załadować wyniku")
        return
    
    # ===== TAGI =====
    if "tags" in result and result["tags"]:
        print("\n📌 TAGI (Tags):")
        print("-" * 90)
        
        tags = result["tags"]
        print(f"Liczba tagów: {len(tags)}\n")
        
        for idx, tag in enumerate(tags[:8], 1):  # Pierwsze 8 tagów
            name = tag.get("name", "N/A")
            confidence = tag.get("confidence", 0.0)
            bar = "█" * int(confidence * 20) + "░" * (20 - int(confidence * 20))
            print(f"  {idx}. {name:20s} │{bar}│ {confidence:6.2%}")
    
    # ===== OPIS KRÓTKI (Caption) =====
    if "description" in result:
        desc = result["description"]
        captions = desc.get("captions", [])
        
        if captions:
            print("\n\n📝 OPIS KRÓTKI (Caption):")
            print("-" * 90)
            
            caption = captions[0]
            text = caption.get("text", "N/A")
            confidence = caption.get("confidence", 0.0)
            
            print(f"\nTekst:\n  \"{text}\"")
            print(f"\nConfidence: {confidence:.2%}")
    
    # ===== DENSE CAPTIONS =====
    if "denseCaptions" in result:
        dense = result["denseCaptions"]
        
        if dense and dense.get("values"):
            print("\n\n📍 DENSE CAPTIONS (Gęste napisy):")
            print("-" * 90)
            
            captions_list = dense["values"]
            print(f"Liczba dense captions: {len(captions_list)}\n")
            
            for idx, cap in enumerate(captions_list, 1):
                text = cap.get("text", "N/A")
                confidence = cap.get("confidence", 0.0)
                bounds = cap.get("boundingBox", {})
                
                bar = "█" * int(confidence * 20) + "░" * (20 - int(confidence * 20))
                
                print(f"  Caption #{idx}:")
                print(f"    Tekst: \"{text}\"")
                print(f"    Conf:  │{bar}│ {confidence:.2%}")
                if bounds:
                    print(f"    Box:   x={bounds.get('x', 0):.2f}, y={bounds.get('y', 0):.2f}, "
                          f"w={bounds.get('w', 0):.2f}, h={bounds.get('h', 0):.2f}")
                print()
    
    # ===== OCR (READ) =====
    if "readResult" in result and result["readResult"]:
        read = result["readResult"]
        
        if read and read.get("blocks"):
            print("\n\n🔤 OCR (Odczytany tekst):")
            print("-" * 90)
            
            blocks = read["blocks"]
            extracted_text = []
            
            for block in blocks:
                if block.get("kind") == "text":
                    for line in block.get("lines", []):
                        text = line.get("text", "")
                        confidence = line.get("confidence", 0.0)
                        
                        if text:
                            bar = "█" * int(confidence * 15) + "░" * (15 - int(confidence * 15))
                            extracted_text.append(text)
                            print(f"  \"{text}\"")
                            print(f"    Confidence: │{bar}│ {confidence:.2%}\n")
            
            if not extracted_text:
                print("  (Brak tekstu do odczytania)")
    else:
        print("\n\n🔤 OCR (Odczytany tekst):")
        print("-" * 90)
        print("  (Brak tekstu do odczytania na tym obrazie)")
    
    print("\n" + "="*90 + "\n")


def compare_image_qualities(all_results):
    """
    Porównanie jakości wyników dla różnych obrazów
    """
    
    print("\n\n" + "="*90)
    print("📊 PORÓWNANIE WYNIKÓW ANALIZY")
    print("="*90)
    
    print("\n{:<18} {:<10} {:<8} {:<12} {:<15} {:<12}".format(
        "Plik", "Rozmiar", "Tagi", "Avg Tag C", "Caption C", "Dense Caps"
    ))
    print("-" * 90)
    
    for result_info in all_results:
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
        
        # OCR dostępny?
        has_ocr = "✓" if result.get("readResult") and result["readResult"].get("blocks") else "✗"
        
        print("{:<18} {:<10} {:<8} {:<12.1%} {:<15.1%} {:<12} {}".format(
            filename[:17],
            f"{file_size} KB",
            num_tags,
            avg_tag_conf,
            caption_conf,
            num_dense,
            f"OCR:{has_ocr}"
        ))
    
    print("="*90)
    print("\n")


def get_image_file_size(image_path):
    """Zwraca rozmiar pliku w KB"""
    return round(Path(image_path).stat().st_size / 1024, 2)


def load_analysis_from_json(json_file):
    """Ładuje wynik analizy z pliku JSON"""
    
    if not Path(json_file).exists():
        return None
    
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """Główna funkcja"""
    
    print("\n🔍 Azure Computer Vision - Image Analysis Results")
    print("="*90)
    
    # Znajduje pliki JSON
    json_files = list(Path(".").glob("*_analysis.json"))
    
    if not json_files:
        print("⚠️  Nie znaleziono plików *_analysis.json")
        return
    
    print(f"Znaleziono {len(json_files)} wyników analizy\n")
    
    results_summary = []
    
    for json_file in sorted(json_files):
        # Wczytanie wyniku
        result = load_analysis_from_json(json_file)
        
        if result:
            # Wyświetlenie wyniku
            print_analysis_results(json_file.name, result)
            
            # Powiązanie z obrazem
            image_name = json_file.stem.replace("_analysis", "")
            image_path = Path(image_name + ".jpg")
            
            if image_path.exists():
                file_size = get_image_file_size(image_path)
            else:
                file_size = 0
            
            # Dodanie do podsumowania
            results_summary.append({
                "file": image_name,
                "size_kb": file_size,
                "result": result
            })
    
    # Porównanie wyników
    if results_summary:
        compare_image_qualities(results_summary)
    
    print("✅ Wyświetlanie wyników zakończone!")
    print("="*90 + "\n")


if __name__ == "__main__":
    main()
