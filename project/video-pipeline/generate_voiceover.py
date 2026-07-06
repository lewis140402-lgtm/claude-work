#!/usr/bin/env python3
"""
Stage 3: script.json -> voiceover.mp3 + per-scene timing.

    python3 generate_voiceover.py <slug>

Uses the ElevenLabs text-to-speech API (needs ELEVENLABS_API_KEY in .env).
Set PIPELINE_MOCK=1 to generate silent placeholder audio instead, sized to
an estimated speech duration (~2.5 words/sec) — enough to test scene timing
and subtitle sync without an API key.

Writes projects/<slug>/voiceover.mp3 and updates script.json with
scene[i]["start"] / scene[i]["end"] (seconds).
"""
import argparse

import requests

from common import (
    ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, MOCK_MODE,
    ffprobe_duration, load_script, project_dir, run, save_script,
)

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
WORDS_PER_SECOND = 2.5  # rough average spoken pace, used for mock timing + as a sanity check


def synthesize_elevenlabs(text: str, dest_path):
    resp = requests.post(
        ELEVENLABS_TTS_URL.format(voice_id=ELEVENLABS_VOICE_ID),
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=120,
    )
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)


def synthesize_mock(text: str, dest_path):
    word_count = max(len(text.split()), 1)
    duration = word_count / WORDS_PER_SECOND
    run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
        "-t", f"{duration:.2f}", "-q:a", "9", str(dest_path),
    ])


def assign_scene_timing(data: dict, total_duration: float) -> dict:
    """Split total voiceover duration across scenes proportional to word count."""
    word_counts = [max(len(s["text"].split()), 1) for s in data["scenes"]]
    total_words = sum(word_counts)
    t = 0.0
    for scene, wc in zip(data["scenes"], word_counts):
        dur = total_duration * (wc / total_words)
        scene["start"] = round(t, 2)
        scene["end"] = round(t + dur, 2)
        scene["duration"] = round(dur, 2)
        t += dur
    return data


def main():
    parser = argparse.ArgumentParser(description="Generate voiceover audio + scene timing for a script.")
    parser.add_argument("slug", help="Project slug (from generate_script.py output)")
    args = parser.parse_args()

    data = load_script(args.slug)
    audio_path = project_dir(args.slug) / "voiceover.mp3"

    if MOCK_MODE or not ELEVENLABS_API_KEY:
        reason = "PIPELINE_MOCK=1" if MOCK_MODE else "no ELEVENLABS_API_KEY set"
        print(f"{reason} -> generating silent placeholder audio")
        synthesize_mock(data["voiceover_script"], audio_path)
    else:
        print("Calling ElevenLabs TTS...")
        synthesize_elevenlabs(data["voiceover_script"], audio_path)

    duration = ffprobe_duration(audio_path)
    print(f"Voiceover duration: {duration:.2f}s")

    data = assign_scene_timing(data, duration)
    save_script(args.slug, data)
    print(f"Scene timing written to script.json")


if __name__ == "__main__":
    main()
