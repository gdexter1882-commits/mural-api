import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from eligible_texts import get_eligible_texts
from grid_mockup import generate_mockup
from grid_core import slugify

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
        grid_str = data.get("grid")  # e.g. "9x5"
        total_pages = int(data.get("pages", 0))

        print(f"🔍 Generating grid for: {handle}", flush=True)
        print(f"📦 Grid: {grid_str}, Pages: {total_pages}", flush=True)

        # Parse grid
        try:
            rows, cols = map(int, grid_str.lower().split("x"))
        except Exception:
            return jsonify({"error": "Invalid grid format"}), 400

        # Generate mockup
        output_dir = os.path.join("static", "previews")
        out_path = generate_mockup(handle, rows, cols, total_pages, output_dir)

        slug = slugify(handle)
        grid_url = f"https://mural-api.onrender.com/static/previews/{slug}_grid.png"
        print(f"🖼️ Grid preview URL: {grid_url}", flush=True)

        return jsonify({"grid_url": grid_url})
    except Exception as e:
        print(f"❌ Error in /api/grid-preview: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)