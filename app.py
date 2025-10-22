import os
import hashlib
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from eligible_texts import get_eligible_texts
from generate_png_grid import generate_png_grid
from grid_core import slugify

# Set environment variables for Flask run
os.environ["FLASK_RUN_HOST"] = "0.0.0.0"
os.environ["FLASK_RUN_PORT"] = os.environ.get("PORT", "5000")

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Ensure preview cache folder exists
PREVIEW_CACHE = os.path.join(app.static_folder, "previews")
os.makedirs(PREVIEW_CACHE, exist_ok=True)


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
        eligible = get_eligible_texts(wall_width, wall_height)
        deduped = list({str(item): item for item in eligible}.values())
        return jsonify({"eligible": deduped})
    except Exception as e:
        print(f"❌ Error in /api/murals: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/accurate-grid", methods=["POST"])
def accurate_grid():
    try:
        data = request.get_json()
        handle = data.get("handle")
        wall_w = float(data.get("wall_width"))
        wall_h = float(data.get("wall_height"))

        out_path = generate_png_grid(handle, wall_w, wall_h)
        if out_path:
            slug = slugify(handle)
            grid_url = f"https://mural-api.onrender.com/static/previews/{slug}_grid.png"
            return jsonify({"grid_url": grid_url})
        else:
            return jsonify({"error": "Grid generation failed"}), 500
    except Exception as e:
        print(f"❌ Error in /api/accurate-grid: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/grid-preview", methods=["POST"])
def grid_preview():
    """
    Generate or retrieve cached grid previews for all eligible murals
    for the given wall dimensions. Returns preview URLs.
    """
    try:
        data = request.get_json()
        wall_width = float(data.get("wall_width", 0))
        wall_height = float(data.get("wall_height", 0))

        # Step 1: Determine eligible murals
        eligible = get_eligible_texts(wall_width, wall_height)
        deduped = list({str(item): item for item in eligible}.values())

        results = []

        for mural in deduped:
            # Unique cache filename based on mural + wall dimensions
            slug = slugify(str(mural))
            cache_key = f"{slug}_{int(wall_width)}x{int(wall_height)}"
            hashed_name = hashlib.md5(cache_key.encode()).hexdigest()
            preview_filename = f"{hashed_name}_grid.png"
            preview_path = os.path.join(PREVIEW_CACHE, preview_filename)

            # Generate preview if not cached
            if not os.path.exists(preview_path):
                try:
                    generate_png_grid(
                        mural_title=str(mural),
                        wall_width=wall_width,
                        wall_height=wall_height,
                        output_path=preview_path
                    )
                except Exception as gen_e:
                    print(f"❌ Error generating grid for {mural}: {gen_e}", flush=True)
                    preview_path = None

            if preview_path and os.path.exists(preview_path):
                preview_url = url_for('static', filename=f'previews/{preview_filename}', _external=True)
            else:
                preview_url = None

            results.append({
                "mural": str(mural),
                "preview_url": preview_url,
                "link_text": "See how this will look on your wall"
            })

        return jsonify({"previews": results})

    except Exception as e:
        print(f"❌ Error in /api/grid-preview: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
