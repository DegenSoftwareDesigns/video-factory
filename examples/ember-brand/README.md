# EMBER: a reusable brand kit

A complete, fictional community/memecoin brand for learning the workshop's brand
setup. EMBER and its mascot Pip are demonstration assets; this kit describes no
live token. It is a brand reference template, with no generated footage or audio.

## Preview

From the workshop root:

```powershell
python -m http.server 8768 --bind 127.0.0.1 --directory examples/ember-brand
```

Open [the brand board](http://localhost:8768/). The board shows the identity, logo,
palette, mascot sheets, and a sample social frame. All fonts are system fonts;
there are no external requests, dependencies, or provider credits.

## Adapt this kit

Copy the example into your ignored brand workspace first:

```powershell
New-Item -ItemType Directory -Force brands | Out-Null
Copy-Item -Recurse examples/ember-brand brands/my-brand
```

Then adapt these files in order:

| File | What to replace |
|---|---|
| `brand.json` | Brand name, tagline, colours, type stacks, mascot name, and preview copy |
| `design.md` | Positioning, voice, visual rules, approved assets, and identity constraints |
| `source/mascot.svg` | The actual approved mascot artwork and its views/expressions/poses |
| `frame.md` | Video formats, safe areas, composition, motion, and musical direction |

Changing a name in the configuration does **not** create a new mascot. Replace the
artwork when adapting the kit, and update its written constraints to match. For a
realistic or detailed character, replace the schematic vector sheets with approved
production model sheets. Keep the same asset paths, or update `index.html` to match.

Rebuild the vector assets after editing configuration or artwork:

```powershell
python brands/my-brand/build_assets.py
python -m http.server 8768 --bind 127.0.0.1 --directory brands/my-brand
```

The builder uses only Python's standard library. It rewrites the known generated
files under `assets/`, preserving the source SVG, configuration, and documents.
Edit `source/mascot.svg` rather than the generated sheets. Update remaining EMBER/Pip
references in the Markdown documents before treating the copy as your own brand.

When redrawing the source, retain its symbol IDs (`mark`, `front`, `three-quarter`,
`side`, `back`, `happy`, `focused`, `surprised`, `wave`, `run`) or update the builder's
mappings. If using supplied official logos or finished raster sheets, replace the
preview's asset paths as needed and adapt/skip the corresponding builder outputs
so a rebuild does not overwrite those approved assets.

## Included reference sheets

- `assets/turnaround.svg`: front, three-quarter, side, and back views.
- `assets/expressions.svg`: neutral, happy, focused, and surprised.
- `assets/poses.svg`: standing, waving, and running.
- `assets/mascot.svg`: the primary transparent mascot artwork.
- `assets/logo.svg`, `assets/mark.svg`: a wordmark lockup and standalone symbol.
- `assets/background.svg`: a reusable background plate.

The sheets reuse the same source definitions, so repeating a character does not
require redrawing its proportions. The generator applies colours from `brand.json`
to every SVG. These are schematic consistency references, not a promise that an AI
model will reproduce every detail. Select references for each shot and review the
actual generated images before animating them.

## Start a production with this brand

After copying and adapting the kit, give the agent this brief:

> Use `brands/my-brand/design.md`, `frame.md`, and `brand.json` for this production.
> Inspect the approved logo and mascot sheets before planning images. Ask only
> about missing campaign decisions: audience, message, format, duration, and assets.
> For a music-led video, approve the recording and its timing map before animation
> or final editing. Keep production files in `videos/`, leaving reusable assets in
> the brand folder.

This example stays versioned in `examples/`. Adapted client/personal kits in
`brands/` and individual productions in `videos/` stay local. See
[`CREDITS.md`](CREDITS.md) for asset provenance.
