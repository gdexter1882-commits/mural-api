import os
import csv
from flask import Flask, jsonify
from generate_layout_preview import generate_preview

app = Flask(__name__)

CSV_PATH = r"D:\csv\mural_master.csv"

@app.route("/")
def index():
    return "✅ Flask is running"

@app.route("/api/murals")
def generate_all_previews():
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        handles = [row["Handle"].strip() for row in reader]

    for handle in handles:
        generate_preview(handle)

    return jsonify({"status": "Previews generated", "count": len(handles)})

if __name__ == "__main__":
    app.run(debug=True)