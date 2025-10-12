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
    return jsonify(eligible)