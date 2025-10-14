from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
from try_layout import try_layout
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

CSV_PATH = "mural_master.csv"
REQUIRED_COLUMNS = {"Handle", "Pages", "Page Height (cm)", "Page Width (cm)"}

# Diagnostic print to confirm CSV path and existence
csv_abs_path = os.path.abspath(CSV_PATH)
print(f"📄 Attempting to read CSV from: {csv_abs_path}", flush=True)

if not os.path.exists(CSV_PATH):
    print("❌ mural_master.csv not found — check repo and deployment path.", flush=True)
    df = pd.DataFrame()
else:
    print("✅ mural_master.csv found — loading now.", flush=True)
    df = pd.read_csv(CSV_PATH)
    print(f"📊 Columns in CSV: {list(df.columns)}", flush=True)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"❌ Missing required columns: {missing}", flush=True)
        df = pd.DataFrame()

@app.route("/api/murals", methods=["POST"])
def get_murals():
    data = request.get_json()
    print(f"📥 Received request: {data}", flush=True)

    wall_width = data.get("wall_width")
    wall_height = data.get("wall_height")

    if wall_width is None or wall_height is None:
        print("❌ Missing wall dimensions", flush=True)
        return jsonify({"error": "Missing wall dimensions"}), 400

    if df.empty:
        print("❌ mural_master.csv is not loaded or missing required columns", flush=True)
        return jsonify({"error": "CSV not loaded or missing required columns"}), 500

    eligible = []

    for i, row in df.iterrows():
        try:
            print(f"🔍 Row {i}: {row.to_dict()}", flush=True)

            handle = str(row.get("Handle", "")).strip()
            pages = int(float(row.get("Pages", 0)))
            height = float(row.get("Page Height (cm)", 0))
            width = float(row.get("Page Width (cm)", 0))
            margin = float(row.get("Margin", 0)) if "Margin" in row else 0

            result = try_layout(
                wall_width,
                wall_height,
                width,
                height,
                pages,
                margin
            )
            print(f"📐 Layout result for {handle}: {result}", flush=True)

            if result.get("eligible"):
                eligible.append({
                    "handle": handle,
                    "layout": result["layout"],
                    "scale": result["scale"],
                    "pages": pages,
                    "margin": margin
                })
        except Exception as e:
            print(f"⚠️ Error in row {i} ({row.get('Handle', 'UNKNOWN')}): {e}", flush=True)

    print(f"✅ Returning {len(eligible)} eligible murals", flush=True)
    return jsonify({"eligible": eligible})