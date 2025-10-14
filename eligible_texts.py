import pandas as pd
from try_layout import try_layout

def get_eligible_texts(wall_w, wall_h, csv_path="mural_master.csv"):
    eligible = []

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}", flush=True)
        return []

    for i, row in df.iterrows():
        try:
            handle = str(row.get("Handle", "")).strip()
            pages = int(float(row.get("Pages", 0)))
            height = float(row.get("Page Height (cm)", 0))
            width = float(row.get("Page Width (cm)", 0))
            margin = float(row.get("Margin", 0)) if "Margin" in row else 0

            result = try_layout(wall_w, wall_h, width, height, pages, margin)

            if result.get("eligible") is True:
                eligible.append({
                    "title": handle,
                    "grid": result.get("grid"),
                    "scale": result.get("scale_pct")
                })
        except Exception as e:
            print(f"⚠️ Skipping row {i} ({handle}): {e}", flush=True)

    return eligible