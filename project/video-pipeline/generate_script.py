#!/usr/bin/env python3
"""
Stage 1: topic in -> script.json out.

    python3 generate_script.py "How solar irrigation pumps actually work"

Produces projects/<slug>/script.json containing the voiceover script, a
scene-by-scene breakdown, and Pexels search terms per scene.

This is a deterministic offline generator (no API key, no network) so the
pipeline always works end-to-end. For higher-quality scripts, paste the
topic into a Claude Code session using the prompt template in
NICHE_AND_TOPICS.md ("daily session prompt"), have it fill out the same
script.json schema, and drop the result into projects/<slug>/script.json
before running the rest of the pipeline.
"""
import argparse
import json
import re
import sys

from common import save_script, slugify

NICHE_VISUAL_BANK = [
    "solar panel close up", "off grid solar farm", "water pump irrigation",
    "farmer field irrigation", "engineer working outdoors", "sunrise over farmland",
    "rural water tank", "solar panel installation", "drip irrigation system",
    "renewable energy technician", "african farm sunrise", "DIY workshop tools",
]

BEAT_TEMPLATES = [
    ("hook", "Here's something most people get wrong about {topic}."),
    ("problem", "The usual approach to {topic_lower} is expensive, fragile, or both — and that's the real barrier for most small-scale users."),
    ("mechanism_1", "Here's how it actually works, step one: the core system that makes {topic_lower} possible."),
    ("mechanism_2", "Step two — the part that keeps it running reliably, day after day, without constant attention."),
    ("mechanism_3", "Step three — the detail almost every guide skips, and the reason most first attempts fail."),
    ("payoff", "Get this right and {topic_lower} pays for itself in months, not years."),
    ("cta", "I've put the full build guide together, link in bio — everything you need to build this yourself."),
]


def keywords_from_topic(topic: str) -> list[str]:
    words = re.findall(r"[a-zA-Z]{4,}", topic.lower())
    stop = {"how", "what", "why", "does", "this", "that", "with", "your", "actually", "really", "into"}
    return [w for w in dict.fromkeys(words) if w not in stop]


def build_scenes(topic: str) -> list[dict]:
    kws = keywords_from_topic(topic)
    scenes = []
    for i, (beat, template) in enumerate(BEAT_TEMPLATES, start=1):
        text = template.format(topic=topic, topic_lower=topic[0].lower() + topic[1:])
        primary_kw = kws[i % len(kws)] if kws else "engineering"
        search_terms = [
            f"{primary_kw} {NICHE_VISUAL_BANK[i % len(NICHE_VISUAL_BANK)]}",
            NICHE_VISUAL_BANK[i % len(NICHE_VISUAL_BANK)],
            NICHE_VISUAL_BANK[(i + 3) % len(NICHE_VISUAL_BANK)],
        ]
        scenes.append({
            "id": i,
            "beat": beat,
            "text": text,
            "search_terms": search_terms,
        })
    return scenes


def generate(topic: str) -> dict:
    scenes = build_scenes(topic)
    voiceover_script = " ".join(s["text"] for s in scenes)
    return {
        "topic": topic,
        "niche": "off-grid solar & DIY sustainable engineering",
        "voiceover_script": voiceover_script,
        "scenes": scenes,
        "title_youtube": f"{topic} (Full Breakdown)",
        "title_tiktok": topic if len(topic) <= 100 else topic[:97] + "...",
        "description": (
            f"{topic} — full explainer. Build guide for a real off-grid solar "
            f"irrigation system linked in bio. #solar #engineering #offgrid"
        ),
        "hashtags": ["#solar", "#engineering", "#offgrid", "#sustainability", "#diy"],
    }


def main():
    parser = argparse.ArgumentParser(description="Generate a video script from a topic.")
    parser.add_argument("topic", help="Video topic, e.g. 'How solar irrigation pumps actually work'")
    args = parser.parse_args()

    slug = slugify(args.topic)
    data = generate(args.topic)
    path = save_script(slug, data)
    print(f"Wrote script for '{args.topic}' -> {path}")
    print(f"Slug: {slug}")
    print(json.dumps(data, indent=2)[:500] + "...")
    return slug


if __name__ == "__main__":
    main()
