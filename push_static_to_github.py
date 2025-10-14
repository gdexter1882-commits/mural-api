import os
import subprocess
import shutil

# Step 1: Define paths
repo_root = os.path.abspath(".")
static_source = os.path.abspath("../static")  # adjust if needed
static_target = os.path.join(repo_root, "static")

# Step 2: Move static/ into repo if not already there
if not os.path.exists(static_target):
    print(f"Moving static folder into repo: {static_target}")
    shutil.move(static_source, static_target)
else:
    print("static/ already exists inside the repo.")

# Step 3: Git add, commit, and push
try:
    subprocess.run(["git", "add", "static/"], check=True)
    subprocess.run(["git", "commit", "-m", "Add static assets for mural thumbnails"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ static/ pushed to GitHub successfully.")
except subprocess.CalledProcessError as e:
    print(f"❌ Git command failed: {e}")