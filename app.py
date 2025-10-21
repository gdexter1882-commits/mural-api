import os
import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
from eligible_texts import get_eligible_texts
from grid_core import slugify

# Paths
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "mural_master.csv")
STATIC_ROOT = os.path.join(BASE_DIR, "csv")

# Flask setup
os.environ["FLASK_RUN_HOST"] = "0.0.0.0"
os.environ["FLASK_RUN_PORT"] = os.environ.get("PORT", "5000")

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def index():
    return "Mural API is running", 200

@app.route("/health")
def health():
    return "OK", 200

@app.route("/api/murals", methods=["POST"])
def get_murals():
    try:
        data = request.get_json()
        wall_width = float(data.get("wall_width", 0))
        wall_height = float(data.get("wall_height", 0))
        print(f"📐 Received dimensions: {wall_width} x {wall_height}", flush=True)

        eligible = get_eligible_texts(wall_width, wall_height)

        deduped = list({str(item): item for item in eligible}.values())
        print(f"🧾 Eligible mural count: {len(deduped)}")
        for i, mural in enumerate(deduped):
            print(f"{i+1}. {mural}", flush=True)

        return jsonify({"eligible": deduped})
    except Exception as e:
        print(f"❌ Error in /api/murals: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/grid-preview", methods=["POST"])
def grid_preview():
    try:
        data = request.get_json()
        handle = data.get("handle")
        wall_w = int(data.get("wall_width", 0))
        wall_h = int(data.get("wall_height", 0))

        print(f"🔍 Looking up handle: {handle}", flush=True)
        print(f"📐 Wall dimensions: {wall_w} x {wall_h}", flush=True)

        # Locate layout report
        report_path = os.path.join(STATIC_ROOT, f"{wall_w}x{wall_h}", "layout_report.csv")
        if not os.path.exists(report_path):
            print(f"⚠️ Missing layout report: {report_path}", flush=True)
            return jsonify({"error": "Layout report not found"}), 404

        # Read layout report
        with open(report_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next((r for r in reader if r["Handle"].strip().lower() == handle.strip().lower() and r["Fit"].strip().lower() == "yes"), None)

        if not row:
            print(f"⚠️ No valid layout found for: {handle}", flush=True)
            return jsonify({"error": "No valid layout found"}), 404

        # Build image path
        slug = slugify(handle)
        filename = f"{slug}_grid.png"
        grid_url = f"https://mural-api.onrender.com/static/previews/{wall_w}x{wall_h}/{filename}"

        print(f"🖼️ Grid preview URL: {grid_url}", flush=True)
        return jsonify({"grid_url": grid_url})
    except Exception as e:
        print(f"❌ Error in /api/grid-preview: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)