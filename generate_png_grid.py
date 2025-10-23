import os
import csv
from PIL import Image

CSV_PATH = "mural_master.csv"
STATIC_ROOT = "static/previews"
TIFF_ROOT = "LowResFacsimiles"

def find_tiff_folder(root, handle):
    print(f"📁 Searching for TIFF folder matching: {handle}")
    for dirpath, dirnames, _ in os.walk(root):
        for dirname in dirnames:
            print(f"🔍 Checking folder: {dirname}")
            if dirname.strip().lower() == handle.strip().lower():
                match = os.path.join(dirpath, dirname)
                print(f"✅ Found TIFF folder: {match}")
                return match
    print("❌ No matching TIFF folder found")
    return None

def select_best_layout(wall_w, wall_h, page_w, page_h, pages):
    wall_ratio = wall_w / wall_h
    best = None
    best_score = float("inf")

    for scale in range(95, 106):
        pw = page_w * scale / 100
        ph = page_h * scale / 100

        for cols in range(1, pages + 1):
            rows = (pages + cols - 1) // cols
            for gap in range(1, 6):
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

    if best:
        print(f"✅ Selected layout: {best}")
    else:
        print("❌ No viable layout found")
    return best if best else {"fit": False, "reason": "scale or margin out of bounds"}

def draw_grid(handle, layout, output_dir, pages):
    cols, rows = map(int, layout["grid"].split("x"))
    pw = int(layout["page_w"] * 10)
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
        except Exception as e:
            print(f"⚠️ Missing or unreadable page: {tiff_name} — {e}")
            blank = Image.new("RGB", (pw, ph), "white")
            img.paste(blank, (x, y))

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{handle}_grid.png")
    img.save(out_path)
    print(f"✅ Saved grid image: {out_path}")
    return out_path

def generate_png_grid(handle, wall_w, wall_h):
    print(f"\n📄 Reading CSV: {CSV_PATH}")
    print(f"📐 Wall dimensions: {wall_w} x {wall_h} cm")
    try:
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_handle = row["Handle"].strip()
                print(f"🔍 Comparing: {csv_handle}  vs  {handle.strip()}")
                if csv_handle == handle.strip():
                    try:
                        pages = int(row["Pages"])
                        page_w = float(row["Page Width (cm)"])
                        page_h = float(row["Page Height (cm)"])
                    except Exception as e:
                        print(f"❌ Invalid page data: {e}")
                        return None

                    layout = select_best_layout(wall_w, wall_h, page_w, page_h, pages)
                    if not layout.get("fit"):
                        print(f"❌ Layout rejected: {layout.get('reason')}")
                        return None

                    output_dir = os.path.join(STATIC_ROOT, f"{int(wall_w)}x{int(wall_h)}")
                    os.makedirs(output_dir, exist_ok=True)
                    return draw_grid(handle, layout, output_dir, pages)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return None

    print("❌ Handle not found in CSV")
    return None