import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from try_layout import try_layout

# Force Flask to bind correctly even if launched via flask run
os.environ["FLASK_RUN_HOST"] = "0.0.0.0"
os.environ["FLASK_RUN_PORT"] = os.environ.get("PORT", "5000")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

CSV_PATH = "mural_master.csv"

# Diagnostic print to confirm CSV path and existence
csv_abs_path = os.path.abspath(CSV_PATH)
print(f"📄 Attempting to read CSV from: {csv_abs_path}", flush=True)

if not os.path.exists(CSV_PATH):
    print("❌ mural_master.csv not found — check repo and deployment path.", flush=True)
    df = pd.DataFrame()
else:
    print("✅ mural_master.csv found — loading now.", flush=True)
    df = pd.read_csv(CSV_PATH)

@app.route("/api/murals", methods=["POST"])
def get_murals():
    data = request.get_json()
    wall_width = data.get("wall_width")
    wall_height = data.get("wall_height")

    eligible = []

    for _, row in df.iterrows():
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

    return jsonify({"eligible": eligible})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)