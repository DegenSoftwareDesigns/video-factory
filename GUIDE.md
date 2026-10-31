# Guide: choosing the right workflow

This guide routes each video task to the appropriate skill. It helps users decide
what to request and agents select a workflow when several skills overlap. For a
request not covered here, start with the `/hyperframes` router.

Teammate setup is documented in `README.md`. External skills are reconstructed
from `skills.lock.json`; updates follow `docs/skills.md`. Productions, their brand
workspaces, and `videos.csv` stay local. Shared samples belong in `examples/`
with minimal media.

## Quick reference

| Goal | Skill/tool | Example request |
|---|---|---|
| Plan a video with AI-generated shots from an idea | `storyboard` | "Make a video about..." |
| Download an online video | `descargar.ps1` (yt-dlp) | "Download this link as a reference" |
| Watch and understand a video | `watch` | "Watch this video and explain its subject" |
| Edit raw footage: cuts, filler words, silence, colour, captions | `video-use` | "Edit these takes into a two-minute video" |
| Extract vertical clips from a long video | `clipify` | "Make three shorts from this podcast" |
| Add captions to an already edited talking head | `embedded-captions` | "Add cinematic captions" |
| Add titles, lower thirds, quotes, and data to a talking head | `talking-head-recut` | "Add titles and data to this interview" |
| Add animated B-roll timed to speech | `motion-broll` | "Create animated B-roll for this video" |
| Explain a topic without recorded footage | `faceless-explainer` | "Turn this article into an explainer" |
| Make a short graphic: title, figure, chart, map, logo | `motion-graphics` (HyperFrames) | "Animate this figure: 3M users" |
| Make a high-energy product promo (12-20 s) | `explainer-high-energy` | "Make a launch teaser for my app" |
| Explain a product in one continuous shot (10-30 s) | `explainer-engaging` | "Explain the workflow using one travelling element" |
| Make a clean product demo (45-90 s) | `explainer-default` | "Demonstrate the product interface" |
| Create a promo or tour from a website | `product-launch-video` (*) | "Make a launch video from this URL" |
| Create a video driven by a song | `music-to-video` | "Make a lyric video for this track" |
| Make a longer or custom piece: reel, montage, multiple scenes | `general-video` | "Make a sizzle reel from these clips" |
| Make a navigable presentation rather than an MP4 | `slideshow` | "Turn this into a deck" |
| Add sound effects to motion graphics | `sound-effects` | "Add sound effects" |
| Mix audio in a HyperFrames composition: fades, ducking, EQ | `hyperframes-audio` | "Lower the music while I speak" |
| Source or generate music, SFX, voice, or images | `media-use` | "Find a calm music bed" |
| Write a bespoke music brief and Suno v6 prompts | `suno-songwriter` | "Write a Suno prompt for this promo's arc" |
| Separate a subject from the background | `object-separation` | "Cut the person out of the background" |
| Generate AI clips from text or images | Higgsfield MCP + `kling-ai` prompts + Melies technique | "Make a five-second night-city shot with a dolly zoom" |
| Evaluate a new skill or tool | "Evaluating a new skill" recipe | "Review this tool and tell me whether it is useful" |
| Review lessons from earlier videos | `scripts/videos.py learnings` | "What did we learn from our latest videos?" |
| Remove working files once a video is finished | `scripts/videos.py clean` | "The coffee video is done" |

(*) Not included in the pinned set. If `product-launch-video` or `pr-to-video`
is needed, add it to the lockfile from the reviewed HyperFrames commit and follow
`docs/skills.md`, so everyone uses the same version.

## Production destinations and learning log

The workflows below name **roles**, not fixed folders. `python scripts/videos.py
paths <id>` prints where each role lives for a production; every workflow and
specialist writes there.

- **Standalone (default):** every video lives in `videos/<YYYY-MM-DD>_<name>/`,
  regardless of workflow. Choose its name at the start. Existing folder names are
  retained for compatibility.
- **Client project:** `--project <folder|alias>` uses the client's
  `video-factory.json`: its folders, existing references, records and declared
  deliverables. Working files such as `storyboard.json` and the HTML board stay in
  the workshop's `.work/`. The user's organization instructions take precedence over
  the manifest, which takes precedence over the defaults. See `docs/client-projects.md`.

| Role | Standalone folder | Contents |
|---|---|---|
| plan | `00_plan/` | Storyboard and planning notes |
| references | `01_referencias/` | Character, product, or location references |
| keyframes | `02_keyframes/` | Keyframe images for each shot |
| clips | `03_clips/` | Generated or trimmed shot clips |
| audio | `04_audio/` | Music, voiceover, and effects |
| assembly | `05_montaje/` | Assembly project and intermediate renders |
| final | `final/` | Deliverables; always retained during cleanup |

When a client declares deliverables (for example 1-2 storyboard sheets, one FHD
image per clip and a single prompt TXT), they replace the default planning outputs
of a workflow: produce exactly those, named as declared, and run
`videos.py check <id>` before reporting a stage complete. Folder names below, such
as `04_audio/`, mean the corresponding role.

The root `videos.csv`, viewable in Excel, is the local learning log. Each row
records a video's name, type, intent, aspect ratio, duration, tools, status, rating
from 1 to 10, what worked, and what to improve. Fill it in with the user at the
end of a production and read it before the next one. When a video is finished,
clean it so no junk accumulates: `videos.py update <id> --estado terminado` prints
what will be removed and how much space it frees, and `videos.py clean <id> --yes`
runs it after the user's OK. Only the final video, declared deliverables, the
images and individual clips used in the final version (`--keep` for clips outside
the storyboard), and `storyboard.json` are kept. `final/` ends with the latest
light version per format; older versions and heavy masters are named with
`--drop`. Everything else is an intermediate and is removed: discarded or
replaced versions, drafts, audio, assembly projects and intermediate renders.
Client cleanup is limited to the production's
own folders.

## Rules for overlapping workflows

- **Captions.** Use `video-use` when raw footage also needs cutting,
  `embedded-captions` for an already edited talking head, or `clipify` for vertical
  extracts from a longer video. Use one captioning workflow per video.
- **Talking-head overlays.** Use `talking-head-recut` for titles and information
  cards; use `motion-broll` for continuous abstract animation accompanying speech.
- **Short graphics and promos.** Use `motion-graphics` for standalone titles,
  figures, or maps; select an `explainer-*` workflow for product promos; use
  `product-launch-video` when the input is a website URL.
- **Rendering engine.** Use HyperFrames (HTML + GSAP); do not add Remotion skills.
- **AI generation versus code animation.** Animate typography, charts, and UI
  with code for repeatability and quick edits. Reserve Higgsfield/Kling footage
  for photorealistic shots that cannot be built that way.
- **AI-shot videos start with `storyboard`.** Show the visual shot sequence and
  obtain approval before generating images or clips. Each phase has a review gate.
- **AI clip prompts.** Look up the specific Melies technique before writing a
  shot prompt; use concrete camera, framing, and lighting direction.
- **Music before editing.** For promos, trailers, and music-led montages:
  idea → narrative storyboard with approximate timings → select and approve a
  recording → analyse phrases, energy, beats, and silence → finalize shot and cut
  times → generate/animate clips → edit. Save the accepted recording and its source
  in `04_audio/`. A requested BPM or prompt does not guarantee the generated timing;
  measure the selected take. Phrase changes and pauses matter as well as beats;
  every cut need not land on a beat. References and keyframes can be prepared early,
  but final durations depend on the recording.
- **Bespoke music.** Use `media-use` for a generic or inexpensive bed. When the
  piece's arc depends on the music, use `suno-songwriter` to write the brief and
  Suno v6 prompts (2-3 directions), generate takes on Suno through an approved
  channel, and save `music-brief.md`, `suno-generation.json`, and the selected take
  in `04_audio/`. Persona or album files go in the production folder, not the
  workshop root. Do not automate Suno through cookies, CAPTCHA handling, or browser
  scraping; see `research/suno-skills-evaluation.md`.
- **Narrated video or interview.** Voice/dialogue determines the structure first.
  Select supporting music before locking the edit and keep it subordinate to speech.
- **Finishing order.** With music or voice already selected: cuts → colour →
  overlays/B-roll → captions → SFX and final mix. Captions sit above overlays.
  `media-use` sources audio, `music-to-video` analyses a track in music-led workflows,
  and `hyperframes-audio` mixes the placed tracks.

## Recipes

### YouTube video to shorts

1. Run `descargar.ps1 "URL" references`.
2. Optionally use `watch` to locate strong moments.
3. Use `clipify` for 9:16 clips with captions.

### Recorded takes to a YouTube video

1. Use `video-use` for cuts, colour, and captions, with output in the production's
   `edit/` directory.
2. Add graphics with `talking-head-recut` or `motion-broll`.
3. Use `sound-effects` if the video includes motion graphics.

### Product launch

1. Plan the narrative storyboard, approve the music, and retime the shots.
2. Build with `explainer-high-energy` for a teaser or `explainer-default` for a demo.
3. Use `sound-effects` for sound design and `hyperframes-audio` for the final mix.

### Explain a topic without filming

1. Start with `faceless-explainer` and the source text.
2. Use `media-use` for voiceover and music.

### Video with AI-generated shots

Use `storyboard` and keep all files in the production's role folders
(`videos/<date>_<name>/` when standalone).

1. **Idea:** restate the brief, clarify missing details, suggest a name, and review
   lessons from earlier productions.
2. **Shots:** propose a sequence using Melies techniques, explaining what appears,
   why each shot belongs, and useful alternatives.
3. **Storyboard:** show the HTML board printed by `storyboard.py build`. Each shot plays its technique
   reference; sequence playback previews the rhythm, and alternatives can be compared.
   Iterate until approved.
4. **Music preproduction:** approve a recording, save it with source/licence details
   in `04_audio/`, analyse changes, and set shot timings against it. If narration
   drives the piece, use the accepted voice first. References and keyframes may
   advance alongside this step; animation with final timings must wait.
5. **Keyframes:** prepare one image per shot, with character/location references
   first when they recur, and show it beside its reference.
6. **Animation:** adapt each technique's prompt template with `kling-ai`, generating
   enough source duration for the approved musical cut.
7. **Assembly:** use FFmpeg for simple cuts or HyperFrames for transitions and text,
   following the accepted recording. Finish with captions, SFX, and mixing.

Before generating paid images, clips, or music, state the quantity, model, and
estimated cost and obtain approval. Future shared samples belong in `examples/`;
current production storyboards remain local in `videos/`.

### Evaluating a new skill

1. **Retrieve the content without login where possible.** For post text, try
   `yt-dlp --skip-download --print description "URL"`. Download attached videos
   into a temporary project folder and inspect FFmpeg contact sheets; use `watch`
   for longer recordings. If a post requires a comment to receive a link, identify
   the tool from visible names and search for its source. If Instagram requires
   login, request a screenshot or permission to use `--cookies-from-browser`.
2. **Identify the product.** It may be a skill, plugin, CLI, paid service, or
   reference website.
3. **Inspect the repository.** Use `gh api repos/<owner>/<repo>` for activity,
   stars, and licence; read `SKILL.md` and installation instructions.
4. **Review risks before installation.** Inspect scripts for `curl | sh`, `iex`,
   `eval`, `base64`, data transmission, and credential access. Check requested API
   keys and telemetry. Reject unlicensed, abandoned, or very low-adoption repositories.
5. **Compare against this guide.** Determine whether it fills a gap or duplicates
   an existing skill, and whether a replacement is meaningfully better.
6. **Record a verdict.** Install, retain as reference, replace an existing skill,
   or reject. To install, add the source, full commit, unique name, path, hash, and
   licence to `skills.lock.json`; follow `docs/skills.md` and update this guide.

## References

| Resource | Purpose | Usage |
|---|---|---|
| [Melies Cinematic Techniques](https://melies.co/cinematic-techniques) | 424 camera, framing, lighting, colour, editing, genre, and viral techniques, with examples and prompt templates | Consult the specific public technique page, such as `/cinematic-techniques/camera-movement/dolly-in`, and adapt its template. Keep the library on its own site. The paid Melies CLI is not used because it duplicates Higgsfield. |

## Requirements and credentials

| Skill | Requirements |
|---|---|
| `video-use` | `ELEVENLABS_API_KEY` in its local `.env` for transcription; uses provider credits |
| `watch` | No transcription provider when captions exist; otherwise local WhisperX (~1.5 GB) or a Groq, OpenAI, or Gemini key |
| `media-use` | Authenticated `heygen` CLI for its music, voice, and avatar catalogue, or generation tools connected to the agent session |
| `clipify`, `embedded-captions` | Local transcription; downloads a model on first use |
| `motion-broll`, `explainer-*` | Install Playwright and Chromium on first use |
| `object-separation` | Downloads SAM2 on first use; CPU processing is slow. Choose CUDA and model size for the machine's GPU. |

## Skill sources

| Skills | Repository |
|---|---|
| `storyboard` | Project-owned (`.claude/skills/storyboard/`) |
| `hyperframes`, `hyperframes-*`, `media-use`, `embedded-captions`, `talking-head-recut`, `general-video`, `faceless-explainer`, `motion-graphics`, `music-to-video`, `slideshow` | heygen-com/hyperframes |
| `video-use` | browser-use/video-use |
| `watch` | bradautomates/claude-video |
| `clipify` | louisedesadeleer/clipify |
| `explainer-*`, `motion-broll`, `object-separation`, `sound-effects` | Barty-Bart/motion-graphics |
| `kling-ai` | maciejdzierzek/kling-ai-prompt-generator |
| `suno-songwriter` | regiellis/suno-songwriter-agent-skill |
