import csv
import re

CSV_PATH = "mural_master.csv"

def strip_trailing_pages(title):
    # Remove ' pages' only if it appears at the end
    return re.sub(r"\s+pages$", "", title)

with open(CSV_PATH, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)
    fieldnames = reader.fieldnames

for row in rows:
    if "Title" in row:
        row["Title"] = strip_trailing_pages(row["Title"])

with open(CSV_PATH, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("✅ mural_master.csv cleaned: removed trailing ' pages' from Title field only")