import os
from PIL import Image

thumb_dir = r"D:\csv\static\thumbnails\firstpage"
source_root = r"D:\NormalizedModeFacsimiles"
target_dpi = (250, 250)
valid_exts = [".tif", ".tiff", ".jpg", ".jpeg", ".png"]

def find_folder_by_name(root, target_name):
    for dirpath, dirnames, _ in os.walk(root):
        for dirname in dirnames:
            if dirname == target_name:
                return os.path.join(dirpath, dirname)
    return None

def find_page_001_image(folder):
    for file in os.listdir(folder):
        if file.lower().startswith("page_001"):
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_exts:
                return os.path.join(folder, file)
    return None

for thumb_file in os.listdir(thumb_dir):
    thumb_path = os.path.join(thumb_dir, thumb_file)
    stem = os.path.splitext(thumb_file)[0]

    matched_folder = find_folder_by_name(source_root, stem)
    if not matched_folder:
        print(f"⚠️ No folder match for: {stem}")
        continue

    source_path = find_page_001_image(matched_folder)
    if not source_path:
        print(f"⚠️ No Page_001 image in: {matched_folder}")
        continue

    try:
        with Image.open(thumb_path) as thumb_img:
            target_size = thumb_img.size
            upscale_size = (target_size[0] * 2, target_size[1] * 2)

        with Image.open(source_path) as source_img:
            source_img = source_img.convert("RGB")
            source_img = source_img.resize(upscale_size, Image.LANCZOS)
            source_img.save(thumb_path, dpi=target_dpi)
            print(f"✅ Replaced: {thumb_file} with upscaled {os.path.basename(source_path)}")
    except Exception as e:
        print(f"❌ Error processing {thumb_file}: {e}")