import os
import subprocess
import kagglehub
import base64

DATASET_HANDLE = "tonmoyk983/test-dataset-1"
LOCAL_DIR = "upload_data"

# -----------------------------
# 0. Install required system tools
# -----------------------------
# -----------------------------
# 1. Setup Kaggle credentials
# -----------------------------
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)

with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
    f.write(f"""{{
  "username": "{os.environ['KAGGLE_USERNAME']}",
  "key": "{os.environ['KAGGLE_KEY']}"
}}""")

os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)

# -----------------------------
# 2. Setup rclone config
# -----------------------------
os.makedirs(os.path.expanduser("~/.config/rclone"), exist_ok=True)

with open(os.path.expanduser("~/.config/rclone/rclone.conf"), "wb") as f:
    f.write(base64.b64decode(os.environ["RCLONE_CONFIG_BASE64"]))

# -----------------------------
# 3. Download dataset from Drive
# -----------------------------
subprocess.run(
    f"rclone copy gdrive:upload_data {LOCAL_DIR} --progress --transfers 8 --checkers 8",
    shell=True,
    check=True
)

# -----------------------------
# 4. Upload to Kaggle
# -----------------------------
kagglehub.dataset_upload(
    DATASET_HANDLE,
    LOCAL_DIR,
    version_notes="Uploaded via Railway"
)

print("✅ Upload completed successfully!")
