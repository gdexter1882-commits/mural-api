import os
import pandas as pd

# === CONFIGURATION ===
csv_path = r"D:\csv\mural_master.csv"  # Path to your original CSV
thumbnail_dir = r"D:\thumbnails\firstpage"  # Local folder with thumbnail images
base_url = "https://mural-api.onrender.com/static/thumbnails/firstpage"  # Public Render URL

# === LOAD CSV ===
df = pd.read_csv(csv_path)
df["Image"] = ""  # Add empty column if not already present

# === BUILD HANDLE → IMAGE MAP ===
available_images = {
    os.path.splitext(f)[0].lower(): f
    for f in os.listdir(thumbnail_dir)
    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
}

# === MATCH AND UPDATE ===
for i, row in df.iterrows():
    handle = str(row.get("Handle", "")).strip().lower()
    if handle in available_images:
        filename = available_images[handle]
        df.at[i, "Image"] = f"{base_url}/{filename}"

# === OVERWRITE ORIGINAL CSV ===
df.to_csv(csv_path, index=False, encoding="utf-8")
print(f"✅ mural_master.csv updated with image URLs.")