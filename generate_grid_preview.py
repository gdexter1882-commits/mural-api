import os
from PIL import Image

LOWRES_ROOT = r"D:\LowResFacsimiles"

def generate_grid_preview(handle, layout, output_dir):
    print(f"\n📸 Generating layout for: {handle}")

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

    cols, rows = map(int, layout["grid"].split("x"))
    scale_pct = layout.get("scale_pct", 100)
    margin_x = layout.get("margin_x", 0)
    margin_y = layout.get("margin_y", 0)
    row_gap = layout.get("row_gap", margin_y)

    sample_path = os.path.join(folder_path, tiffs[0])
    try:
        with Image.open(sample_path) as sample:
            page_w, page_h = sample.size
    except Exception as e:
        print(f"❌ Failed to open sample page: {e}")
        return

    scaled_w = int(page_w * scale_pct / 100)
    scaled_h = int(page_h * scale_pct / 100)

    canvas_w = cols * scaled_w + (cols - 1) * margin_x
    canvas_h = rows * scaled_h + (rows - 1) * row_gap
    preview = Image.new("RGB", (canvas_w, canvas_h), "white")

    for idx in range(cols * rows):
        if idx >= len(tiffs):
            break

        page_path = os.path.join(folder_path, tiffs[idx])
        try:
            with Image.open(page_path) as img:
                img = img.resize((scaled_w, scaled_h))
                col = idx % cols
                row = idx // cols
                x = col * (scaled_w + margin_x)
                y = row * (scaled_h + row_gap)
                preview.paste(img, (x, y))
        except Exception as e:
            print(f"⚠️ Skipping page {idx + 1}: {e}")

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{handle}_layout.png")
    try:
        preview.save(out_path)
        print(f"✅ Saved: {out_path}")
    except Exception as e:
        print(f"❌ Failed to save preview: {e}")