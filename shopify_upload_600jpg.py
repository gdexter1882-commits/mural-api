import os
import json
import base64
import requests

# === CONFIG ===
SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"
API_VERSION = "2023-10"
ACCESS_TOKEN = "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"
IMAGE_DIR = "converted_images"
SLUG_MAP_FILE = "slug_to_image_map.json"

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# === LOAD SLUG MAP ===
with open(SLUG_MAP_FILE, "r", encoding="utf-8") as f:
    slug_map = json.load(f)

# === GET ALL PRODUCTS ===
def get_all_products():
    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/products.json?limit=250"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["products"]

# === GET IMAGES FOR PRODUCT ===
def get_product_images(product_id):
    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/products/{product_id}/images.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["images"]

# === DELETE IMAGE BY ID ===
def delete_image(product_id, image_id):
    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/products/{product_id}/images/{image_id}.json"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 200:
        print(f"🗑️ Deleted image {image_id}")
    else:
        print(f"❌ Failed to delete image {image_id} → {response.status_code} {response.text}")

# === UPLOAD IMAGE ===
def upload_image(product_id, image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "image": {
            "attachment": encoded,
            "filename": os.path.basename(image_path),
            "position": 1
        }
    }

    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/products/{product_id}/images.json"
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 201]:
        print(f"✅ Uploaded: {os.path.basename(image_path)}")
    else:
        print(f"❌ Upload failed: {os.path.basename(image_path)} → {response.status_code} {response.text}")

# === MAIN ===
products = get_all_products()
slug_to_id = {p["handle"]: p["id"] for p in products}

for slug, tif_path in slug_map.items():
    product_id = slug_to_id.get(slug)
    if not product_id:
        print(f"⚠️ No product found for slug: {slug}")
        continue

    jpg_path = os.path.join(IMAGE_DIR, f"{slug}.jpg")
    if not os.path.exists(jpg_path):
        print(f"⚠️ Missing image file: {jpg_path}")
        continue

    # Check existing images
    existing_images = get_product_images(product_id)
    high_res_found = False

    for img in existing_images:
        width = img.get("width", 0)
        height = img.get("height", 0)
        src = img.get("src", "")
        image_id = img.get("id")

        if width >= 2000 and height >= 3000:
            high_res_found = True
            print(f"🖼️ High-res already present for {slug}")
        else:
            delete_image(product_id, image_id)

    if not high_res_found:
        upload_image(product_id, jpg_path)