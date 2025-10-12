from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from try_layout import try_layout
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

CSV_PATH = "mural_master.csv"
REQUIRED_COLUMNS = {"Handle", "Width", "Height", "Pages", "Margin"}

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
        df = pd.DataFrame()  # prevent layout loop from running

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

    for _, row in df.iterrows():
        try:
            result = try_layout(
                wall_width,
                wall_height,
                row["Width"],
                row["Height"],
                row["Pages"],
                row["Margin"]
            )
            if result["eligible"]:
                eligible.append({
                    "handle": row["Handle"],
                    "layout": result["layout"],
                    "scale": result["scale"],
                    "pages": row["Pages"],
                    "margin": row["Margin"]
                })
        except Exception as e:
            print(f"⚠️ Layout error for {row.get('Handle', 'UNKNOWN')}: {e}", flush=True)

    print(f"✅ Returning {len(eligible)} eligible murals", flush=True)
    return jsonify({"eligible": eligible})