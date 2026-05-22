import os
import subprocess
import kagglehub
import base64
import urllib.request
import re

DATASET_HANDLE = "tonmoyk983/sevtone-half-inter4k-input"

# Folder structure to keep in Kaggle
LOCAL_DIR = "sevtone/Inter4K_png/Raw/Input"
DATASET_DIR = "sevtone"

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
  "username":"{os.environ['KAGGLE_USERNAME']}",
  "key":"{os.environ['KAGGLE_KEY']}"
}}""")

os.chmod(
    os.path.expanduser("~/.kaggle/kaggle.json"),
    0o600
)

# -----------------------------
# 2. Install rclone
# -----------------------------
print("Installing rclone...")

urllib.request.urlretrieve(
    "https://downloads.rclone.org/rclone-current-linux-amd64.zip",
    "rclone.zip"
)

subprocess.run(
    "rm -rf rclone-* && unzip -o rclone.zip",
    shell=True,
    check=True
)

folder = [
    f for f in os.listdir()
    if f.startswith("rclone-")
]

folder = folder[0]

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
# 4. Create file list
# Videos 1-500 only
# -----------------------------
print("Reading file list...")

result = subprocess.run(
    f"{rclone_path} lsf dataset:sevtone/Inter4K_png/Raw/Input -R",
    shell=True,
    capture_output=True,
    text=True,
    check=True
)

all_files = [
    x.strip()
    for x in result.stdout.splitlines()
    if x.strip()
]

selected = []

# Match:
# Inter4K_vid_1_f001_in1.png

pattern = re.compile(
    r"Inter4K_vid_(\d+)_f(\d+)_in(\d+)\.png"
)

for file in all_files:

    filename = os.path.basename(file)

    m = pattern.match(filename)

    if m:

        vid = int(m.group(1))
        frame = int(m.group(2))
        in_num = int(m.group(3))

        if 1 <= vid <= 500:
            selected.append(
                (
                    vid,
                    frame,
                    in_num,
                    file
                )
            )

# Sort:
# vid1→vid2→...
# frame001→081→161→241
# in1→in7

selected.sort(
    key=lambda x: (
        x[0],
        x[1],
        x[2]
    )
)

with open(
    "video_1_500.txt",
    "w"
) as f:

    for _, _, _, file in selected:
        f.write(file + "\n")

print(
    f"Selected files: {len(selected)}"
)

# Preview first lines
print("\nFirst 30 files:\n")

with open(
    "video_1_500.txt",
    "r"
) as f:

    for i, line in enumerate(f):

        if i >= 30:
            break

        print(
            line.strip()
        )

# -----------------------------
# 5. Download files
# -----------------------------
print(
    "\nDownloading videos 1-500..."
)

os.makedirs(
    LOCAL_DIR,
    exist_ok=True
)

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
print("Uploading...")

kagglehub.dataset_upload(
    DATASET_HANDLE,
    DATASET_DIR,
    version_notes="Inter4K videos 1-500 only"
)

print("🎉 Upload completed")
