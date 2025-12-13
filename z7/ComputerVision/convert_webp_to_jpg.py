#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konwersja WEBP -> JPG
"""

from PIL import Image
from pathlib import Path

def convert_webp_to_jpg(webp_path):
    """Konwertuje WEBP na JPG"""
    
    webp_file = Path(webp_path)
    jpg_file = webp_file.stem + ".jpg"
    
    try:
        # Otwórz WEBP
        img = Image.open(webp_file)
        
        # Konwertuj na RGB jeśli ma alpha channel
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Zapisz jako JPG
        img.save(jpg_file, 'JPEG', quality=95)
        
        print(f"✅ {webp_file.name:25s} -> {jpg_file:25s} ({Path(jpg_file).stat().st_size} bytes)")
        return jpg_file
    
    except Exception as e:
        print(f"❌ {webp_file.name:25s} - Błąd: {e}")
        return None


def main():
    print("\n📸 Konwersja WEBP -> JPG")
    print("="*80)
    
    # Znajdź wszystkie pliki WEBP
    webp_files = list(Path(".").glob("*.webp"))
    
    if not webp_files:
        # Sprawdź czy to mogą być JPG z rozszerzeniem .jpg ale rzeczywiście WEBP
        jpg_files = list(Path(".").glob("*.jpg"))
        
        print(f"\nZnaleziono plików 'jpg': {len(jpg_files)}")
        for f in jpg_files:
            print(f"  - {f.name}")
            
            # Sprawdź format
            try:
                img = Image.open(f)
                print(f"    Format: {img.format}")
            except:
                pass
        
        return
    
    print(f"\nZnaleziono {len(webp_files)} plików WEBP\n")
    
    converted = 0
    for webp_file in webp_files:
        jpg_file = convert_webp_to_jpg(webp_file)
        if jpg_file:
            converted += 1
            # Usuń oryginalny WEBP
            webp_file.unlink()
            print(f"   (Original WEBP usunięty)")
    
    print("\n" + "="*80)
    print(f"✅ Skonwertowano {converted} plików\n")


if __name__ == "__main__":
    main()
