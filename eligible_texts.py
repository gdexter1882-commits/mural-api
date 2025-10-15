import csv
import os
import re
import unicodedata

def slugify(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.lower().strip("-")

def try_layout(wall_w, wall_h, page_w, page_h, pages, margin=0):
    for margin_test in range(5, 16):  # test margins from 5 to 15 cm
        usable_w = wall_w - 2 * margin_test
        usable_h = wall_h - 2 * margin_test

        for scale_pct in range(95, 106):  # 95% to 105%
            scaled_pw = page_w * scale_pct / 100
            scaled_ph = page_h * scale_pct / 100

            for row_gap in range(1, 6):  # 1 to 5 cm
                for cols in range(1, pages + 1):
                    rows = (pages + cols - 1) // cols  # ceiling division

                    mural_w = cols * scaled_pw
                    mural_h = rows * scaled_ph + (rows - 1) * row_gap

                    if mural_w <= usable_w and mural_h <= usable_h:
                        margin_x = (wall_w - mural_w) / 2
                        margin_y = (wall_h - mural_h) / 2

                        if not (5 <= margin_x <= 15 and 5 <= margin_y <= 15):
                            continue

                        return {
                            "eligible": True,
                            "grid": f"{cols}x{rows}",
                            "scale_pct": scale_pct,
                            "row_gap": row_gap,
                            "margin_x": round(margin_x, 2),
                            "margin_y": round(margin_y, 2),
                            "text_centered": True
                        }

    return {"eligible": False}

def get_eligible_texts(wall_width, wall_height):
    eligible = []
    base_url = "https://mural-api.onrender.com/static/thumbnails/firstpage"

    csv_path = os.path.join(os.path.dirname(__file__), "mural_master.csv")
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                handle = str(row.get("Handle", "")).strip()
                pages = int(row.get("Pages", 0))
                width_cm = float(row.get("Page Width (cm)", 0))
                height_cm = float(row.get("Page Height (cm)", 0))

                layout = try_layout(wall_width, wall_height, width_cm, height_cm, pages)
                if layout.get("eligible"):
                    thumbnail_url = f"{base_url}/{handle}.jpg"
                    eligible.append({
                        "title": handle,
                        "handle": handle,
                        "slug": slugify(handle),
                        "grid": layout.get("grid"),
                        "scale": layout.get("scale_pct"),
                        "thumbnail": thumbnail_url
                    })
            except Exception as e:
                print(f"⚠️ Skipping row due to error: {e}", flush=True)

    return eligible