# Lightweight examples

This directory contains lightweight references and can host one or two reproducible
sample productions. Everyday productions live in `videos/` and stay outside Git.

## Available examples

- [`ember-brand/`](ember-brand/README.md): a reusable fictional brand kit with
  brand/video guides, configuration, original SVG logos and mascot sheets, a small
  asset builder, and a local visual brand board. Start here before your first
  recurring-brand production.

## Adding an example

Each example should have its own directory containing:

- A README with its purpose, execution instructions, and expected result.
- Code, a storyboard, and assembly configuration with specific tool versions.
- The necessary branding and one or two small reference images.
- Source information and permission/licence details for included assets.

Repository budget: at most 5 MiB per file, preferably less than 1 MiB per image.
Export references to WebP/JPEG where appropriate. Download final MP4s, full audio
tracks, and raw footage separately, with instructions in the example. `renders/`,
`.media/`, `node_modules/`, and caches remain ignored here.

Run examples from `examples/<name>/`. If an example uses `scripts/videos.py`, that
script still writes to the local `videos/` workspace. To publish an example, copy
only its source files and minimum required assets into this directory.
