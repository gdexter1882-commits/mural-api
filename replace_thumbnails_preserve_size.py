import os
from PIL import Image

thumb_dir = r"D:\csv\static\thumbnails\firstpage"
source_root = r"D:\NormalizedModeFacsimiles"
target_dpi = (250, 250)

# Build a stem-to-path map from all source images
source_map = {}
for root, _, files in os.walk(source_root):
    for file in files:
        stem = os.path.splitext(file)[0]
        full_path = os.path.join(root, file)
        source_map[stem] = full_path

# Process each thumbnail
for thumb_file in os.listdir(thumb_dir):
    thumb_path = os.path.join(thumb_dir, thumb_file)
    stem = os.path.splitext(thumb_file)[0]

    # Find matching source by stem
    source_path = source_map.get(stem)
    if not source_path:
        print(f"⚠️ No match found for: {thumb_file}")
        continue

    try:
        # Get target pixel dimensions from thumbnail
        with Image.open(thumb_path) as thumb_img:
            target_size = thumb_img.size

        # Open source image and resize
        with Image.open(source_path) as source_img:
            resized = source_img.resize(target_size, Image.LANCZOS)
            resized = resized.convert("RGB")  # Ensure JPEG-compatible
            resized.save(thumb_path, dpi=target_dpi)
            print(f"✅ Replaced: {thumb_file} from {os.path.basename(source_path)}")
    except Exception as e:
        print(f"❌ Error processing {thumb_file}: {e}")