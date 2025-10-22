import csv
import requests
import re

# Shopify credentials
SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"
ACCESS_TOKEN = "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"
API_URL = f"https://{SHOPIFY_STORE}/admin/api/2023-10/products.json"

# CSV file to patch
CSV_PATH = "mural_master_shopify.csv"

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")

def get_product_images_by_slug():
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    products = {}
    endpoint = f"{API_URL}?limit=250"
    last_id = None

    while True:
        if last_id:
            endpoint = f"{API_URL}?limit=250&since_id={last_id}"

        response = requests.get(endpoint, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch products: {response.text}")
            break

        data = response.json().get("products", [])
        if not data:
            break

        for product in data:
            title = product.get("title", "").strip()
            slug = slugify(title)
            images = product.get("images", [])
            if images:
                products[slug] = images[0].get("src", "")
            last_id = product.get("id")

        if len(data) < 250:
            break

    return products

def patch_csv_with_images(image_map):
    with open(CSV_PATH, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    fieldnames = reader.fieldnames
    if "Image Src" not in fieldnames:
        fieldnames.append("Image Src")

    for row in rows:
        handle = row.get("Handle", "").strip()
        slug = slugify(handle)
        if slug in image_map:
            row["Image Src"] = image_map[slug]

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ mural_master_shopify.csv overwritten with Shopify CDN image URLs")

# Run the patch
image_map = get_product_images_by_slug()
patch_csv_with_images(image_map)