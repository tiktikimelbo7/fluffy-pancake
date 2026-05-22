import os
import subprocess
import kagglehub
import base64
import urllib.request

DATASET_HANDLE = "tonmoyk983/sevtone-half-inter4k-input"
LOCAL_DIR = "sevtone/Inter4K_png/Raw/Input"

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

os.makedirs(
    os.path.expanduser("~/.kaggle"),
    exist_ok=True
)

with open(
    os.path.expanduser("~/.kaggle/kaggle.json"),
    "w"
) as f:

    f.write(f"""{{
  "username": "{os.environ['KAGGLE_USERNAME']}",
  "key": "{os.environ['KAGGLE_KEY']}"
}}""")

os.chmod(
    os.path.expanduser("~/.kaggle/kaggle.json"),
    0o600
)

# -----------------------------
# 2. Install rclone
# -----------------------------
print("Installing rclone...")

url = "https://downloads.rclone.org/rclone-current-linux-amd64.zip"
zip_path = "rclone.zip"

urllib.request.urlretrieve(
    url,
    zip_path
)

subprocess.run(
    "rm -rf rclone-v1.74.1-linux-amd64 && unzip rclone.zip",
    shell=True,
    check=True
)

folder = [
    f for f in os.listdir()
    if f.startswith("rclone-")
][0]

rclone_path = os.path.abspath(
    f"{folder}/rclone"
)

subprocess.run(
    f"chmod +x {rclone_path}",
    shell=True,
    check=True
)

subprocess.run(
    f"{rclone_path} version",
    shell=True,
    check=True
)

print("✅ Rclone ready:", rclone_path)

# -----------------------------
# 3. Setup rclone config
# -----------------------------
print("Configuring rclone...")

os.makedirs(
    os.path.expanduser("~/.config/rclone"),
    exist_ok=True
)

with open(
    os.path.expanduser(
        "~/.config/rclone/rclone.conf"
    ),
    "wb"
) as f:

    f.write(
        base64.b64decode(
            os.environ["RCLONE_CONFIG_BASE64"]
        )
    )

print("✅ Rclone configured")

# -----------------------------
# 4. Create file list for videos 1-500
# -----------------------------
print("Reading file list from Google Drive...")

result = subprocess.run(
    f"{rclone_path} lsf dataset:sevtone/Inter4K_png/Raw/Input -R",
    shell=True,
    capture_output=True,
    text=True,
    check=True
)

all_files = [
    f.strip()
    for f in result.stdout.splitlines()
    if f.strip()
]

selected_files = []

for file in sorted(all_files):

    filename = os.path.basename(file)

    # Example:
    # Inter4K_vid_1_f001_in1.png
    if filename.startswith("Inter4K_vid_"):

        try:
            vid_num = int(
                filename.split("_")[2]
            )

            if 1 <= vid_num <= 500:
                selected_files.append(file)

        except:
            pass

print(f"Total selected files: {len(selected_files)}")

with open("video_1_500.txt", "w") as f:
    for file in selected_files:
        f.write(file + "\n")

print("✅ File list prepared")

# -----------------------------
# 5. Download selected files
# -----------------------------
print("Downloading videos 1-500...")

subprocess.run(
    f"{rclone_path} copy "
    f"dataset:sevtone/Inter4K_png/Raw/Input "
    f"{LOCAL_DIR} "
    f"--files-from video_1_500.txt "
    f"--progress "
    f"--transfers 8 "
    f"--checkers 8 "
    f"--retries 5",
    shell=True,
    check=True
)

print("✅ Download complete")

# -----------------------------
# 6. Upload to Kaggle
# -----------------------------
print("Uploading to Kaggle...")

kagglehub.dataset_upload(
    DATASET_HANDLE,
    LOCAL_DIR,
    version_notes="Uploaded Inter4K videos 1-500"
)

print("🎉 Upload completed successfully!")
