#!/usr/bin/env python3
"""
Stage 2: script.json -> one downloaded stock clip per scene, cached locally.

    python3 fetch_footage.py <slug>

Uses the Pexels Videos API (free tier: https://www.pexels.com/api/, needs a
free PEXELS_API_KEY in .env). Set PIPELINE_MOCK=1 to skip the network call
and generate synthetic placeholder clips instead (useful for testing the
rest of the pipeline without API keys or network access).
"""
import argparse
import sys

import requests

from common import FOOTAGE_DIR, MOCK_MODE, PEXELS_API_KEY, load_script, project_dir, run

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"


def scene_clip_path(slug: str, scene_id: int):
    return project_dir(slug) / "footage" / f"scene_{scene_id:02d}.mp4"


def pick_best_video_file(video: dict) -> str:
    """Prefer HD (720p-1080p) files to keep downloads small; fall back to the largest available."""
    files = sorted(video.get("video_files", []), key=lambda f: f.get("width", 0) or 0)
    for f in files:
        if f.get("width") and 720 <= f["width"] <= 1080:
            return f["link"]
    return files[-1]["link"] if files else None


def fetch_from_pexels(query: str, dest_path):
    resp = requests.get(
        PEXELS_SEARCH_URL,
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": 5, "orientation": "portrait"},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json().get("videos", [])
    if not results:
        return False
    link = pick_best_video_file(results[0])
    if not link:
        return False
    video_resp = requests.get(link, timeout=60, stream=True)
    video_resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in video_resp.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    return True


def make_mock_clip(label: str, dest_path, duration: int = 6):
    """Generate a synthetic labeled test clip with ffmpeg — no network required."""
    safe_label = label.replace("'", "").replace(":", "-")[:40]
    run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"testsrc2=size=1080x1920:rate=30:duration={duration}",
        "-vf", f"drawtext=text='{safe_label}':fontcolor=white:fontsize=48:"
               f"x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:boxborderw=20",
        "-pix_fmt", "yuv420p", str(dest_path),
    ])


def fetch_all(slug: str):
    data = load_script(slug)
    footage_dir = project_dir(slug) / "footage"
    footage_dir.mkdir(exist_ok=True)

    for scene in data["scenes"]:
        dest = scene_clip_path(slug, scene["id"])
        if dest.exists():
            print(f"  scene {scene['id']}: cached, skipping")
            continue

        if MOCK_MODE or not PEXELS_API_KEY:
            reason = "PIPELINE_MOCK=1" if MOCK_MODE else "no PEXELS_API_KEY set"
            print(f"  scene {scene['id']}: {reason} -> generating placeholder clip")
            make_mock_clip(scene["search_terms"][0], dest)
            continue

        got_clip = False
        for term in scene["search_terms"]:
            print(f"  scene {scene['id']}: searching Pexels for '{term}'")
            try:
                if fetch_from_pexels(term, dest):
                    got_clip = True
                    break
            except requests.RequestException as e:
                print(f"    request failed: {e}", file=sys.stderr)
        if not got_clip:
            print(f"  scene {scene['id']}: no Pexels match, falling back to placeholder")
            make_mock_clip(scene["search_terms"][0], dest)

    print(f"Footage ready in {footage_dir}")


def main():
    parser = argparse.ArgumentParser(description="Download/generate stock footage for a script's scenes.")
    parser.add_argument("slug", help="Project slug (from generate_script.py output)")
    args = parser.parse_args()
    fetch_all(args.slug)


if __name__ == "__main__":
    main()
