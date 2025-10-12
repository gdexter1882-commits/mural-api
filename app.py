from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from try_layout import try_layout

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

CSV_PATH = "mural_master.csv"

print(f"📄 Attempting to read CSV from: {os.path.abspath(CSV_PATH)}", flush=True)
if not os.path.exists(CSV_PATH):
    print("❌ mural_master.csv not found — check repo and deployment path.", flush=True)
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
    app.run(host="0.0.0.0", port=port, debug=False)