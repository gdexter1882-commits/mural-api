import os
import csv
import requests

# === CONFIG ===
SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"
API_VERSION = "2023-10"
ACCESS_TOKEN = "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"
LOCAL_IMAGE_DIR = r"D:\csv\converted_images"
CSV_AUDIT = "shopify_image_audit.csv"
CSV_URLS = "shopify_image_urls.csv"

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# === GET ALL PRODUCTS ===
def get_all_products():
    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/products.json?limit=250"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch products: {response.status_code}")
        return []
    return response.json().get("products", [])

# === GET IMAGES FOR PRODUCT ===
def get_product_images(product_id):
    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/products/{product_id}/images.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch images for product {product_id}: {response.status_code}")
        return []
    return response.json().get("images", [])

# === MAIN AUDIT ===
products = get_all_products()
if not products:
    print("⚠️ No products found. Check your token or store name.")
    exit()

with open(CSV_AUDIT, "w", newline="", encoding="utf-8") as audit_file, \
     open(CSV_URLS, "w", newline="", encoding="utf-8") as url_file:

    audit_writer = csv.writer(audit_file)
    url_writer = csv.writer(url_file)

    audit_writer.writerow([
        "Slug", "Product Title", "Local Image Exists",
        "Shopify Image Count", "Low-Res Shopify Image"
    ])
    url_writer.writerow(["Slug", "Shopify Image URL"])

    for product in products:
        slug = product.get("handle", "").strip()
        product_id = product.get("id")
        title = product.get("title", "").strip()
        local_path = os.path.join(LOCAL_IMAGE_DIR, f"{slug}.jpg")
        local_exists = os.path.exists(local_path)

        print(f"🔍 Auditing: {slug} ({title})")
        images = get_product_images(product_id)
        image_count = len(images)
        low_res_flag = any(img.get("width", 0) < 2000 or img.get("height", 0) < 3000 for img in images)

        audit_writer.writerow([
            slug,
            title,
            "✅" if local_exists else "❌",
            image_count,
            "⚠️" if low_res_flag else "✅"
        ])

        for img in images:
            url = img.get("src", "")
            url_writer.writerow([slug, url])

print(f"\n✅ Audit complete.\n→ Summary: {CSV_AUDIT}\n→ URLs: {CSV_URLS}")