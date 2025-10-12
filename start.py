from app import app
import os

port = int(os.environ.get("PORT", 10000))
print(f"🚀 Starting Flask on 0.0.0.0:{port}", flush=True)
app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)