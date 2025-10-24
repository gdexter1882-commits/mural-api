import csv
import os
import re
import unicodedata
from try_layout import try_layout

def slugify(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.lower().strip("-")

def get_eligible_texts(wall_width, wall_height):
    eligible = []
    base_url = "https://mural-api.onrender.com/static/thumbnails/firstpage"
    csv_path = os.path.join(os.path.dirname(__file__), "mural_master.csv")
    shopify_csv_path = os.path.join(os.path.dirname(__file__), "mural_master_shopify.csv")

    # ✅ Load Shopify CDN URLs into a lookup dictionary
    cdn_lookup = {}
    try:
        with open(shopify_csv_path, newline="", encoding="utf-8") as shopify_file:
            shopify_reader = csv.DictReader(shopify_file)
            for row in shopify_reader:
                raw_handle = str(row.get("Handle", "")).strip()
                handle = raw_handle.lower()
                cdn_url = str(row.get("Image src", "")).strip()
                if handle:
                    cdn_lookup[handle] = cdn_url
        print(f"🛒 Loaded {len(cdn_lookup)} CDN entries from mural_master_shopify.csv", flush=True)
    except Exception as e:
        print(f"❌ Failed to load mural_master_shopify.csv: {e}", flush=True)

    # ✅ Load mural layout and sizing from mural_master.csv
    try:
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    raw_handle = str(row.get("Handle", "")).strip()
                    handle = raw_handle.lower()
                    title = str(row.get("Title", "")).strip()
                    pages = int(row.get("Pages", 0))
                    width_cm = float(row.get("Page Width (cm)", 0))
                    height_cm = float(row.get("Page Height (cm)", 0))
                    cdn_url = cdn_lookup.get(handle, "")

                    if height_cm == 0:
                        continue

                    aspect_ratio = round(width_cm / height_cm, 4)

                    layout = try_layout(wall_width, wall_height, width_cm, height_cm, pages)
                    if layout.get("eligible"):
                        thumbnail_url = f"{base_url}/{raw_handle}.jpg"
                        if not cdn_url:
                            print(f"⚠️ No CDN match for: {raw_handle}", flush=True)
                        else:
                            print(f"✅ Matched CDN for: {raw_handle} → {cdn_url}", flush=True)
                        eligible.append({
                            "title": title,
                            "handle": raw_handle,
                            "slug": slugify(raw_handle),
                            "grid": layout.get("grid"),
                            "scale": layout.get("scale_pct"),
                            "thumbnail": thumbnail_url,
                            "pages": pages,
                            "aspect_ratio": aspect_ratio,
                            "cdn_url": cdn_url
                        })
                except Exception as e:
                    print(f"⚠️ Skipping row due to error: {e}", flush=True)
        print(f"📄 Reloaded mural_master.csv with {len(eligible)} eligible entries", flush=True)
    except Exception as e:
        print(f"❌ Failed to load mural_master.csv: {e}", flush=True)

    return eligible