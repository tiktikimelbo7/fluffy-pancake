import os
import subprocess
import kagglehub
import base64
import urllib.request
import re

DATASET_HANDLE = "tonmoyk983/sevtone-half-inter4k-input"
LOCAL_DIR = "sevtone/Inter4K_png/Raw/Input"
DATASET_DIR = "sevtone"

# -----------------------------
# 0. Install required tools
# -----------------------------
print("Installing system tools...")
subprocess.run(
    "apt update && apt install -y unzip ca-certificates",
    shell=True, check=True
)

# -----------------------------
# 1. Setup Kaggle credentials
# -----------------------------
print("Setting up Kaggle credentials...")
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
    f.write(f"""{{ "username":"{os.environ['KAGGLE_USERNAME']}", "key":"{os.environ['KAGGLE_KEY']}" }}""")
os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)

# -----------------------------
# 2. Install rclone
# -----------------------------
print("Installing rclone...")
urllib.request.urlretrieve(
    "https://downloads.rclone.org/rclone-current-linux-amd64.zip",
    "rclone.zip"
)
subprocess.run("rm -rf rclone-v1.74.1-linux-amd64 && unzip -o rclone.zip", shell=True, check=True)
folder = [f for f in os.listdir() if f.startswith("rclone-")][0]
rclone_path = os.path.abspath(f"{folder}/rclone")
subprocess.run(f"chmod +x {rclone_path}", shell=True, check=True)
print("✅ Rclone ready")

# -----------------------------
# 3. Setup rclone config
# -----------------------------
print("Configuring rclone...")
os.makedirs(os.path.expanduser("~/.config/rclone"), exist_ok=True)
with open(os.path.expanduser("~/.config/rclone/rclone.conf"), "wb") as f:
    f.write(base64.b64decode(os.environ["RCLONE_CONFIG_BASE64"]))

# -----------------------------
# 4. Create file list for videos 1-500
#    ONLY the required frame groups:
#       1-7, 81-87, 161-167, 241-247
# -----------------------------
print("Reading file list...")
result = subprocess.run(
    f"{rclone_path} lsf dataset:sevtone/Inter4K_png/Raw/Input -R",
    shell=True, capture_output=True, text=True, check=True
)
all_files = [x.strip() for x in result.stdout.splitlines() if x.strip()]
selected = []

# Allowed frame ranges
ALLOWED_FRAMES = set(range(1, 8)) | set(range(81, 88)) | set(range(161, 168)) | set(range(241, 248))

pattern = re.compile(r"Inter4K_vid_(\d+)_f(\d+)_in\d+\.png")
for file in all_files:
    filename = os.path.basename(file)
    m = pattern.match(filename)
    if m:
        vid = int(m.group(1))
        frame = int(m.group(2))
        if 1 <= vid <= 500 and frame in ALLOWED_FRAMES:
            selected.append((vid, frame, file))

# Sort by video, then by frame
selected.sort(key=lambda x: (x[0], x[1]))

with open("video_1_500.txt", "w") as f:
    for _, _, file in selected:
        f.write(file + "\n")

print(f"Selected {len(selected)} files")

# Print first and last 50 entries to verify order
print("\n===== First 50 entries =====\n")
with open("video_1_500.txt", "r") as f:
    for i, line in enumerate(f):
        if i >= 50:
            break
        print(line.strip())

print("\n===== Last 50 entries =====\n")
with open("video_1_500.txt", "r") as f:
    lines = f.readlines()
    for line in lines[-50:]:
        print(line.strip())

# -----------------------------
# 5. Download files
# -----------------------------
print("Downloading videos 1-500 (only selected frames)...")
subprocess.run(
    f"{rclone_path} copy "
    f"dataset:sevtone/Inter4K_png/Raw/Input "
    f"{LOCAL_DIR} "
    f"--files-from video_1_500.txt "
    f"--progress "
    f"--transfers 8 "
    f"--checkers 8",
    shell=True, check=True
)
print("✅ Download complete")

# -----------------------------
# 6. Upload to Kaggle
# -----------------------------
print("Uploading...")
kagglehub.dataset_upload(
    DATASET_HANDLE,
    DATASET_DIR,
    version_notes="Inter4K videos 1-500 only (frames 1-7,81-87,161-167,241-247)"
)
print("🎉 Upload completed")
