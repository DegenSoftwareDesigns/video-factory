---
name: video-factory
description: Common entry for any video work in the open project - AI cinematic shots, motion graphics, editing, music or cleanup of a finished video. Resolves where this project keeps its files and deliverables, reads past lessons, loads the right video-factory workshop skills, and keeps every output in the project's own folders. Use first whenever the user asks to plan, make, edit or finish a video, storyboard, trailer, promo, clip or animated graphic.
---

# Video Factory

The workshop's knowledge (methodology, skills, scripts, pinned tools) lives in the
workshop folder `WORKSHOP` = `${user_config.workshop}`. The work belongs to the **open
project**: every plan, reference, keyframe, clip, audio file, edit and deliverable goes
into the project's folders, never into the workshop. Match the user's language in conversation.

If `WORKSHOP` above still reads as a literal `${user_config...}` placeholder (or this
skill was opened from a project's `AGENTS.md`), use the `VIDEO_FACTORY_HOME` environment
variable, then `pluginConfigs` → `video-factory@video-factory` → `options.workshop` in
`~/.claude/settings.json`; otherwise ask the user for it.

## Start

1. Read `WORKSHOP/GUIDE.md` (workflow routing, overlaps, music-before-editing,
   finishing order, cleanup) and the Production section of `WORKSHOP/AGENTS.md`.
   Treat them as this skill's instructions; their notes about running from the workshop
   root are replaced by the commands below.
2. Run these from the open project folder, which they treat as the client project:
   - `"WORKSHOP/bin/vf"` = `videos.py` (`new`, `paths`, `check`, `update`, `learnings`, `clean`)
   - `"WORKSHOP/bin/vf-storyboard"` = the storyboard board builder (`init`, `build`)
   - `"WORKSHOP/bin/vf-melies"` = Melies technique lookup (`search`, `list`, `shot ... --prompt`)
   - `"WORKSHOP/bin/vf-hyperframes"` = the workshop's pinned HyperFrames CLI

   These are Bash scripts. In PowerShell or cmd use the same names with `.cmd`
   (`& "WORKSHOPinf.cmd" paths <name>`).
3. Find the project's destination contract: `video-factory.json` at the project root or one
   folder below it. Without one, propose a small manifest from the project's existing folders
   (format in `WORKSHOP/docs/client-projects.md`), confirm it with the user, and write it where
   the project keeps its records. The user's instructions on organization override it.
4. `vf learnings` (add `--tipo <type>` when known), and read the manifest's `context` documents.
5. Create or reopen the production: `vf new "<name>" --tipo <type> --formato <aspect> --intencion "..."`,
   then `vf paths <name>`. Write each output only to the role folder `paths` gives, with the
   deliverable names it declares. Reuse the manifest's `references` as generation inputs.

## Route to a track

Pick the track from `GUIDE.md`'s quick reference. Workshop skills are not registered in this
project: load one by reading `WORKSHOP/.claude/skills/<skill>/SKILL.md` and following it, with
its relative references resolved from that folder.

| Track | Use when | Skills |
|---|---|---|
| Cinematic AI | photoreal or illustrated shots generated with AI | `storyboard` (its `scripts/` are the `vf-storyboard` and `vf-melies` commands), `kling-ai`, Higgsfield tools, `suno-songwriter` or `media-use` for music, `music-to-video` for timing |
| Motion graphics | typography, charts, titles, logos, product promos built in code | `hyperframes` first, then `motion-graphics`, `explainer-*`, `general-video`, `hyperframes-registry`, `hyperframes-animation`, `sound-effects`, `hyperframes-audio`. HyperFrames projects go in the **assembly** role; run the CLI as `vf-hyperframes` |
| Editing | recorded footage, talking heads, shorts, captions | `video-use`, `clipify`, `embedded-captions`, `talking-head-recut`, `motion-broll`, `watch`, `media-use`, `hyperframes-audio` |

Within a track, its skill's phases and STOP gates apply. Folder names those skills mention
(`00_plan/`, `04_audio/`, `05_montaje/`, `final/`...) mean the corresponding role from `vf paths`.

## Rules

- Before any paid image, clip, music or voice generation, state quantity, model and estimated
  cost and wait for an explicit OK. Record approvals and costs in the project's `records`.
- Do not install dependencies, clone repositories or copy skills into the project; the workshop
  owns them. Write nothing in the workshop except through `vf` (its learning log and `.work/`).
- Run `vf check <name>` before reporting a stage complete.
- When the user approves the final video: `vf update <name> --estado terminado --nota N ...`
  prints the cleanup dry run. Show it; after the user's OK run `vf clean <name> --yes`, adding
  `--keep` for final-version clips outside the storyboard and `--drop` for older versions or
  heavy masters in the final folder. Only the production's own folders are touched.
