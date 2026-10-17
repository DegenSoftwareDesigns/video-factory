# EMBER: video direction template

Read `design.md`, `brand.json`, and the approved mascot sheets before planning a
production. This file supplies reusable video defaults; the campaign brief supplies
its audience, message, delivery format, duration, footage, and call to action.

## Formats and safe areas

| Destination | Canvas | Starting safe area |
|---|---|---|
| Social feed | 1080 × 1440 (3:4) | 72 px left/right, 96 px top/bottom |
| Vertical short | 1080 × 1920 (9:16) | 72 px left/right, 160 px top, 280 px bottom |
| Landscape promo | 1920 × 1080 (16:9) | 96 px left/right, 72 px top/bottom |

These are layout starting points, not universal platform guarantees. Check the
actual destination's current overlays and crop behaviour for each campaign.

## Composition

- One clear message per shot, with the mascot or product as the visual anchor.
- Headline: 88-128 px on a 1080-wide canvas, at most two lines; verify real bounds.
- Supporting line: 36-44 px, usually one sentence. Labels: 24-28 px.
- Use the approved background plate or a flat `paper`/`ink` field.
- A three-segment chapter bar can mark narrative phases; keep it inside the safe area.
- Preserve Pip's full silhouette in reference views. Cropping is allowed in a
  deliberate close-up, provided key identity details remain understandable.

The static social card on the brand board demonstrates these rules. It is a layout
reference, not an animated composition or a completed campaign.

## Motion

Start from decisive 0.25-0.45 s entrances, short anticipation before a reveal, and
clean exits. Use transform and opacity. Let Pip's pose, the edit, and the soundtrack
provide energy; keep text readable and avoid constant movement in every layer.
Use holds and contrast in scale. An accent can stretch slightly on entrance, but
preserve the mascot's anatomy and silhouette. Review movement before adding detail.

## Musical identity

Preferred territory: warm electronic percussion, a clear bass pulse, playful
rhythmic details, and space for voice or character sounds. A starting tempo range
of 110-128 BPM can suit an energetic promo; measure the chosen recording rather
than assuming it follows the requested tempo.

Offer two or three directions per campaign, such as a light groove, a stronger
percussive build, or a minimal bed under narration. Select music before final shot
timings and animation. Map the actual phrases, changes of energy, drop, pauses,
and ending; save that map with the selected track in the production's `04_audio/`.

Avoid default orchestral drama for this identity. Do not interpret that preference
as a requirement to fill every moment with sound. A short silence before a reveal
can be useful. For narration-led pieces, lock the voice first and support it with
music. Finish with restrained SFX and a measured mix, then review the exported file.

## Generation handoff

For each image/clip, specify the intended composition and action, then attach the
relevant approved mascot view, expression, and pose. Describe permitted changes
and preserve the invariants in `design.md`. Keep new image/clip outputs inside the
production, and review them before treating them as a new brand reference.

## Campaign brief to fill in

```text
Brand folder:
Audience and destination:
Main message:
Duration and aspect ratio:
Music-led or narration-led:
Accepted audio and timing map:
Required approved assets:
Mascot view / expression / pose:
Call to action:
Campaign-specific exclusions:
```
