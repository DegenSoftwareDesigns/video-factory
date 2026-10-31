# Suno skill evaluation for `video-factory`

Review date: 2026-10-17

Scope: actual capabilities, overlap, maintenance, licensing, dependencies,
credentials, network access, telemetry, and fit with the existing video workflow.
No candidate skill was installed or executed during this review. Findings and
repository statistics below describe the sources as reviewed on that date.

## Executive assessment

| Skill | Actual contribution | Risk / friction | Recommendation for this project |
|---|---|---|---|
| `suno-songwriter` by `regiellis` | Suno v6 briefs, lyrics, instrumentals, screen music, duration planning, variations, iteration, and controls | Low technical risk; does not generate audio itself; latest public release predates v6 | **Pilot as the main composition skill**, pinning the reviewed commit rather than the older release |
| `suno-music-engine` | Detailed musical direction, song analysis, dramatic arcs, instrumentals, albums, and explicit music/video synchronization methodology | Broad scope overlaps with `music-to-video` and other HyperFrames skills; 0 stars, no releases, ongoing changes | **Use selected references**, possibly informing a small local scoring skill later; avoid installing the whole skill initially |
| `qiaomu-suno-master` | Automated generation, downloads, LRC/SRT/MP3/MP4 export, manifests, and genre selection | Private web API, cookies/JWT, CAPTCHA, privileged CDP, Bash/macOS assumptions, outdated v5.5 defaults, poor fit for Windows; official API available and terms restrict robots/scraping/unapproved downloads | **Reject this route**; evaluate the official Suno Platform for future automation |

Start with `suno-songwriter` for direction and prompts. Retain `media-use` for
simple or inexpensive music, `music-to-video` for analysing the accepted recording
and synchronizing visuals, and `hyperframes-audio` for mixing, ducking, EQ, and
limiting. `suno-music-engine` has useful ideas for translating a video's dramatic
arc into a score, but its full installation would duplicate existing workflows.

## The gap to address

The workshop already separates three responsibilities:

1. `media-use` sources or generates background music. Its generation route uses
   Lyria or MusicGen. MusicGen creates one segment of roughly 28-30 seconds and
   extends it with crossfades; automatic prompt inference starts from a few
   business categories and generic arcs. This supports a quick music bed but
   provides limited direction for a bespoke narrative composition. Installed
   reference: `.claude/skills/media-use/audio/references/bgm.md`.
2. `music-to-video` starts with selected audio, creates `audiomap.json`, and makes
   shots follow phrases, energy, beats, and silence. It does not compose music.
   Installed reference: `.claude/skills/music-to-video/SKILL.md`.
3. `hyperframes-audio` mixes placed tracks through volume, automation, voice carve,
   EQ, compression, limiting, and effects. Sourcing and generation are explicitly
   outside its scope. Installed reference:
   `.claude/skills/hyperframes-audio/SKILL.md`.

The missing step comes before these: translate intent, planned editing, and the
emotional arc into a reproducible musical brief, generate comparable takes, and
select one. Suno skills should own that step. Installed references are available
after setup; external skill copies are intentionally excluded from this repository.

## Identifying `suno-songwriter`: two different repositories

At least two public skills use `name: suno-songwriter`:

- [`regiellis/suno-songwriter-agent-skill`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/SKILL.md), covering vocals, instrumentals, screen music, genres, albums, samples, controls, and iteration in v6.
- [`Fyzel/claude-skills/skills/suno-songwriter`](https://github.com/Fyzel/claude-skills/blob/8cb5eb2de2805f64fdb1588650d04bdae63f7cc0/skills/suno-songwriter/SKILL.md), a much shorter skill focused on three copyable blocks and still targeting v5.5.

The supplied description, "prompts, instrumentals, songs, and variations", fits
`regiellis` more closely; that is the main candidate evaluated here. If the intended
link was Fyzel's repository, the recommendation becomes **do not install**: it
targets v5.5, offers limited instrumental guidance, and Suno has migrated generation
to v6. The reviewed Suno documentation and v6 skill references describe the older
models' retirement: [Current Models: v6](https://help.suno.com/en/articles/13924737),
[`suno-v6-controls.md`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/references/suno-v6-controls.md).

## 1. `suno-songwriter` (`regiellis`)

### Actual capabilities

This is a knowledge and text-generation skill. It returns packages to paste into
Suno rather than generating audio. Its output contract separates vocal songs
(`Title`, `Style`, `Excluded Styles`, `Lyrics`) from instrumentals (`Title`,
`Instrumental Prompt`, `Arrangement`). It also covers song matrices, harmony,
rhythm, instrumentation, genres, fusion, screen music, Studio iteration, personas,
and albums. It explicitly requires claims about generating, listening to, uploading,
or saving audio to reflect what actually happened. Sources:
[`SKILL.md`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/SKILL.md),
[`instrumental.md`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/references/instrumental.md).

Especially relevant references:

- `screen-music.md` distinguishes songs, trailer cues, idents, stings, and game
  music; suggests forms for 3-15 s, 30-60 s, 90 s, and longer pieces; and notes that
  neither `[End]` nor a duration setting guarantees an exact cut.
  [`screen-music.md`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/references/screen-music.md)
- `song-matrix.md` and the harmony, rhythm, and structure references help budget
  sections and contrasts before spending credits. The index is in the
  [`README`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/README.md).
- `studio-and-iteration.md` covers take comparison and the decision between
  regeneration and editing, which the current workshop has not formalized.
  [Reference directory](https://github.com/regiellis/suno-songwriter-agent-skill/tree/cc3053bd027f822476734f41edbf9ae98078f61a/references).

### Repository status

As of 2026-10-17, the repository has an MIT licence, 11 stars, 0 forks, and 0 open
issues. Its latest push was 2026-10-11. The latest release, `v1.2.1` from 2026-07-31,
predates Suno v6, whereas `main` includes the September/October v6 revision. Pin
`cc3053bd027f822476734f41edbf9ae98078f61a` if adopted, or wait for a v6 release:
the "latest release" button may deliver the v5.5 version. Primary sources:
[API metadata](https://api.github.com/repos/regiellis/suno-songwriter-agent-skill),
[release v1.2.1](https://github.com/regiellis/suno-songwriter-agent-skill/releases/tag/v1.2.1),
[reviewed commit](https://github.com/regiellis/suno-songwriter-agent-skill/commit/cc3053bd027f822476734f41edbf9ae98078f61a).

### Dependencies and risks

- Writing prompts requires no API, login, or credentials.
- There is no music execution code. The only script is a ZIP packager using the
  Python standard library.
  [`scripts/package_skill.py`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/scripts/package_skill.py)
- Static review found no telemetry or data transmission in that script. This is
  a review finding rather than an absolute guarantee.
- Requested persona/album specifications can be saved as Markdown; direct them
  to the correct production folder rather than applying them as global configuration.
  [`SKILL.md`, Saved Projects](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/SKILL.md#saved-projects-and-portability)
- Documentation is divided into focused references and includes evaluations/manual
  smoke tests, but no automated listening tests: those checks validate text rather
  than musical quality.
  [`references/evals.md`](https://github.com/regiellis/suno-songwriter-agent-skill/blob/cc3053bd027f822476734f41edbf9ae98078f61a/references/evals.md)

### Fit

This provides the clearest module boundary: deliver a musical brief/package, then
let a separate tool generate the recording. Its scope does not extend into editing
or mixing. Restrict invocation to composing or improving Suno material so it fits
alongside `music-to-video` and `hyperframes-audio`.

## 2. `suno-music-engine`

### Actual capabilities

This is also primarily a prompting methodology, with much broader scope. It covers
mapping existing songs, vocal songs, instrumentals, albums, genre fusion, translating
personal context, v6 editing, multimodal inputs, music videos, and YouTube publishing
copy. Sources:
[`README.md`](https://github.com/Holodeck23/suno-music-engine/blob/1db25bda81334d07da9dc64f0fcdbd5c00e8c616/README.md),
[`SKILL.md`](https://github.com/Holodeck23/suno-music-engine/blob/1db25bda81334d07da9dc64f0fcdbd5c00e8c616/dist/codex/suno-music-engine/SKILL.md).

Its distinctive strengths for `video-factory` are:

- Defining an emotional journey beyond a single mood, separating form, phrase,
  beat, and texture.
- Assigning different visual roles to drums, bass, and melody; accounting for
  tempo drift, stem bleed, and separation noise; and saving deterministic offline
  curves.
  [`instrumental-video-production.md`](https://github.com/Holodeck23/suno-music-engine/blob/1db25bda81334d07da9dc64f0fcdbd5c00e8c616/references/instrumental-video-production.md)
- Helpers to extract embedded captions, align words, detect literal overlap with
  a reference, and measure visual appearance. The inventory explicitly states
  that it includes neither a general stem analyser nor a universal renderer.
  [`docs/video-capabilities.md`](https://github.com/Holodeck23/suno-music-engine/blob/1db25bda81334d07da9dc64f0fcdbd5c00e8c616/docs/video-capabilities.md)

### Repository status

As of 2026-10-17, it has an MIT licence, 0 stars, 0 forks, 2 open issues, no releases,
and activity on the review date. It was created in April 2026; recent history shows
several methodology changes within hours. This indicates activity, but also a
volatile surface with little evidence of external adoption. Sources:
[API metadata](https://api.github.com/repos/Holodeck23/suno-music-engine),
[commits](https://github.com/Holodeck23/suno-music-engine/commits/1db25bda81334d07da9dc64f0fcdbd5c00e8c616/).

The workshop's evaluation recipe rejects or avoids installing repositories with
very few stars, no licence, or no maintenance. This candidate has a licence and
activity, but its maturity signal does not support adopting its entire scope as
an operational dependency. Local policy:
[`GUIDE.md`, Evaluating a new skill](../GUIDE.md#evaluating-a-new-skill).

### Dependencies and risks

- `check-lift.py` uses only the Python standard library.
- `extract-video-timing.py` and `measure-frame-look.py` run FFmpeg/FFprobe locally.
- `align-lyric-words.py` imports `mlx-whisper` and may download weights on first use.
  Its documentation limits it to compatible Apple hardware and suggests Whisper.cpp
  as an alternative. It would not work unchanged on this Windows machine.
  [`align-lyric-words.py`](https://github.com/Holodeck23/suno-music-engine/blob/1db25bda81334d07da9dc64f0fcdbd5c00e8c616/scripts/align-lyric-words.py)
- Static review found no HTTP calls, `curl | sh`, `eval`, credential reads, or
  telemetry in its four helpers. The recommended Polyskill installer is a separate
  dependency and was not audited in this report.
  [`polyskill.yaml`](https://github.com/Holodeck23/suno-music-engine/blob/1db25bda81334d07da9dc64f0fcdbd5c00e8c616/polyskill.yaml)

### Fit and overlap

Instrumental composition and cue mapping are particularly relevant. However, its
description also triggers for music-video creation, synchronization, Blender/browser
rendering, visual quality, and YouTube publishing. Those responsibilities already
belong to `music-to-video`, `hyperframes-creative`, `hyperframes-cli`, and the
workshop's production workflow. Installing it wholesale would make routing
ambiguous and could bypass the order and gates in [`GUIDE.md`](../GUIDE.md).

Use selected MIT-licensed references to inform a future, narrowly scoped local skill:

1. `music-theory-engine.md`
2. `instrumental-video-production.md`
3. The instrumental composition section of `SKILL.md`

A future skill such as `video-score-brief` should finish after delivering a cue
sheet and prompts. Rendering, editing, and publishing remain separate workflows.

## 3. `qiaomu-suno-master`

### Actual capabilities

This is the only candidate attempting the full execution cycle: writing lyrics/tags,
using a local database of 5,947 genres, generating through a Rust CLI, downloading
MP3/video, exporting LRC/SRT/Markdown, validating synchronized lyrics, and recording
a manifest. Sources:
[`README.md`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/README.md),
[`SKILL.md`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/SKILL.md),
[`_meta.json`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/references/genre-finder/_meta.json).

Its automation does not use the current official API. `paperfoot/suno-cli` states
in its README that Suno has no official API and therefore calls the web API,
extracts the browser's Clerk cookie, exchanges it for a JWT, and stores a refreshable
session in a local file with mode `0600`. That premise is outdated: [Suno Platform](https://platform.suno.com/)
now advertises a REST API for generating songs, covers, and mashups.
[`paperfoot/suno-cli README`](https://github.com/paperfoot/suno-cli/blob/6d28c67a733b32183a80d81306bf0013f46b00b7/README.md#authentication)

This changes the risk comparison. Future automation should first evaluate the
official platform with its own credentials and terms, ahead of the private web
API, cookie extraction, CAPTCHA handling, or CDP.

### Significant compatibility drift

`qiaomu-suno-master` still pins `model: v5.5` in its skill, browser workflow, manifest,
and wrapper. Its latest documented verified path used `suno 0.5.7` on 2026-05-25.
[`SKILL.md`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/SKILL.md#inputs-to-resolve),
[`generate_with_suno.sh`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/generate_with_suno.sh).

The reviewed upstream CLI is `0.10.1`, targeting v6. Its documentation records a
breaking contract change in `0.6.0`, and models before v6 no longer generate.
[`paperfoot/suno-cli v0.10.1`](https://github.com/paperfoot/suno-cli/releases/tag/v0.10.1),
[`Cargo.toml`](https://github.com/paperfoot/suno-cli/blob/6d28c67a733b32183a80d81306bf0013f46b00b7/Cargo.toml),
[Suno Current Models](https://help.suno.com/en/articles/13924737).

Qiaomu's bootstrap installs the latest version through `cargo install suno --locked`
or Homebrew, then sends defaults and expects behaviour from 0.5.x. `--locked` pins
the downloaded version's dependencies, not the `suno` version. There is no `0.5.7`
pin or demonstrated adaptation to `0.10.1`.
[`ensure_suno_cli.sh`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/ensure_suno_cli.sh)

### Workstation compatibility

Although the upstream Rust CLI offers Windows binaries, Qiaomu's orchestration
mainly assumes Bash/macOS:

- `.sh` wrappers and Python calls to `bash`;
- Homebrew/Cargo installation paths;
- a Chrome launcher using `open -a`, `pgrep`, `~/Library/Application Support`, and
  TCC/LaunchAgent-specific notes;
- clipboard/download checks and examples using `sips`.

The CDP helper contains some Windows paths, but that does not make the whole
workflow native to PowerShell. Sources:
[`launch_suno_cdp_chrome.sh`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/launch_suno_cdp_chrome.sh),
[`cdp.mjs`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/cdp.mjs),
[`run_workflow.py`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/run_workflow.py).

### Security, credentials, and network access

Observed risks:

- Automatically installs an unpinned third-party binary and permits updates.
  [`ensure_suno_cli.sh`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/ensure_suno_cli.sh),
  [`upstream-suno-cli.md`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/references/upstream-suno-cli.md)
- Reuses browser cookies/sessions and enables Chrome remote debugging. CDP can
  inspect/control any exposed tab; the helper provides `Runtime.evaluate` and
  arbitrary CDP commands.
  [`chrome-cdp-auth.md`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/references/chrome-cdp-auth.md),
  [`cdp.mjs`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/cdp.mjs)
- Injects JavaScript into a tab to download from `cdn1.suno.ai`; if no Suno tab is
  found, it may select the first debuggable tab.
  [`browser_download_clips.py`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/browser_download_clips.py)
- Passes an optional hCaptcha token as a `--token` argument, potentially exposing
  it in the process list. The manifest avoids storing it and recommends an
  environment variable, reducing but not eliminating the wrapper's exposure.
  [`generate_with_suno.sh`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/generate_with_suno.sh),
  [`run_workflow.py`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/scripts/run_workflow.py)
- The upstream CLI states that its update channel checks SHA256 against GitHub
  Releases without independent signatures or attestation.
  [`paperfoot/suno-cli README`, Known limitations](https://github.com/paperfoot/suno-cli/blob/6d28c67a733b32183a80d81306bf0013f46b00b7/README.md#known-limitations)

Static review found no explicit telemetry/analytics endpoints in Qiaomu's scripts
or an evident telemetry dependency in `paperfoot/suno-cli/Cargo.toml`. Necessary
traffic does go to GitHub, Suno, Clerk, and Suno's CDN. This finding is based on
the pinned source commits, not a network capture.

There is also a compliance concern. The reviewed [Suno Terms](https://suno.com/terms/)
restrict robots, scraping, similar methods, and obtaining content through means
not intentionally made available. Commercial use requires an approved download
channel; obtaining a copy through another channel is prohibited. Qiaomu automates
the UI with CDP/robots, handles CAPTCHA, and can download directly from a CDN or
private web endpoints. This report does not determine that every individual call
is a legal violation, but the workflow falls into risk categories the terms name,
which supports rejecting it for a workshop that publishes videos.

### Repository status and licensing

As of 2026-10-17, Qiaomu has an MIT licence, 71 stars, 12 forks, and 0 open issues.
Its latest push was 2026-06-07, with no releases. Its manifest describes it as
`maturity_tier: scaffold` and `lifecycle_stage: personal`. Sources:
[API metadata](https://api.github.com/repos/joeseesun/qiaomu-suno-master),
[`manifest.json`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/manifest.json),
[LICENSE](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/LICENSE).

The genre database identifies Rate Your Music as its source but includes no
dataset-specific licence in `_meta.json`. The code's MIT licence does not itself
establish redistribution rights for data from another website. This does not
prevent reading tags locally, but the provenance uncertainty should be resolved
before copying that database into this repository.
[`_meta.json`](https://github.com/joeseesun/qiaomu-suno-master/blob/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5/references/genre-finder/_meta.json)

## Coverage and overlap

| Workshop need | `suno-songwriter` | `suno-music-engine` | `qiaomu-suno-master` | Existing coverage |
|---|---|---|---|---|
| Instrumental music brief | Very good | Excellent | Basic/moderate | Partial in `media-use` |
| Narrative arc and dramatic development | Good | Excellent | Basic | Partial in storyboard |
| Lyrics and vocal songs | Excellent | Very good | Good | No specialist skill |
| Trailer, ident, or short-form music | Very good | Very good | Generic | `media-use` sources/generates BGM |
| Variations and take comparison | Very good methodology | Good | Generates two clips through a fragile workflow | Not formalized |
| Automatic audio generation/download | No | No | Yes | `media-use` with other providers |
| Timing, beat, and stem-driven animation | Handoff only | Extensive | LRC/SRT | Strong in `music-to-video` |
| Mixing, ducking, EQ, limiting | No | No | No | `hyperframes-audio` |
| Native Windows fit | Yes, text-based | Partial; one helper is Apple-only | Poor | Workshop runs on Windows |
| Credential risk | None | None | High | Existing auth model in `media-use` |

Installing all three offers little benefit. `suno-songwriter` and
`suno-music-engine` trigger on similar requests and overlap in composition,
prompts, instrumentals, lyrics, genres, albums, and v6 controls. Qiaomu duplicates
lyrics/tags again while adding an execution layer that is outdated and poorly
suited to this workstation.

## Recommended workflow

```text
narrative storyboard / video brief
        ↓
suno-songwriter
cue sheet + 2-3 musical directions + Suno v6 prompts + exclusions
        ↓
user-authorized Suno generation
website or official API, 2 takes per direction,
recording prompts, model, controls, and plan
        ↓
human selection of one take
accepted recording in videos/<date_name>/04_audio/
        ↓
music-to-video
audiomap, phrases, energy, beats, silence
        ↓
HyperFrames editing
        ↓
hyperframes-audio
mixing, carve/ducking, EQ, fades, limiting
```

Retain `media-use` for a generic bed or a piece whose narrative does not depend
on music: HeyGen catalogue, Lyria, or MusicGen. Reserve Suno for pieces whose
musical arc justifies the credits and take-selection work. The accepted recording
must precede final shot timings and editing; see [`GUIDE.md`](../GUIDE.md).

### Minimum record for each generation

Store these in `04_audio/` alongside the selected recording:

- `music-brief.md`: purpose, target duration, arc, approximate BPM, instrumentation,
  motif, change points, and exclusions.
- `suno-generation.json`: date, model, exact prompt, excluded styles, sliders,
  Variety/Max Mode if used, take IDs/URLs, and Suno plan.
- `selected-audio.sha256`: identity of the accepted recording.
- `selection-notes.md`: why it was selected and defects to address in mixing/editing.

This makes musical directions repeatable, distinguishes a prompt from a listening
result, and preserves information relevant to commercial-use rights.

## Rights for monetized videos

According to the official Suno help reviewed on the stated date, songs created
and downloaded under Pro/Premier receive commercial-use rights; free-plan songs
are for non-commercial use, and a later subscription does not ordinarily grant
retroactive rights. Suno also distinguishes commercial-use permission from
copyright protection. Its [Terms](https://suno.com/terms/) require an approved
download channel for commercial use. Sources:
[What rights do I have with a paid subscription?](https://help.suno.com/en/articles/9601665),
[If I subscribe, do I get rights for songs made before subscribing?](https://help.suno.com/en/articles/2425729),
[How do downloads work?](https://help.suno.com/en/articles/13876865).

Record the plan active at creation/download. For third-party material, remixes,
or uploaded audio, also record provenance and authorization.

## Proposed adoption plan

Status 2026-10-19: step 1 is complete. The `regiellis` repository was confirmed and
`suno-songwriter` is pinned in `skills.lock.json` at
`cc3053bd027f822476734f41edbf9ae98078f61a`; the step 2 pilot productions are pending.

1. **Do not install yet.** First confirm that the intended `suno-songwriter` is
   the `regiellis` repository.
2. **Pilot three videos** pinned to `cc3053bd027f822476734f41edbf9ae98078f61a`:
   one narrative piece, one 15-20 s promo, and one narrated explainer.
3. Measure generation count, credits, time to an accepted take, fit to the arc,
   ease of editing, interference with voice, and final rating in `videos.csv`.
4. If musical development remains the main weakness, create a narrow local
   `video-score-brief` skill informed by the instrumental references in
   `suno-music-engine`, pinned to `1db25bda81334d07da9dc64f0fcdbd5c00e8c616`.
5. Reconsider Qiaomu only after v6 support, declared Windows compatibility, a pinned
   and tested CLI version, and removal of automation that conflicts with the
   applicable terms. Evaluate [official Suno Platform](https://platform.suno.com/)
   first if automation is needed, then compare third-party wrappers if relevant.

## Reviewed source snapshot

| Repository | Reviewed commit | Licence | Popularity/activity as of 2026-10-17 |
|---|---|---|---|
| `Holodeck23/suno-music-engine` | [`1db25bd`](https://github.com/Holodeck23/suno-music-engine/commit/1db25bda81334d07da9dc64f0fcdbd5c00e8c616) | MIT | 0 stars, 0 forks, pushed 2026-10-17, no release |
| `regiellis/suno-songwriter-agent-skill` | [`cc3053b`](https://github.com/regiellis/suno-songwriter-agent-skill/commit/cc3053bd027f822476734f41edbf9ae98078f61a) | MIT | 11 stars, 0 forks, pushed 2026-10-11, release v1.2.1 predates v6 |
| `joeseesun/qiaomu-suno-master` | [`6e1c224`](https://github.com/joeseesun/qiaomu-suno-master/commit/6e1c2244e447b18cf24f05a29dc64f4cd8261bf5) | MIT | 71 stars, 12 forks, pushed 2026-06-07, no release |
| `Fyzel/claude-skills` (same-name alternative) | [`8cb5eb2`](https://github.com/Fyzel/claude-skills/commit/8cb5eb2de2805f64fdb1588650d04bdae63f7cc0) | Apache-2.0 | 1 star, pushed 2026-07-13; Suno v5.5 skill |
| `paperfoot/suno-cli` (Qiaomu dependency) | [`6d28c67`](https://github.com/paperfoot/suno-cli/commit/6d28c67a733b32183a80d81306bf0013f46b00b7) | MIT | 59 stars, 29 forks, release v0.10.1, pushed 2026-09-28 |

Star/fork counts are a snapshot and may change. Primary metadata is available
through each repository's GitHub API, linked in its section above.
