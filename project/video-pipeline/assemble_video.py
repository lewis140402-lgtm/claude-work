#!/usr/bin/env python3
"""
Stage 5: footage + voiceover + subtitles -> finished 9:16 and 16:9 video files.

    python3 assemble_video.py <slug>

For each scene, loops/trims its footage clip to the scene's exact duration
(from generate_voiceover.py timing), scales+crops to the target aspect
ratio, concatenates all scenes, muxes in the voiceover, and burns in the
subtitle track. Produces both a 9:16 (TikTok/Shorts) and 16:9 (YouTube)
export.
"""
import argparse
import shutil
import tempfile
from pathlib import Path

from common import OUTPUT_DIR, project_dir, load_script, run
from fetch_footage import scene_clip_path

ASPECTS = {
    "9x16": (1080, 1920),
    "16x9": (1920, 1080),
}
FPS = 30
SUBTITLE_STYLE = (
    "Fontsize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
    "BorderStyle=3,Outline=2,Shadow=0,Alignment=2,MarginV=140"
)


def normalize_scene_clip(src: Path, duration: float, width: int, height: int, out_path: Path):
    vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={FPS},setsar=1"
    run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{max(duration, 0.1):.2f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        str(out_path),
    ])


def concat_clips(clip_paths: list[Path], list_file: Path, out_path: Path):
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path)])


def mux_audio_and_subtitles(video_path: Path, audio_path: Path, subtitles_path: Path, out_path: Path):
    subs_arg = str(subtitles_path.resolve()).replace("\\", "/").replace(":", r"\:")
    run([
        "ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path),
        "-vf", f"subtitles='{subs_arg}':force_style='{SUBTITLE_STYLE}'",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        str(out_path),
    ])


def assemble(slug: str):
    data = load_script(slug)
    if "start" not in data["scenes"][0]:
        raise SystemExit("No scene timing found — run generate_voiceover.py first.")

    audio_path = project_dir(slug) / "voiceover.mp3"
    subtitles_path = project_dir(slug) / "subtitles.srt"
    if not audio_path.exists():
        raise SystemExit(f"Missing {audio_path} — run generate_voiceover.py first.")
    if not subtitles_path.exists():
        raise SystemExit(f"Missing {subtitles_path} — run generate_subtitles.py first.")

    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for aspect_name, (width, height) in ASPECTS.items():
            print(f"Assembling {aspect_name} ({width}x{height})...")
            clip_paths = []
            for scene in data["scenes"]:
                src = scene_clip_path(slug, scene["id"])
                if not src.exists():
                    raise SystemExit(f"Missing footage for scene {scene['id']} — run fetch_footage.py first.")
                dest = tmp / f"{aspect_name}_scene_{scene['id']:02d}.mp4"
                normalize_scene_clip(src, scene["duration"], width, height, dest)
                clip_paths.append(dest)

            concat_out = tmp / f"{aspect_name}_concat.mp4"
            concat_clips(clip_paths, tmp / f"{aspect_name}_list.txt", concat_out)

            final_out = out_dir / f"{slug}_{aspect_name}.mp4"
            mux_audio_and_subtitles(concat_out, audio_path, subtitles_path, final_out)
            print(f"  -> {final_out}")

    print(f"\nDone. Finished videos in {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Assemble the final 9:16 and 16:9 videos for a project.")
    parser.add_argument("slug", help="Project slug")
    args = parser.parse_args()
    assemble(args.slug)


if __name__ == "__main__":
    main()
