import os
import subprocess
import kagglehub
import base64

DATASET_HANDLE = "tonmoyk983/quadruplet-dataset-60"
LOCAL_DIR = "upload_data"

# -----------------------------
# Kaggle setup
# -----------------------------
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)

with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
    f.write(f"""{{
  "username": "{os.environ['KAGGLE_USERNAME']}",
  "key": "{os.environ['KAGGLE_KEY']}"
}}""")

os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)


# Install curl if missing
subprocess.run("apt update && apt install -y curl", shell=True, check=True)

# -----------------------------
# Install rclone
# -----------------------------
subprocess.run("curl https://rclone.org/install.sh | bash", shell=True, check=True)

# -----------------------------
# Setup rclone config
# -----------------------------
os.makedirs(os.path.expanduser("~/.config/rclone"), exist_ok=True)

with open(os.path.expanduser("~/.config/rclone/rclone.conf"), "wb") as f:
    f.write(base64.b64decode(os.environ["RCLONE_CONFIG_BASE64"]))

# -----------------------------
# Download dataset from Drive
# -----------------------------
subprocess.run(
    f"rclone copy gdrive:upload_data {LOCAL_DIR} --progress",
    shell=True,
    check=True
)

# -----------------------------
# Upload to Kaggle
# -----------------------------
kagglehub.dataset_upload(
    DATASET_HANDLE,
    LOCAL_DIR,
    version_notes="Uploaded via Railway"
)

print("✅ Done!")
