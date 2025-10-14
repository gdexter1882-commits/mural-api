import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from eligible_texts import get_eligible_texts

# Force Flask to bind correctly even if launched via flask run
os.environ["FLASK_RUN_HOST"] = "0.0.0.0"
os.environ["FLASK_RUN_PORT"] = os.environ.get("PORT", "5000")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api/murals", methods=["POST"])
def get_murals():
    data = request.get_json()
    wall_width = float(data.get("wall_width", 0))
    wall_height = float(data.get("wall_height", 0))

    eligible = get_eligible_texts(wall_width, wall_height)

    return jsonify({"eligible": eligible})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)