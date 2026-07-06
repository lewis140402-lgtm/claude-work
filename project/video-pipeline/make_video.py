#!/usr/bin/env python3
"""
One command, one finished video:

    python3 make_video.py "How this Raspberry Pi decides which garden bed to water"

Runs the full pipeline: script -> footage -> voiceover -> subtitles -> assembly.
Set PIPELINE_MOCK=1 (or leave PEXELS_API_KEY / ELEVENLABS_API_KEY unset) to
run entirely offline with synthetic placeholders, useful for a dry run
before spending API credits.
"""
import argparse
import sys

import assemble_video
import fetch_footage
import generate_script
import generate_subtitles
import generate_voiceover
from common import project_dir, slugify


def main():
    parser = argparse.ArgumentParser(description="Generate a finished short-form video from a topic.")
    parser.add_argument("topic", help="Video topic")
    args = parser.parse_args()

    slug = slugify(args.topic)
    script_path = project_dir(slug) / "script.json"
    if script_path.exists():
        print(f"=== [1/5] Script: using existing {script_path} ===")
    else:
        print(f"=== [1/5] Script: {args.topic} (generating from template) ===")
        generate_script.save_script(slug, generate_script.generate(args.topic))

    print(f"=== [2/5] Footage ===")
    fetch_footage.fetch_all(slug)

    print(f"=== [3/5] Voiceover ===")
    data = generate_voiceover.load_script(slug)
    audio_path = generate_voiceover.project_dir(slug) / "voiceover.mp3"
    if generate_voiceover.MOCK_MODE or not generate_voiceover.ELEVENLABS_API_KEY:
        generate_voiceover.synthesize_mock(data["voiceover_script"], audio_path)
    else:
        generate_voiceover.synthesize_elevenlabs(data["voiceover_script"], audio_path)
    duration = generate_voiceover.ffprobe_duration(audio_path)
    data = generate_voiceover.assign_scene_timing(data, duration)
    generate_voiceover.save_script(slug, data)

    print(f"=== [4/5] Subtitles ===")
    captions = generate_subtitles.build_captions(data)
    generate_subtitles.write_srt(captions, generate_subtitles.project_dir(slug) / "subtitles.srt")

    print(f"=== [5/5] Assembly ===")
    assemble_video.assemble(slug)

    print(f"\nAll done: {slug}")


if __name__ == "__main__":
    sys.exit(main())
