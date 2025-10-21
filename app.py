import os
import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
from eligible_texts import get_eligible_texts
from grid_core import slugify, select_best_layout, draw_grid

# Paths
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "mural_master.csv")
STATIC_ROOT = os.path.join(BASE_DIR, "static", "previews")

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
        wall_w = float(data.get("wall_width", 0))
        wall_h = float(data.get("wall_height", 0))

        print(f"🔍 Looking up handle: {handle}", flush=True)
        print(f"📐 Wall dimensions: {wall_w} x {wall_h}", flush=True)

        # Lookup mural metadata from CSV
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next((r for r in reader if r["Handle"].strip().lower() == handle.strip().lower()), None)

        print(f"📄 CSV row: {row}", flush=True)

        if not row:
            return jsonify({"error": "Mural not found"}), 404

        try:
            pages = int(row["Pages"])
            raw_page_w = float(row["Page Width (cm)"])
            raw_page_h = float(row["Page Height (cm)"])
            scale_factor = 0.2  # shrink preview to 20% of original size
            page_w = raw_page_w * scale_factor
            page_h = raw_page_h * scale_factor
        except:
            return jsonify({"error": "Invalid mural data"}), 400

        layout = select_best_layout(wall_w, wall_h, page_w, page_h, pages)
        print(f"📊 Layout: {layout}", flush=True)

        if not layout.get("fit"):
            return jsonify({"error": layout["reason"]}), 400

        output_dir = os.path.join(STATIC_ROOT, f"{int(wall_w)}x{int(wall_h)}")
        os.makedirs(output_dir, exist_ok=True)
        print(f"🖼️ Output dir: {output_dir}", flush=True)

        out_path = draw_grid(handle, layout, output_dir, pages)
        print(f"📁 Grid path: {out_path}", flush=True)

        if not out_path:
            return jsonify({"error": "Grid rendering failed"}), 500

        filename = os.path.basename(out_path)
        slug = slugify(handle)
        grid_url = f"https://mural-api.onrender.com/static/previews/{int(wall_w)}x{int(wall_h)}/{filename}"

        return jsonify({"grid_url": grid_url})
    except Exception as e:
        print(f"❌ Error in /api/grid-preview: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)