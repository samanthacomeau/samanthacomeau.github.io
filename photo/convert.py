import os
import json
from PIL import Image
import pillow_heif

# Enable HEIC support in Pillow
pillow_heif.register_heif_opener()

PHOTO_DIR = "images"
JSON_FILE = "data.json"

SUPPORTED_HEIC = (".heic", ".HEIC")


def convert_heic_to_jpg(filepath):
    img = Image.open(filepath)

    new_path = os.path.splitext(filepath)[0] + ".jpg"
    rgb_img = img.convert("RGB")
    rgb_img.save(new_path, "JPEG", quality=95)

    return new_path


# -------------------------
# 1. Load JSON
# -------------------------
with open(JSON_FILE, "r") as f:
    data = json.load(f)


updated_data = []

# -------------------------
# 2. Convert images + update JSON
# -------------------------
for item in data:
    src = item["src"]

    if src.lower().endswith(SUPPORTED_HEIC):

        print(f"Converting: {src}")

        new_src = convert_heic_to_jpg(src)

        # Update JSON path
        item["src"] = new_src.replace("\\", "/")

    updated_data.append(item)


# -------------------------
# 3. Save updated JSON
# -------------------------
with open(JSON_FILE, "w") as f:
    json.dump(updated_data, f, indent=2)

print("\nDone! JSON updated and HEIC files converted.")