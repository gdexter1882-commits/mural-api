import csv
import os
from layout_filter import get_layout

def get_eligible_texts(wall_width, wall_height):
    eligible = []
    base_url = "https://mural-api.onrender.com/static/thumbnails/firstpage"

    csv_path = os.path.join(os.path.dirname(__file__), "mural_master.csv")
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                filename = str(row.get("Handle", "")).strip()
                pages = int(row.get("Pages", 0))
                width_cm = float(row.get("Page Width (cm)", 0))
                height_cm = float(row.get("Page Height (cm)", 0))
                margin = float(row.get("Margin", 0)) if "Margin" in row else 0

                result = get_layout(wall_width, wall_height, pages, width_cm, height_cm, margin)
                if result:
                    thumbnail_url = f"{base_url}/{filename}.jpg"
                    eligible.append({
                        "title": filename,
                        "grid": result.get("grid"),
                        "scale": result.get("scale_pct"),
                        "thumbnail": thumbnail_url
                    })
            except Exception as e:
                print(f"⚠️ Skipping row due to error: {e}", flush=True)

    return eligible