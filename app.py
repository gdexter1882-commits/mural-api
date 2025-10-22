from flask import Flask, request, jsonify, send_from_directory
from generate_png_grid import generate_png_grid
import os

app = Flask(__name__, static_folder="static")

@app.route("/api/accurate-grid", methods=["POST"])
def accurate_grid():
    try:
        data = request.get_json(force=True)
        handle = data.get("handle")
        wall_w = data.get("wall_width")
        wall_h = data.get("wall_height")

        if not all([handle, wall_w, wall_h]):
            return jsonify({"error": "Missing required fields"}), 400

        grid_path = generate_png_grid(handle, wall_w, wall_h)
        if not grid_path:
            return jsonify({"error": "Grid generation failed"}), 500

        filename = os.path.basename(grid_path)
        grid_url = f"/static/previews/{filename}"
        return jsonify({"grid_url": grid_url})

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/api/test-csv", methods=["GET"])
def test_csv():
    try:
        with open("csv/mural_master.csv", encoding="utf-8") as f:
            first_line = f.readline().strip()
        return jsonify({"status": "success", "first_line": first_line})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/static/previews/<path:filename>")
def serve_preview(filename):
    return send_from_directory("static/previews", filename)

if __name__ == "__main__":
    app.run(debug=True)