from PIL import Image
import os
import json

# Load slug-to-image map
with open("slug_to_image_map.json", "r", encoding="utf-8") as f:
    slug_map = json.load(f)

output_dir = "converted_images"
os.makedirs(output_dir, exist_ok=True)

for slug, tif_path in slug_map.items():
    try:
        img = Image.open(tif_path)
        rgb_img = img.convert("RGB")
        output_path = os.path.join(output_dir, f"{slug}.jpg")
        rgb_img.save(output_path, "JPEG", quality=95)
        print(f"✅ Converted: {slug}")
    except Exception as e:
        print(f"❌ Failed: {slug} → {e}")