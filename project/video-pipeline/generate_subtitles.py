#!/usr/bin/env python3
"""
Stage 4: script.json (with scene timing) -> subtitles.srt

    python3 generate_subtitles.py <slug>

Splits each scene's text into short caption chunks (~6 words) and spreads
them evenly across that scene's [start, end] window, so captions land
roughly in sync with the voiceover without needing word-level alignment.
"""
import argparse

from common import project_dir, load_script

WORDS_PER_CAPTION = 6


def srt_timestamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_captions(data: dict) -> list[tuple[float, float, str]]:
    captions = []
    for scene in data["scenes"]:
        words = scene["text"].split()
        start, end = scene["start"], scene["end"]
        duration = end - start
        chunks = [words[i:i + WORDS_PER_CAPTION] for i in range(0, len(words), WORDS_PER_CAPTION)] or [[]]
        per_chunk = duration / len(chunks)
        for i, chunk in enumerate(chunks):
            c_start = start + i * per_chunk
            c_end = c_start + per_chunk
            captions.append((c_start, c_end, " ".join(chunk)))
    return captions


def write_srt(captions: list[tuple[float, float, str]], dest_path):
    lines = []
    for i, (start, end, text) in enumerate(captions, start=1):
        lines.append(str(i))
        lines.append(f"{srt_timestamp(start)} --> {srt_timestamp(end)}")
        lines.append(text)
        lines.append("")
    dest_path.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Generate an SRT subtitle file from a timed script.")
    parser.add_argument("slug", help="Project slug (must already have scene timing from generate_voiceover.py)")
    args = parser.parse_args()

    data = load_script(args.slug)
    if "start" not in data["scenes"][0]:
        raise SystemExit("No scene timing found — run generate_voiceover.py first.")

    captions = build_captions(data)
    dest = project_dir(args.slug) / "subtitles.srt"
    write_srt(captions, dest)
    print(f"Wrote {len(captions)} captions -> {dest}")


if __name__ == "__main__":
    main()
