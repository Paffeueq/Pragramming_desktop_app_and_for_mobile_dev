from PIL import Image
import os

img_path = 'traktor.jpg'
print(f"Original file size: {os.path.getsize(img_path):,} bytes")

# Open and check dimensions
img = Image.open(img_path)
print(f"Original dimensions: {img.size}")
print(f"Original format: {img.format}")

# Resize - max dimension should be around 4096 for Azure
# Traktor is probably very large, let's resize to max 2000px
max_dim = 2000
ratio = min(max_dim / img.size[0], max_dim / img.size[1])
new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))

print(f"New dimensions: {new_size}")

# Resize and save with quality
img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
img_resized.save(img_path, 'JPEG', quality=90)

print(f"New file size: {os.path.getsize(img_path):,} bytes")
print(f"Saved!")
