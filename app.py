from flask import Flask, request, jsonify
from flask_cors import CORS
from eligible_texts import get_eligible_texts

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api/murals", methods=["GET", "POST"])
def get_murals():
    if request.method == "POST":
        data = request.get_json()
        wall_width = data.get("wall_width") or data.get("width")
        wall_height = data.get("wall_height") or data.get("height")
    else:
        wall_width = request.args.get("wall_width", type=float) or request.args.get("width", type=float)
        wall_height = request.args.get("wall_height", type=float) or request.args.get("height", type=float)

    if wall_width is None or wall_height is None:
        return jsonify({"error": "Missing wall dimensions"}), 400

    eligible = get_eligible_texts(wall_width, wall_height)

    # Format for Shopify: list of {title: "..."}
    return jsonify([{"title": text} for text in eligible])