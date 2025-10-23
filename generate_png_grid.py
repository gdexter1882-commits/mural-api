import os
import csv
from PIL import Image

# Deployment-safe paths
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "mural_master.csv")
TIFF_ROOT = os.path.join(BASE_DIR, "LowResFacsimiles")
STATIC_ROOT = os.path.join(BASE_DIR, "static", "previews")

def find_tiff_folder(root, handle):
    for dirpath, dirnames, _ in os.walk(root):
        for dirname in dirnames:
            if dirname.strip().lower() == handle.strip().lower():
                return os.path.join(dirpath, dirname)
    return None

def select_best_layout(wall_w, wall_h, page_w, page_h, pages):
    wall_ratio = wall_w / wall_h
    best = None
    best_score = float("inf")

    for scale in range(95, 106):  # 95% to 105%
        pw = page_w * scale / 100
        ph = page_h * scale / 100

        for cols in range(1, pages + 1):
            rows = (pages + cols - 1) // cols
            for gap in range(1, 6):  # 1–5 cm
                grid_w = cols * pw
                grid_h = rows * ph + (rows - 1) * gap

                margin_x = (wall_w - grid_w) / 2
                margin_y = (wall_h - grid_h) / 2

                if not (5 <= margin_x <= 15 and 5 <= margin_y <= 15):
                    continue

                grid_ratio = grid_w / grid_h
                aspect_diff = abs(grid_ratio - wall_ratio)
                scale_penalty = abs(scale - 100) / 2
                score = aspect_diff + scale_penalty

                if score < best_score:
                    best_score = score
                    best = {
                        "fit": True,
                        "grid": f"{cols}x{rows}",
                        "scale_pct": scale,
                        "margin_x": margin_x,
                        "margin_y": margin_y,
                        "row_gap": gap,
                        "page_w": pw,
                        "page_h": ph
                    }

    return best if best else {"fit": False, "reason": "scale or margin out of bounds"}

def draw_grid(handle, layout, output_dir, pages):
    cols, rows = map(int, layout["grid"].split("x"))
    pw = int(layout["page_w"] * 10)  # cm → pixels
    ph = int(layout["page_h"] * 10)
    margin_x = int(layout["margin_x"] * 10)
    margin_y = int(layout["margin_y"] * 10)
    gap = layout["row_gap"] * 10

    grid_w = cols * pw
    grid_h = rows * ph + (rows - 1) * gap
    canvas_w = grid_w + 2 * margin_x
    canvas_h = grid_h + 2 * margin_y

    img = Image.new("RGB", (canvas_w, canvas_h), "white")

    tiff_dir = find_tiff_folder(TIFF_ROOT, handle)
    if not tiff_dir:
        print(f"❌ TIFF folder not found for: {handle}")
        return None

    for idx in range(pages):
        col = idx % cols
        row = idx // cols
        x = margin_x + col * pw
        y = margin_y + row * (ph + gap)

        page_num = idx + 1
        tiff_name = f"Page_{page_num:03}.tif"
        tiff_path = os.path.join(tiff_dir, tiff_name)

        try:
            page_img = Image.open(tiff_path).convert("RGB")
            page_img = page_img.resize((pw, ph), Image.LANCZOS)
            img.paste(page_img, (x, y))
        except:
            blank = Image.new("RGB", (pw, ph), "white")
            img.paste(blank, (x, y))

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{handle}_grid.png")
    img.save(out_path)
    print(f"✅ Saved: {out_path}")
    return out_path

def generate_png_grid(handle, wall_w, wall_h):
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Handle"].strip().lower() == handle.strip().lower():
                try:
                    pages = int(row["Pages"])
                    page_w = float(row["Page Width (cm)"])
                    page_h = float(row["Page Height (cm)"])
                except:
                    return None

                layout = select_best_layout(wall_w, wall_h, page_w, page_h, pages)
                if layout.get("fit"):
                    return draw_grid(handle, layout, STATIC_ROOT, pages)
                else:
                    print(f"❌ Layout failed: {layout['reason']}")
                    return None
    print(f"❌ Handle not found in CSV: {handle}")
    return None