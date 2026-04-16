import os
import json
import subprocess

PHOTO_DIR = "images"
OUTPUT_JSON = "bucket_list.json"

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".heic")

bucket_items = []


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


def clean_input(prompt_text):
    return input(prompt_text).strip()

def collect_resources():
    print("\nEnter resource links (press ENTER on empty line to finish):")
    print("Examples: AllTrails, Google Maps, booking pages, guides")

    resources = []

    while True:
        link = input("  • ").strip()
        if link == "":
            break
        resources.append(link)

    return resources


def collect_ideas():
    print("\nEnter specific ideas (press ENTER on empty line to finish):")
    ideas = []

    while True:
        idea = input("  • ").strip()
        if idea == "":
            break
        ideas.append(idea)

    return ideas


for filename in os.listdir(PHOTO_DIR):
    if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
        continue

    filepath = os.path.join(PHOTO_DIR, filename)

    print("\n" + "=" * 50)
    print(f"Processing: {filename}")

    preview_image(filepath)

    action = clean_input("Keep (Enter) / Skip (s) / Move to review (r): ").lower()

    if action == "s":
        print("Skipped")
        continue

    if action == "r":
        review_dir = "review"
        os.makedirs(review_dir, exist_ok=True)
        os.rename(filepath, os.path.join(review_dir, filename))
        print("Moved to review/")
        continue

    # ----------------------------
    # Core metadata
    # ----------------------------
    item = clean_input("Item (bucket list goal): ")
    season = clean_input("Season (spring/summer/fall/winter/any): ")
    cost = clean_input("Cost ($/$$/$$$/free): ")
    location = clean_input("Location: ")
    time_required = clean_input("Time required (e.g. 2 hours, 1 day, weekend): ")

    # ----------------------------
    # NEW: detailed ideas
    # ----------------------------
    ideas = collect_ideas()

    # ----------------------------
    # NEW: detailed resources
    # ----------------------------
    resources = collect_resources()


    entry = {
        "src": filepath.replace("\\", "/"),
        "item": item,
        "season": season,
        "cost": cost,
        "location": location,
        "time_required": time_required,
        "ideas": ideas,
        "resources": resources
    }

    bucket_items.append(entry)


with open(OUTPUT_JSON, "w") as f:
    json.dump(bucket_items, f, indent=2)

print(f"\nDone! Wrote {len(bucket_items)} bucket list items.")