import os
import re
import unicodedata
import json

SOURCE_ROOT = r"D:\NormalizedModeFacsimiles"
OUTPUT_JSON = "slug_to_image_map.json"

def slugify(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.lower().strip("-")

slug_to_image = {}

for root, dirs, files in os.walk(SOURCE_ROOT):
    for f in files:
        if f.lower() == "page_001.tif":
            folder_name = os.path.basename(root)
            slug = slugify(folder_name)
            full_path = os.path.join(root, f)
            slug_to_image[slug] = full_path.replace("\\", "/")

# Save to JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(slug_to_image, f, indent=2)

print(f"✅ Saved {len(slug_to_image)} entries to {OUTPUT_JSON}")