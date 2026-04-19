import os
import json
import subprocess
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

PHOTO_DIR = "images"
REVIEW_DIR = "review"
OUTPUT_JSON = "data.json"

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

photos_data = []
seen_photos = []

# 🔥 Autocomplete memory
camera_history = set()
state_history = set()
country_history = set()
title_history = set()
tag_history = set()

if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r+") as f:
        photos_data = json.load(f)

        for photo in photos_data:
            seen_photos.append(photo["src"])
            camera_history.add(photo["camera"])
            state_history.add(photo["location"]["state"])
            country_history.add(photo["location"]["country"])
            title_history.add(photo["caption"])
            for tag in photo["tags"]:
                tag_history.add(tag)

os.makedirs(REVIEW_DIR, exist_ok=True)


def get_exif_data(filepath):
    try:
        img = Image.open(filepath)
        exif = img._getexif()
        if not exif:
            return {}
        return {TAGS.get(tag, tag): value for tag, value in exif.items()}
    except Exception:
        return {}


def get_camera_model(exif):
    return exif.get("Model")


def get_date_taken(exif, filepath):
    date = exif.get("DateTimeOriginal") or exif.get("DateTime")
    if date:
        return date
    return str(os.path.getmtime(filepath))


def preview_image(filepath):
    try:
        if os.name == "nt":
            os.startfile(filepath)
        elif os.uname().sysname == "Darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])
    except Exception as e:
        print(f"Preview error: {e}")


def progress_bar(current, total, width=30):
    ratio = current / total
    filled = int(ratio * width)
    bar = "█" * filled + "-" * (width - filled)
    return f"[{bar}] {current}/{total}"


# 🔥 Collect + sort
files = []

for filename in os.listdir(PHOTO_DIR):
    if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
        print(f"Failed to process {filename} due to extension")
        continue

    filepath = os.path.join(PHOTO_DIR, filename)
    exif = get_exif_data(filepath)
    date_taken = get_date_taken(exif, filepath)

    files.append((filepath, filename, exif, date_taken))

files.sort(key=lambda x: x[3])
total_files = len(files)


# 🔁 Process
for idx, (filepath, filename, exif, _) in enumerate(files, start=1):
    # Check if file is already accounted for
    if filepath in seen_photos:
        print(f"Already Seen: {filename}")
        continue

    print("\n" + "=" * 50)
    print(progress_bar(idx, total_files))
    print(f"Processing: {filename}")
    seen_photos.append(filepath)

    preview_image(filepath)

    action = input("Keep (Enter) / Move to review (r) / Skip (s): ").strip().lower()

    if action == "r":
        shutil.move(filepath, os.path.join(REVIEW_DIR, filename))
        print("Moved to review/")
        continue

    if action == "s":
        print("Skipped")
        continue

    detected_camera = get_camera_model(exif)

    camera_completer = WordCompleter(list(camera_history), ignore_case=True)
    state_completer = WordCompleter(list(state_history), ignore_case=True)
    country_completer = WordCompleter(list(country_history), ignore_case=True)
    title_completer = WordCompleter(list(title_history), ignore_case=True)
    tag_completer = WordCompleter(list(tag_history), ignore_case=True)

    # Camera
    if detected_camera:
        if "iPhone" in detected_camera:
            detected_camera = "iPhone"
        confirm = input(f"Detected camera: '{detected_camera}'. Is this correct? (Y/n): ").strip().lower()
        if confirm == "n":
            camera = prompt("Camera: ", completer=camera_completer)
        else:
            camera = detected_camera
    else:
        camera = prompt("Camera: ", completer=camera_completer)

    camera_history.add(camera)

    # Location
    state = prompt("State: ", completer=state_completer)
    state_history.add(state)

    country = prompt("Country: ", completer=country_completer)
    country_history.add(country)

    # Title
    title = prompt("Title (optional): ", completer=title_completer)
    if title:
        title_history.add(title)

    # Tags
    tags_input = prompt("Tags (comma separated): ", completer=tag_completer)

    tags = []
    if tags_input:
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]
        for t in tags:
            tag_history.add(t)

    photo_entry = {
        "src": filepath.replace("\\", "/"),
        "camera": camera,
        "caption": title,
        "location": {
            "state": state,
            "country": country,
        },
        "tags": tags
    }

    photos_data.append(photo_entry)


with open(OUTPUT_JSON, "w") as f:
    json.dump(photos_data, f, indent=2)

print("\nDone!")