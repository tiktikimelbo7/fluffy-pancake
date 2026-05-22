import os, subprocess, kagglehub, base64, urllib.request, re, shutil

DATASET_HANDLE = "tonmoyk983/sevtone-half-inter4k-vcip"
LOCAL_DIR = "sevtone"

# Install tools
print("Installing system tools...")
subprocess.run("apt update && apt install -y unzip ca-certificates",
               shell=True, check=True)

# Kaggle credentials
print("Setting up Kaggle credentials...")
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)

with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
    f.write(f"""{{
  "username":"{os.environ['KAGGLE_USERNAME']}",
  "key":"{os.environ['KAGGLE_KEY']}"
}}""")

os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)

# Install rclone
print("Installing rclone...")
urllib.request.urlretrieve(
    "https://downloads.rclone.org/rclone-current-linux-amd64.zip",
    "rclone.zip"
)

subprocess.run(
    "rm -rf rclone-* && unzip -o rclone.zip",
    shell=True, check=True
)

folder = [f for f in os.listdir() if f.startswith("rclone-")][0]
rclone_path = os.path.abspath(f"{folder}/rclone")

subprocess.run(f"chmod +x {rclone_path}", shell=True, check=True)
subprocess.run(f"{rclone_path} version", shell=True, check=True)

print("✅ Rclone ready")

# Rclone config
print("Configuring rclone...")
os.makedirs(os.path.expanduser("~/.config/rclone"), exist_ok=True)

with open(os.path.expanduser("~/.config/rclone/rclone.conf"), "wb") as f:
    f.write(base64.b64decode(os.environ["RCLONE_CONFIG_BASE64"]))

# Prepare folders
if os.path.exists(LOCAL_DIR):
    shutil.rmtree(LOCAL_DIR)

os.makedirs(f"{LOCAL_DIR}/Inter4K_png/Raw/Input", exist_ok=True)
os.makedirs(f"{LOCAL_DIR}/Inter4K_png/Raw/Output", exist_ok=True)
os.makedirs(f"{LOCAL_DIR}/VCIP_png", exist_ok=True)

# Read Inter4K files
print("Reading Inter4K files...")

result = subprocess.run(
    f"{rclone_path} lsf dataset:sevtone/Inter4K_png/Raw/Input -R",
    shell=True, capture_output=True, text=True, check=True
)

files = [x.strip() for x in result.stdout.splitlines() if x.strip()]
selected = []

pattern = re.compile(r"Inter4K_vid_(\d+)_f(\d+)_in(\d+)\.png")

for file in files:
    m = pattern.match(os.path.basename(file))

    if m:
        vid = int(m.group(1))
        frame = int(m.group(2))
        in_num = int(m.group(3))

        if 501 <= vid <= 1000:
            selected.append((vid, frame, in_num, file))

selected.sort(key=lambda x: (x[0], x[1], x[2]))

with open("second_half.txt", "w") as f:
    for _, _, _, file in selected:
        f.write(file + "\n")

print(f"Selected Inter4K files: {len(selected)}")

# Download Inter4K input (501-1000 only)
print("Downloading Inter4K Input...")

subprocess.run(
    f"{rclone_path} copy "
    f"dataset:sevtone/Inter4K_png/Raw/Input "
    f"{LOCAL_DIR}/Inter4K_png/Raw/Input "
    f"--files-from second_half.txt "
    f"--progress --transfers 8 --checkers 8 --retries 5",
    shell=True, check=True
)

print("✅ Inter4K Input complete")

# Download full Inter4K output
print("Downloading full Inter4K Output...")

subprocess.run(
    f"{rclone_path} copy "
    f"dataset:sevtone/Inter4K_png/Raw/Output "
    f"{LOCAL_DIR}/Inter4K_png/Raw/Output "
    f"--progress --transfers 8 --checkers 8 --retries 5",
    shell=True, check=True
)

print("✅ Inter4K Output complete")

# Download full VCIP
print("Downloading full VCIP...")

subprocess.run(
    f"{rclone_path} copy "
    f"dataset:sevtone/VCIP_png "
    f"{LOCAL_DIR}/VCIP_png "
    f"--progress --transfers 8 --checkers 8 --retries 5",
    shell=True, check=True
)

print("✅ VCIP complete")

# Upload
print("Uploading to Kaggle...")

kagglehub.dataset_upload(
    DATASET_HANDLE,
    LOCAL_DIR,
    version_notes="Inter4K input 501-1000 + full Inter4K output + full VCIP"
)

print("🎉 Upload completed successfully!")
