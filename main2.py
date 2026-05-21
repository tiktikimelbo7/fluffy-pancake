import os
import subprocess
import kagglehub
import base64
import urllib.request

DATASET_HANDLE = "tonmoyk983/quadruple-dataset-org-60"
LOCAL_DIR = "upload_data"

# -----------------------------
# 0. Install required tools
# -----------------------------
print("Installing system tools...")
subprocess.run(
    "apt update && apt install -y unzip ca-certificates",
    shell=True,
    check=True
)

# -----------------------------
# 1. Setup Kaggle credentials
# -----------------------------
print("Setting up Kaggle credentials...")
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)

with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
    f.write(f"""{{
  "username": "{os.environ['KAGGLE_USERNAME']}",
  "key": "{os.environ['KAGGLE_KEY']}"
}}""")

os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)

# -----------------------------
# 2. Install rclone (MANUAL - FIXED)
# -----------------------------
print("Installing rclone manually...")

url = "https://downloads.rclone.org/rclone-current-linux-amd64.zip"
zip_path = "rclone.zip"

urllib.request.urlretrieve(url, zip_path)

subprocess.run("unzip rclone.zip", shell=True, check=True)

# Find extracted folder
folder = [f for f in os.listdir() if f.startswith("rclone-")][0]
rclone_path = os.path.abspath(f"{folder}/rclone")

# Make executable
subprocess.run(f"chmod +x {rclone_path}", shell=True, check=True)

# Test rclone
subprocess.run(f"{rclone_path} version", shell=True, check=True)

print("✅ Rclone ready at:", rclone_path)

# -----------------------------
# 3. Setup rclone config
# -----------------------------
print("Configuring rclone...")
os.makedirs(os.path.expanduser("~/.config/rclone"), exist_ok=True)

with open(os.path.expanduser("~/.config/rclone/rclone.conf"), "wb") as f:
    f.write(base64.b64decode(os.environ["RCLONE_CONFIG_BASE64"]))

# -----------------------------
# 4. Download dataset from Drive
# -----------------------------
print("Downloading dataset from Google Drive...")

subprocess.run(
    f"{rclone_path} copy dataset:upload_data {LOCAL_DIR} "
    "--progress --transfers 8 --checkers 8 --retries 5",
    shell=True,
    check=True
)

print("✅ Download complete")

# -----------------------------
# 5. Upload to Kaggle
# -----------------------------
print("Uploading to Kaggle...")

kagglehub.dataset_upload(
    DATASET_HANDLE,
    LOCAL_DIR,
    version_notes="Uploaded via Railway (rclone fixed)"
)

print("🎉 Upload completed successfully!")
