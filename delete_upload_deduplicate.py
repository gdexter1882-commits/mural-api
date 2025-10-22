import csv
import os
import base64
import requests
from datetime import datetime
from collections import defaultdict

SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"
ACCESS_TOKEN = "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"
API_BASE = f"https://{SHOPIFY_STORE}/admin/api/2023-10"
thumb_dir = r"D:\csv\static\thumbnails\firstpage"

# 🔒 Prevent accidental reruns
if os.path.exists("import.lock"):
    print("🛑 Import already ran. Exiting.")
    exit()
else:
    with open("import.lock", "w") as f:
        f.write(datetime.now().isoformat())

# 🔹 Encode local image as base64
def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 🔹 Get all products
def get_all_products():
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    products = []
    page_info = None

    while True:
        params = {"limit": 250}
        if page_info:
            params["page_info"] = page_info

        response = requests.get(f"{API_BASE}/products.json", headers=headers, params=params)
        if response.status_code != 200:
            print("❌ Failed to fetch products:", response.text)
            break

        data = response.json()
        products.extend(data.get("products", []))

        link_header = response.headers.get("Link", "")
        if 'rel="next"' in link_header:
            page_info = link_header.split("page_info=")[-1].split(">")[0]
        else:
            break

    return products

# 🔹 Delete product
def delete_product(product_id, title):
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    response = requests.delete(f"{API_BASE}/products/{product_id}.json", headers=headers)
    if response.status_code == 200:
        print(f"🗑️ Deleted: {title} at {datetime.now().isoformat()}")
    else:
        print(f"❌ Failed to delete: {title} → {response.text}")

# 🔹 Check if product exists by handle
def product_exists(handle):
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    response = requests.get(f"{API_BASE}/products.json?handle={handle}", headers=headers)
    if response.status_code == 200:
        return bool(response.json().get("products"))
    return False

# 🔹 Create product
def create_product(title, handle, image_path):
    if product_exists(handle):
        print(f"⏭️ Skipped (already exists): {title}")
        return

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    payload = {
        "product": {
            "title": title,
            "handle": handle,
            "body_html": "",
            "images": [{"attachment": encode_image(image_path)}]
        }
    }
    response = requests.post(f"{API_BASE}/products.json", json=payload, headers=headers)
    if response.status_code == 201:
        print(f"✅ Created: {title} at {datetime.now().isoformat()}")
    else:
        print(f"❌ Failed: {title} → {response.text}")

# 🔹 Phase 1: Delete all products
print("🧹 Deleting existing products...")
products = get_all_products()
for product in products:
    delete_product(product["id"], product["title"])

# 🔹 Phase 2: Create clean listings
print("\n🚀 Creating fresh listings...")
with open(r"D:\csv\mural_master.csv", newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        handle = row["Handle"].strip()
        title = row["Title"].strip()

        thumb_path = os.path.join(thumb_dir, f"{handle}.jpg")
        print("🔍 Checking:", thumb_path, "→", os.path.exists(thumb_path))

        if os.path.exists(thumb_path):
            create_product(title, handle, thumb_path)
        else:
            print(f"⚠️ Missing thumbnail for: {handle}")

# 🔹 Phase 3: Deduplicate by title
print("\n🧹 Deduplicating products by title...")
products = get_all_products()
by_title = defaultdict(list)

for p in products:
    by_title[p["title"]].append(p)

for title, entries in by_title.items():
    if len(entries) > 1:
        # Keep the earliest created product, delete the rest
        entries.sort(key=lambda x: x["created_at"])
        to_delete = entries[1:]
        for p in to_delete:
            delete_product(p["id"], p["title"])