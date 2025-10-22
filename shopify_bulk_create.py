import csv
import os
import base64
import requests

SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"
ACCESS_TOKEN = "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"
API_URL = f"https://{SHOPIFY_STORE}/admin/api/2023-10/products.json"

thumb_dir = r"D:\csv\static\thumbnails\firstpage"

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def create_product(title, image_path):
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    payload = {
        "product": {
            "title": title,
            "body_html": "",
            "images": [{"attachment": encode_image(image_path)}]
        }
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code == 201:
        print(f"✅ Created: {title}")
    else:
        print(f"❌ Failed: {title} → {response.text}")

with open(r"D:\csv\mural_master.csv", newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        handle = row["Handle"].strip()
        title = row["Title"].strip()

        thumb_path = os.path.join(thumb_dir, f"{handle}.jpg")
        print("🔍 Checking:", thumb_path, "→", os.path.exists(thumb_path))

        if os.path.exists(thumb_path):
            create_product(title, thumb_path)
        else:
            print(f"⚠️ Missing thumbnail for: {handle}")