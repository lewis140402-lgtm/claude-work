"""Shared config, paths, and small ffmpeg/ffprobe helpers used by every pipeline stage."""
import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel", a default stock voice
MOCK_MODE = os.environ.get("PIPELINE_MOCK", "0") == "1"

OUTPUT_DIR = ROOT / "output"
CACHE_DIR = ROOT / "cache"
FOOTAGE_DIR = CACHE_DIR / "footage"
AUDIO_DIR = CACHE_DIR / "audio"

for d in (OUTPUT_DIR, FOOTAGE_DIR, AUDIO_DIR):
    d.mkdir(parents=True, exist_ok=True)


def project_dir(slug: str) -> Path:
    d = ROOT / "projects" / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def slugify(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text.strip()]
    slug = "".join(keep)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:60] or "untitled"


def load_script(slug: str) -> dict:
    path = project_dir(slug) / "script.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No script.json found for '{slug}'. Run generate_script.py first."
        )
    return json.loads(path.read_text())


def save_script(slug: str, data: dict) -> Path:
    path = project_dir(slug) / "script.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def ffprobe_duration(path) -> float:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def run(cmd: list[str]):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n{result.stderr[-4000:]}"
        )
    return result
