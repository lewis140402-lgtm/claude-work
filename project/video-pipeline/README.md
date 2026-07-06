# Faceless Video Pipeline

One command, one finished video. Topic in → script, stock footage, ElevenLabs
voiceover, burned-in subtitles, 9:16 + 16:9 exports out.

## Setup

```bash
cd video-pipeline
pip3 install -r requirements.txt
cp .env.example .env
# then edit .env and add PEXELS_API_KEY, PIXABAY_API_KEY, and ELEVENLABS_API_KEY
```

Get a free Pexels key at https://www.pexels.com/api/ (200 req/hr, 20k/month —
plenty for this volume). Get a free Pixabay key at https://pixabay.com/api/docs/
— it's used as a fallback whenever Pexels doesn't have a good clip for a
scene's search terms, so between the two you'll rarely hit a placeholder in
a real run. Get an ElevenLabs key at https://elevenlabs.io.

`ffmpeg` must be installed and on your `PATH` (`ffmpeg -version` to check).

## Run it

```bash
python3 make_video.py "How solar irrigation pumps actually work"
```

Output lands in `output/<slug>/<slug>_9x16.mp4` and `<slug>_16x9.mp4`.

### Dry run without API keys

```bash
PIPELINE_MOCK=1 python3 make_video.py "Test topic"
```

Generates placeholder labeled clips and silent audio sized to the estimated
speech duration, so you can confirm cutting/cropping/subtitle-sync mechanics
work before spending any API credits. This was used to verify the pipeline
end-to-end in development (see `output/` after a mock run: valid H.264/AAC
mp4s at the correct resolutions, subtitles burned in, audio synced to scene
timing).

## How it works (each stage can also be run standalone)

1. **`generate_script.py <topic>`** — deterministic offline template
   generator: produces `projects/<slug>/script.json` with a hook → problem →
   mechanism (x3) → payoff → CTA structure, Pexels search terms per scene.
   No API key needed. For a better script, paste the topic into a Claude Code
   session using the prompt in `NICHE_AND_TOPICS.md` and drop the result into
   `script.json` before continuing — this is the "one prompt in" daily
   workflow described in `../OPERATIONS.md`.
2. **`fetch_footage.py <slug>`** — downloads one clip per scene: tries each
   scene's search terms against Pexels first, then Pixabay, until one hits.
3. **`generate_voiceover.py <slug>`** — sends the full voiceover script to
   ElevenLabs, gets back the duration, and splits it across scenes
   proportional to word count. Writes scene `start`/`end`/`duration` back
   into `script.json`.
4. **`generate_subtitles.py <slug>`** — chunks each scene's text into ~6-word
   captions spread evenly across its time window → `subtitles.srt`.
5. **`assemble_video.py <slug>`** — loops/trims each clip to its scene
   duration, scales+crops to 1080x1920 and 1920x1080, concatenates, muxes
   the voiceover, burns subtitles with libass. Two final files per project.

## Known limitations (MVP, fix if they start costing you views)

- Subtitle timing is proportional to word count within a scene, not
  word-level forced alignment — good enough for short punchy captions but
  can drift by a few hundred ms on longer scenes. If it's noticeably off,
  swap in `whisper` (small model) to re-time from the actual audio.
- The script generator is a template, not a language model — its scripts
  are serviceable placeholders, not your best copy. Best-quality path is
  still writing/editing scripts through Claude Code (see `OPERATIONS.md`).
- No music track — add a `-i background.mp3` bed in `assemble_video.py`'s
  final mux step if you want one (keep it under -20dB under the voiceover
  and check the track's licence).
- Pexels and Pixabay can both come up empty if a scene's search terms are
  too generic or too specific; the final fallback is a placeholder clip, so
  a real run may still produce a video with 1-2 mismatched scenes worth a
  manual re-search.
