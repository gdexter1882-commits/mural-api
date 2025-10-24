import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eligible_texts import get_eligible_texts
from generate_png_grid import generate_png_grid  # ✅ accurate grid generator

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

        # ✅ Deduplicate by handle
        deduped = list({item["handle"]: item for item in eligible}.values())

        print(f"🧾 Eligible mural count: {len(deduped)}")
        for i, mural in enumerate(deduped):
            print(f"{i+1}. {mural['handle']}", flush=True)

        return jsonify({"eligible": deduped})
    except Exception as e:
        print(f"❌ Error in /api/murals: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/accurate-grid", methods=["POST"])
def accurate_grid():
    try:
        data = request.get_json()
        handle = data.get("handle")
        wall_w = float(data.get("wall_width", 0))
        wall_h = float(data.get("wall_height", 0))

        print(f"📦 Received accurate-grid request for: {handle} at {wall_w} x {wall_h}", flush=True)

        result = generate_png_grid(handle, wall_w, wall_h)

        if result:
            print(f"✅ Returning grid preview: {result}", flush=True)
            return jsonify({"grid_url": result})
        else:
            print("❌ Grid generation failed", flush=True)
            return jsonify({"error": "Grid generation failed"}), 400
    except Exception as e:
        print(f"❌ Exception in /api/accurate-grid: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/static/previews/<path:filename>")
def serve_preview(filename):
    return send_from_directory("static/previews", filename)

@app.route("/static/converted_images/<path:filename>")
def serve_converted_image(filename):
    return send_from_directory("static/converted_images", filename)