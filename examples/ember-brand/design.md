# EMBER brand identity

Status: fictional example. Replace this document's decisions when adapting the kit.
`brand.json` is the source for names, colours, fonts, and preview copy. The builder
and brand board read it directly; the guidance below explains how to use those values.

## Positioning and voice

EMBER is a playful community built around small contributions becoming shared
momentum. The audience is people discovering a character-led community on social
media. Personality: warm, curious, energetic, and welcoming.

Use short, concrete English copy. Invite participation through a specific action.
Keep the humour friendly and the character expressive. Example brand line:
"Small spark. Big energy." In a real campaign, use verified product/community
facts rather than inventing token metrics, partnerships, or financial promises.

## Visual direction

Warm paper backgrounds, deep green ink, coral-orange emphasis, heavy sans-serif
headlines, generous spacing, flat shapes, and rounded character forms. Colour
names and exact values live in `brand.json`; use `paper` and `ink` for readable
text/background pairs. `primary`, `sun`, and `mint` are illustration/shape accents.

Use `ink` text on light accents and `paper` text on `ink`. Keep small text off the
orange accent. Use one dominant accent per composition and let the character's
silhouette carry the identity. Avoid metallic rendering, photorealistic fire,
neon tunnels, or unrelated visual styles unless a campaign deliberately changes
the art direction and the owner approves that change.

## Typography and layout

- Display: the `display` stack, uppercase for short labels or sentence case for
  a large message; heavy weight, tight leading, at most two headline lines.
- Body: the `body` stack, regular weight, plain language, short paragraphs.
- Labels: the `label` monospace stack, short uppercase captions with light tracking.
- Spacing: an 8-unit base, using 8, 16, 24, 32, 48, and 64 units.
- Geometry: circles, soft rectangles, simple lines, and flat fills; use outlines
  sparingly. Shadows are not part of the base identity.

System fonts keep the example self-contained. If a real brand supplies fonts,
place permitted local font files in its brand folder and replace the font stacks.

## Logos

`assets/logo.svg` is the horizontal symbol/name lockup. `assets/mark.svg` is the
standalone flame symbol. Leave clear space of at least one quarter of the symbol's
height around either. Use the lockup when the name matters and the mark when space
is limited. Preserve proportions and approved colours.

The SVG wordmark contains live text using the configured display font. For a final
client identity, replace it with supplied official vector artwork or outlined type
to guarantee matching letterforms across machines.

## Pip: immutable character details

Pip is a flat, coral-orange spark with one tall tip leaning toward the viewer's
right in the front view, a smaller notch on the viewer's left, a warm yellow inner face, dark green
eyes, two small rounded feet, and one small yellow diamond on the front of its body.

Maintain these details across shots:

1. One primary tip and one side notch; their visible orientation changes with the
   viewpoint (the back silhouette mirrors the front). No extra spikes, ears, horns, or tail.
2. Short body and small feet; limbs stay simple and never become human anatomy.
3. Coral outer body, yellow face, dark eyes, and the front diamond.
4. The back view has no face or front diamond. A side view shows one eye.
5. The face remains recognizable while eyes and mouth change expression.

Expressions and limb poses can change. Costume, props, materials, proportions,
or extra characters require a deliberate campaign decision and matching updated
references. Reuse the approved sheets rather than relying on a text description.

## Asset ownership and approval

The vector kit is authored for this example; provenance is in `CREDITS.md`. For an
adapted brand, record each asset's source, owner, and approval date here or in a
small asset manifest. Keep original references separate from proposed variations.
Promote a variation into the reusable kit only after review.

## Adaptation checklist

- Replace brand identity and messaging in this document and `brand.json`.
- Replace logos and mascot artwork with the actual brand's approved assets.
- Check turnaround, expressions, poses, and written invariants against each other.
- Rebuild the assets and inspect the brand board.
- Complete `frame.md` before the first campaign, especially tone and music.
