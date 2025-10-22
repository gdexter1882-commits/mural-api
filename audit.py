import requests
from collections import defaultdict
from datetime import datetime

SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"
ACCESS_TOKEN = "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"
API_BASE = f"https://{SHOPIFY_STORE}/admin/api/2023-10"

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def get_all_products():
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

products = get_all_products()
by_title = defaultdict(list)

for p in products:
    by_title[p["title"]].append({
        "id": p["id"],
        "created_at": p["created_at"],
        "updated_at": p["updated_at"],
        "handle": p["handle"],
        "admin_graphql_api_id": p["admin_graphql_api_id"]
    })

for title, entries in by_title.items():
    if len(entries) > 1:
        print(f"\n⚠️ Duplicate: {title} → {len(entries)} copies")
        for entry in entries:
            print(f"  • ID: {entry['id']} | Created: {entry['created_at']} | Handle: {entry['handle']}")