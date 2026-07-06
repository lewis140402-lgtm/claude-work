# Product: The Solar Smart Garden — Build Plans

Real product, not a placeholder — this is a complete, working build guide
for a solar-powered, Raspberry Pi-controlled self-watering vegetable garden,
based on the actual award-winning installation at the Strathclyde Community
Garden (Winner, IChemE Young Engineers Award for Innovation and
Sustainability, Food and Drink category).

Master source files live in `product-source/`:
- **`SolarSmartGardenBuildGuide.docx`** — the 14-section build guide:
  what you're building, how it works, safety, parts & tools, water
  storage/delivery, solar sizing, the Raspberry Pi control system, the full
  Python controller code (`garden.py`) and systemd service, fertigation
  upgrade, bottle micro-greenhouses, commissioning checklist, season-by-
  season care, troubleshooting, FAQ.
- **`SolarSmartGardenPartsList.xlsx`** — full UK parts list with prices and
  a tick-off column, plus a solar/battery sizing calculator and a watering
  calculator, both of which recalculate from a few editable inputs.
- **`LaunchKit.md`** — the complete go-to-market plan: Etsy + Gumroad
  listing copy (title, tags, description, pricing), photo/video shot list,
  first-30-days distribution plan, and a launch checklist. This is the
  source of truth for pricing/launch — `PRICING.md` and `LAUNCH_PLAN.md` in
  this folder mirror it so the rest of this project's structure stays
  consistent, but if the two ever disagree, `LaunchKit.md` wins.

## What's left before this is sellable (from the build guide's own "read me first" page)

The guide's structure and the software are complete and real — these are
the specific "yellow box" gaps only you can fill, since they're your actual
build:

1. A labelled photo/sketch of your own bed layout (tank position, pipe
   route, valve positions, dripper spacing) — Stage 1
2. Your wiring diagram + a labelled photo of your controller enclosure —
   Stages 2-3 (reuse your DesignSpark diagram if you have one)
3. Your production code, if it differs from the `garden.py` listed in the
   guide (e.g. a dashboard, cloud logging, per-bed fertigation control) —
   Stage 4
4. Your per-bed fertigation mass balance tables (crop, daily water volume,
   target nutrient concentration, resulting dose) — Stage 5. The guide
   calls this out as "the single biggest differentiator of the whole
   product," so it's worth your best material, not a quick fill-in
5. A photo of a bottle micro-greenhouse in place — Stage 6
6. Delete the "read me first" page, update the award year if needed, export
   to PDF

Once those are in, you have your two customer-facing files: the PDF guide
and the parts list spreadsheet — both well under Etsy's 20MB/file limit.

## Before publishing

Two courtesy checks flagged in the LaunchKit and worth doing exactly as
written there: agree with Reuben how you're handling this since the garden
was a joint project, and skim the RS Big Pitch / Alumni Fund terms for
anything about commercial spin-offs.
