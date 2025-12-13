#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konwersja WEBP (named as .jpg) -> Proper JPG
"""

from PIL import Image
from pathlib import Path
import os

def convert_webp_to_proper_jpg(jpg_path):
    """Sprawdza format i konwertuje WEBP na JPG jeśli trzeba"""
    
    jpg_file = Path(jpg_path)
    
    try:
        # Otwórz plik
        img = Image.open(jpg_file)
        
        # Jeśli to WEBP, konwertuj
        if img.format == 'WEBP':
            print(f"🔄 {jpg_file.name:25s} (WEBP -> JPEG)")
            
            # Konwertuj na RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            # Zapisz jako JPG
            temp_file = jpg_file.stem + "_temp.jpg"
            img.save(temp_file, 'JPEG', quality=95)
            
            # Zamień oryginał
            os.remove(jpg_file)
            os.rename(temp_file, jpg_file)
            
            print(f"   ✅ Konwersja ukończona ({Path(jpg_file).stat().st_size} bytes)")
            return True
        
        elif img.format == 'JPEG':
            print(f"✅ {jpg_file.name:25s} (już JPEG)")
            return False
        
        else:
            print(f"❓ {jpg_file.name:25s} (Format: {img.format})")
            return False
    
    except Exception as e:
        print(f"❌ {jpg_file.name:25s} - Błąd: {e}")
        return False


def main():
    print("\n📸 Konwersja plików na prawidłowy JPG")
    print("="*80 + "\n")
    
    jpg_files = list(Path(".").glob("*.jpg"))
    
    if not jpg_files:
        print("Nie znaleziono plików .jpg")
        return
    
    print(f"Przetwarzam {len(jpg_files)} plików:\n")
    
    converted_count = 0
    for jpg_file in sorted(jpg_files):
        if convert_webp_to_proper_jpg(jpg_file):
            converted_count += 1
    
    print("\n" + "="*80)
    print(f"✅ Skonwertowano: {converted_count} plików\n")


if __name__ == "__main__":
    main()
