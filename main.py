import os
import subprocess
import kagglehub
import base64
import urllib.request
import zipfile

DATASET_HANDLE = "tonmoyk983/sevtone-dataset-80"
LOCAL_DIR = "sevtone"

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
# 2. Download rclone manually
# -----------------------------
print("Installing rclone...")

url = "https://downloads.rclone.org/rclone-current-linux-amd64.zip"

urllib.request.urlretrieve(url, "rclone.zip")

with zipfile.ZipFile("rclone.zip", "r") as zip_ref:
    zip_ref.extractall()

folder = [f for f in os.listdir() if f.startswith("rclone-")][0]

rclone_path = os.path.abspath(
    os.path.join(folder, "rclone")
)

os.chmod(rclone_path, 0o755)

subprocess.run(
    [rclone_path, "version"],
    check=True
)

print("✅ Rclone ready")

# -----------------------------
# 3. Setup rclone config
# -----------------------------
print("Configuring rclone...")

os.makedirs(
    os.path.expanduser("~/.config/rclone"),
    exist_ok=True
)

with open(
    os.path.expanduser("~/.config/rclone/rclone.conf"),
    "wb"
) as f:
    f.write(
        base64.b64decode(
            os.environ["RCLONE_CONFIG_BASE64"]
        )
    )

# -----------------------------
# 4. Download from Drive
# -----------------------------
print("Downloading dataset...")

subprocess.run([
    rclone_path,
    "copy",
    "dataset:sevtone",
    LOCAL_DIR,
    "--progress",
    "--transfers", "8",
    "--checkers", "8",
    "--retries", "5"
], check=True)

print("✅ Download complete")

# -----------------------------
# 5. Upload to Kaggle
# -----------------------------
print("Uploading to Kaggle...")

kagglehub.dataset_upload(
    DATASET_HANDLE,
    LOCAL_DIR,
    version_notes="Uploaded via Render",
    is_private=False
)

print("🎉 Upload completed")
