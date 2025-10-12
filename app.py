from flask import Flask, request, jsonify
from flask_cors import CORS
from eligible_texts import get_eligible_texts

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api/murals", methods=["POST"])
def get_murals():
    data = request.get_json()
    wall_width = data.get("wall_width")
    wall_height = data.get("wall_height")

    if wall_width is None or wall_height is None:
        return jsonify({"error": "Missing wall dimensions"}), 400

    eligible = get_eligible_texts(wall_width, wall_height)
    return jsonify({"eligible": eligible})