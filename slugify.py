import csv

def slugify(text):
    import re, unicodedata
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.lower().strip("-")

SHOPIFY_STORE = "sj1vbt-c0.myshopify.com"

with open(r"D:\csv\mural_master.csv", newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title = row["Title"].strip()
        raw_handle = row["Handle"].strip()
        slug = slugify(raw_handle)
        url = f"https://{SHOPIFY_STORE}/products/{slug}"
        print(f"{title}\n→ {url}\n")