from flask import Flask, request, jsonify
import pandas as pd
from try_layout import try_layout

app = Flask(__name__)

# Define the path to your CSV
CSV_PATH = "mural_master.csv"

# Diagnostic print to confirm CSV path
print(f"📄 Reading CSV from: {CSV_PATH}")

# Load the mural data
df = pd.read_csv(CSV_PATH)

@app.route("/api/murals", methods=["POST"])
def get_murals():
    data = request.get_json()
    wall_width = data.get("wall_width")
    wall_height = data.get("wall_height")

    eligible = []

    for _, row in df.iterrows():
        result = try_layout(
            wall_width,
            wall_height,
            row["Width"],
            row["Height"],
            row["Pages"],
            row["Margin"]
        )
        if result["eligible"]:
            eligible.append({
                "handle": row["Handle"],
                "layout": result["layout"],
                "scale": result["scale"],
                "pages": row["Pages"],
                "margin": row["Margin"]
            })

    return jsonify({"eligible": eligible})

if __name__ == "__main__":
    app.run(debug=True)