import os
import pandas as pd
from PIL import Image, ImageDraw

# Base directory of this script
BASE_DIR = os.path.dirname(__file__)

# Deployment-safe paths
CSV_PATH = os.path.join(BASE_DIR, "mural_master.csv")
TIFF_ROOT = os.path.join(BASE_DIR, "LowResFacsimiles")
STATIC_ROOT = os.path.join(BASE_DIR, "static", "previews")

def generate_png_grid(handle, wall_width, wall_height):
    # Normalize handle
    handle = handle.strip().lower()

    # Load mural metadata
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return None

    # Match handle
    row = df[df["Handle"].str.strip().str.lower() == handle]
    if row.empty:
        print(f"❌ Handle not found: {handle}")
        return None

    row = row.iloc[0]
    pages = int(row["Pages"])
    grid = row["grid"]
    cols, rows = map(int, grid.split("x"))
    slug = row["slug"]

    # Locate TIFF folder
    tiff_dir = os.path.join(TIFF_ROOT, slug)
    if not os.path.isdir(tiff_dir):
        print(f"❌ TIFF folder not found: {tiff_dir}")
        return None

    # Load and resize images
    images = []
    for i in range(1, pages + 1):
        filename = f"Page_{i:03}.tif"
        path = os.path.join(tiff_dir, filename)
        if not os.path.exists(path):
            print(f"⚠️ Missing page: {path}")
            continue
        img = Image.open(path).convert("RGB")
        images.append(img)

    if not images:
        print("❌ No images loaded")
        return None

    # Compute cell size
    cell_w = wall_width // cols
    cell_h = wall_height // rows

    # Create grid canvas
    grid_img = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
    draw = ImageDraw.Draw(grid_img)

    for idx, img in enumerate(images):
        if idx >= cols * rows:
            break
        x = (idx % cols) * cell_w
        y = (idx // cols) * cell_h
        img_resized = img.resize((cell_w, cell_h))
        grid_img.paste(img_resized, (x, y))

    # Save output
    os.makedirs(STATIC_ROOT, exist_ok=True)
    output_filename = f"{slug}_grid.png"
    output_path = os.path.join(STATIC_ROOT, output_filename)
    grid_img.save(output_path)

    return output_path