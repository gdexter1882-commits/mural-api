import os
import csv
from try_layout import try_layout
from generate_grid_preview import generate_grid_preview

LOWRES_ROOT = r"D:\LowResFacsimiles"
CSV_PATH = r"D:\csv\mural_master.csv"
STATIC_ROOT = r"D:\static\previews"

def main():
    print("📐 Enter wall dimensions in cm:")
    wall_w = float(input("Wall width: "))
    wall_h = float(input("Wall height: "))

    output_dir = os.path.join(STATIC_ROOT, f"{int(wall_w)}x{int(wall_h)}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n📁 Output folder: {output_dir}")

    results = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle = row["Handle"].strip()
            try:
                pages = int(row["Pages"])
                page_w = float(row["Page Width (cm)"])
                page_h = float(row["Page Height (cm)"])
            except (ValueError, KeyError):
                print(f"⚠️ Skipping malformed row: {row}")
                continue

            print(f"\n🔍 Trying layout for: {handle}")
            layout = try_layout(wall_w, wall_h, page_w, page_h, pages)
            print(f"📊 Layout result: {layout}")

            if layout.get("fit"):
                results.append({
                    "handle": handle,
                    "layout": layout
                })
                generate_grid_preview(handle, layout, output_dir)

    print(f"\n✅ Finished. Eligible murals: {len(results)}")
    for r in results:
        print(f" - {r['handle']} → {r['layout']['grid']} @ {r['layout']['scale_pct']}%")

if __name__ == "__main__":
    main()