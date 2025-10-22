import requests

SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"
ACCESS_TOKEN = "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"
API_URL = f"https://{SHOPIFY_STORE}/admin/api/2023-10/products.json"

headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

response = requests.get(API_URL, headers=headers)

if response.status_code == 200:
    print("✅ Token is valid. Products retrieved:")
    for product in response.json().get("products", []):
        print("-", product.get("title"))
else:
    print(f"❌ Token failed: {response.status_code}")
    print(response.text)