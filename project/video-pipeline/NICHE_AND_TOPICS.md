# Niche & First 10 Topics

## Niche: off-grid solar & small-scale irrigation engineering

Not "renewable energy" in general (oversaturated, low intent) — specifically
**how off-grid solar-powered water systems work and how to build them**,
aimed at homesteaders, smallholder farmers, and DIY/engineering-curious
viewers. This is deliberately the exact audience for your solar irrigation
guide: every video's CTA drives to the same product, so distribution and
monetisation are the same funnel, not two separate projects.

Monetisation beyond platform payouts:
- Bio link → solar irrigation guide (primary — this is the point of the channel)
- Later: affiliate links for solar panel kits / pumps / controllers (Amazon
  Associates UK or manufacturer affiliate programs) once you have traffic
- Platform ad revenue (TikTok Creator Rewards, YouTube Shorts/long-form)
  is a bonus, not the plan — thresholds take months either way

## First 10 video topics

1. How solar irrigation pumps actually work
2. Why most off-grid solar setups fail in the first year
3. Solar panel vs battery: what actually limits your pump's runtime
4. The £40 part that makes or breaks a DIY irrigation system
5. How much water can one solar panel actually pump per day?
6. Grid power vs solar for irrigation: the real break-even point
7. The biggest mistake first-time solar irrigation builders make
8. How a solar water pump survives a UK winter (or doesn't)
9. Submersible vs surface pump: which one for a small solar setup
10. What a £300 off-grid irrigation system can actually do

## Daily session prompt (paste into Claude Code for a better script than the offline template)

```
Write a video script for topic: "<TOPIC>"
Niche: off-grid solar & small-scale irrigation engineering.
Audience: homesteaders/smallholder farmers + DIY/engineering-curious viewers.
CTA: drive to my solar irrigation build guide, link in bio.

Output valid JSON matching this schema exactly:
{
  "topic": str,
  "niche": str,
  "voiceover_script": str,          # full spoken text, 120-160 words, punchy, no fluff
  "scenes": [
    {"id": int, "beat": str, "text": str, "search_terms": [str, str, str]}
  ],                                  # 6-8 scenes: hook, problem, mechanism x2-3, payoff, cta
  "title_youtube": str,
  "title_tiktok": str,
  "description": str,
  "hashtags": [str]
}
search_terms must be things that exist as real stock footage on Pexels
(concrete visual nouns: "solar panel installation", "water pump irrigation",
not abstract phrases). Save the result to
video-pipeline/projects/<slug>/script.json, then I'll run the rest of the
pipeline myself.
```
