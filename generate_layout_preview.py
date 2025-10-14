import os
from PIL import Image, ImageDraw, ImageFont
import math
import csv

LOWRES_ROOT = r"D:\LowResFacsimiles"
CSV_PATH = r"D:\csv\mural_master.csv"
PREVIEW_OUT_DIR = os.path.join("static", "previews")

def generate_preview(handle):
    print(f"\n🔧 Starting preview for: {handle}")

    # Find matching row in CSV
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next((r for r in reader if r["Handle"].strip() == handle), None)
        if not row:
            print(f"❌ Handle not found in CSV: {handle}")
            return

    folder_path = os.path.join(LOWRES_ROOT, handle)
    if not os.path.isdir(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return

    tiffs = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".tif", ".tiff"))
    ])

    if not tiffs:
        print(f"⚠️ No TIFFs found in {folder_path}")
        return

    os.makedirs(PREVIEW_OUT_DIR, exist_ok=True)

    # Layout grid
    num_pages = len(tiffs)
    cols = math.ceil(math.sqrt(num_pages))
    rows = math.ceil(num_pages / cols)

    thumb_w, thumb_h = 150, 200
    margin = 10
    canvas_w = cols * (thumb_w + margin) + margin
    canvas_h = rows * (thumb_h + margin) + margin

    preview = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(preview)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    for idx, fname in enumerate(tiffs):
        page_path = os.path.join(folder_path, fname)
        try:
            with Image.open(page_path) as img:
                img.thumbnail((thumb_w, thumb_h))
                col = idx % cols
                row = idx // cols
                x = margin + col * (thumb_w + margin)
                y = margin + row * (thumb_h + margin)
                preview.paste(img, (x, y))
                draw.text((x + 4, y + 4), f"{idx+1}", fill="black", font=font)
        except Exception as e:
            print(f"⚠️ Skipping {fname}: {e}")

    out_path = os.path.join(PREVIEW_OUT_DIR, f"{handle}_preview.png")
    try:
        preview.save(out_path)
        print(f"✅ Preview saved: {out_path}")
    except Exception as e:
        print(f"❌ Failed to save preview: {e}")