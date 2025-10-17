"""
routfits_viewer_cli

Fetch and download all saved Roblox outfit thumbnails for a given user.

Requirements:
    pip install requests

Usage:
    python main.py <ROBLOX_USER_ID>
"""

import sys
import os
import time
import requests

# --- CONFIG ---
USER_AGENT = "RobloxOutfitViewer/1.0"
OUTFITS_API = "https://avatar.roblox.com/v1/users/{user_id}/outfits"
THUMBNAIL_API = "https://thumbnails.roblox.com/v1/users/outfits"
DELAY_BETWEEN_REQUESTS = 2.0  # seconds
MAX_RETRIES = 5
# --------------


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_outfits(user_id):
    """Fetch all outfits for the given user ID."""
    url = OUTFITS_API.format(user_id=user_id)
    headers = {"User-Agent": USER_AGENT}
    delay = 2

    for attempt in range(1, MAX_RETRIES + 1):
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200:
            return resp.json().get("data", [])

        elif resp.status_code == 429:
            print(f"⚠️ Rate limited (attempt {attempt}/{MAX_RETRIES}). Waiting {delay}s...")
            time.sleep(delay)
            delay *= 2  # exponentially increase delay

        else:
            resp.raise_for_status()

    raise Exception("Failed to fetch outfits after multiple retries.")


def get_outfit_thumbnail_url(outfit_id, size="420x420", fmt="Png", is_circular="false"):
    """Get a thumbnail URL for a specific outfit using Roblox’s thumbnails API."""
    params = {
        "userOutfitIds": str(outfit_id),
        "size": size,
        "format": fmt,
        "isCircular": is_circular,
    }
    headers = {"User-Agent": USER_AGENT}
    delay = 2
    for attempt in range(1, MAX_RETRIES + 1):
        resp = requests.get(THUMBNAIL_API, headers=headers, params=params, timeout=10)

        if resp.status_code == 200:
            data = resp.json().get("data", [])
            return data[0].get("imageUrl") if data else None

        elif resp.status_code == 429:
            print(f"⚠️ Rate limited (thumbnail attempt {attempt}/{MAX_RETRIES}). Waiting {delay}s...")
            time.sleep(delay)
            delay *= 2

        else:
            resp.raise_for_status()

    print(f"❌ Could not retrieve thumbnail for outfit {outfit_id}")
    return None


def download_image(url, save_path):
    """Download and save an image from a URL."""
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, stream=True, timeout=20)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(4096):
            f.write(chunk)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <ROBLOX_USER_ID>")
        sys.exit(1)

    user_id = sys.argv[1]
    user_folder = f"user_{user_id}"
    ensure_dir(user_folder)

    print(f"Fetching outfits for user {user_id}...")
    outfits = get_outfits(user_id)
    if not outfits:
        print("No outfits found.")
        return

    print(f"Found {len(outfits)} outfits. Starting downloads...\n")

    for i, outfit in enumerate(outfits, start=1):
        outfit_id = outfit["id"]
        outfit_name = outfit["name"].replace("/", "_")
        print(f"[{i}/{len(outfits)}] Fetching thumbnail for: {outfit_name} (ID: {outfit_id})")

        thumb_url = get_outfit_thumbnail_url(outfit_id)
        if not thumb_url:
            print("  ❌ Could not get thumbnail URL; skipping.")
            continue

        filename = f"outfit_{outfit_id}_{outfit_name}.png"
        save_path = os.path.join(user_folder, filename)

        try:
            download_image(thumb_url, save_path)
            print(f"  ✅ Saved to: {save_path}")
        except Exception as e:
            print(f"  ⚠️ Failed to download: {e}")

        time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\n✅ All available outfit thumbnails for user {user_id} downloaded!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)

