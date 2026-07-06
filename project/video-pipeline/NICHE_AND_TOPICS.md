# Niche & First 10 Topics

## Niche: solar-powered, Raspberry Pi-controlled smart gardens

Specifically **how an off-grid solar + Raspberry Pi system waters a garden
automatically**, aimed at allotment growers, homesteaders, and Raspberry
Pi/DIY-electronics hobbyists. This is deliberately the exact audience for
the Solar Smart Garden build plans (`../solar-smart-garden/`) — every
video's CTA drives to the same product, and the product's own
award-winning backstory (IChemE Young Engineers Award) gives the channel a
genuine hook that isn't available to generic "off-grid solar" content.

Monetisation beyond platform payouts:
- Bio link → Solar Smart Garden build plans (Etsy + Gumroad) — primary
- Later: affiliate links for Raspberry Pi kits / soil sensors / solar
  panels (Amazon Associates UK) once you have traffic
- Platform ad revenue (TikTok Creator Rewards, YouTube Shorts/long-form)
  is a bonus, not the plan — thresholds take months either way

## First 10 video topics

1. How this Raspberry Pi decides which garden bed to water
2. Why a timer waters your garden wrong (and this doesn't)
3. Sizing a solar panel and battery for an off-grid garden — the actual maths
4. What happens when a soil sensor fails (real troubleshooting)
5. The £10 fitting that lets your garden feed itself too (fertigation)
6. Free recycled-bottle micro-greenhouses — the £0 upgrade
7. What actually breaks first in an off-grid garden system
8. Does this survive a Scottish winter? Season-by-season care
9. One Pi, five beds, one pump at a time — why not water everything at once
10. What £300 of solar and a Raspberry Pi can actually run

## Daily session prompt (paste into Claude Code for a better script than the offline template)

```
Write a video script for topic: "<TOPIC>"
Niche: solar-powered, Raspberry Pi-controlled smart gardens.
Audience: allotment growers/homesteaders + Raspberry Pi/DIY-electronics hobbyists.
CTA: drive to my Solar Smart Garden build plans, link in bio.
Real product context (use real details, don't invent numbers): a
Raspberry Pi Zero 2 W reads capacitive soil moisture sensors through
ADS1115 ADC boards and switches a 12V pump + up to 5 solenoid valves,
powered entirely by a 50W solar panel and a 12V battery via a PWM charge
controller. It won the IChemE Young Engineers Award for Innovation and
Sustainability. Full technical detail is in
../solar-smart-garden/product-source/SolarSmartGardenBuildGuide.docx if
you need to check a fact before scripting it.

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
search_terms must be things that exist as real stock footage on Pexels or
Pixabay (concrete visual nouns: "raspberry pi close up", "vegetable garden
raised beds", "solar panel installation", not abstract phrases). Save the
result to video-pipeline/projects/<slug>/script.json, then I'll run the
rest of the pipeline myself.
```
