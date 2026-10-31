# video-factory

A shared workshop for producing videos with coding agents: visual storyboards,
references, AI-generated footage, HyperFrames animation, editing, and audio.
Workshop code and instructions are versioned; each teammate keeps productions
and provider accounts on their own machine.

## Windows setup

Install Git, Python **3.12**, Node.js **22 or newer**, and FFmpeg/FFprobe on PATH.
The original workstation uses Node 24. Deno is optional for YouTube downloads.
Both Claude Code and Codex can use the workshop; each person configures generation
connectors in their own agent.

From the cloned directory:

```powershell
.\scripts\setup.ps1 -Agent both -Audio
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = '1'
python scripts/doctor.py --target both
```

`-Agent claude` (the default) installs into `.claude/skills/`; `-Agent codex`
installs into `.agents/skills/`; `both` enables both. Our own `storyboard` skill
lives in `.claude/skills/storyboard/`, and the installer creates a copy for Codex.
Start a new agent session after installation to discover the skills.

Setup creates `.venv`, installs the basic dependencies, runs `npm ci`, and installs
the **28 external skills** pinned in `skills.lock.json`. `-Audio` adds music
analysis; `-Transcription` adds Whisper/PyTorch, which requires substantially more
disk space. Some workflows download models and Chromium when first used.
To install skills only: `.\scripts\setup.ps1 -SkillsOnly -Agent both`.

The Python skill installer is portable to macOS/Linux. The PowerShell setup is
tested on Windows; configure the environment manually elsewhere with Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-audio.txt
npm ci
python scripts/skills.py install --target both
python scripts/doctor.py --target both
```

Python requirements pin the direct dependencies tested here; pip resolves
transitive dependencies for each platform. Choose the GPU configuration and
CPU/CUDA build of PyTorch per machine, separately from the basic profile.

## Prepare reusable brands first

Before producing multiple videos for the same brand, company, or project, create
a dedicated local folder at `brands/<name>/`. Build its reference kit once and
reuse it across productions to keep the visual identity consistent.

Include the assets you expect to need: official logos and their variants, fonts,
colour values, backgrounds, textures, product images, and approved visual examples.
Keep a `design.md` describing typography, logo usage, tone, visual rules, and what
to avoid; add a `frame.md` if the brand has specific video layout or motion rules.

For a memecoin, include the main mascot's approved artwork and several character
reference sheets (cheat sheets), ideally covering:

- A turnaround: front, side, three-quarter, and back views.
- Expressions and poses for recurring actions or emotions.
- Distinctive details: proportions, colours, clothing, accessories, and symbols
  that must stay consistent across generated shots.
- Separate sheets for other recurring characters or NFT variants, where relevant.

For example:

```text
brands/<name>/
├── design.md
├── frame.md                 # Optional video-specific rules
├── logos/
├── fonts/
├── backgrounds/
├── mascot/
│   ├── original.png         # Approved primary artwork
│   ├── turnaround.png
│   ├── expressions.png
│   └── poses.png
├── characters/              # Other recurring characters or variants
└── references/              # Approved images and visual examples
```

Point the agent to this folder when briefing a new video. Use approved mascot and
character references as generation inputs whenever those subjects recur; avoid
reconstructing their identity from text alone. Add approved assets and decisions
back to the brand kit as it develops. Brand folders stay local and are ignored by
Git; shared examples include only the branding and references they actually need.

Start with the [EMBER brand kit](examples/ember-brand/README.md): a fictional
identity with editable brand/video guides, configuration, SVG logos, mascot
turnaround/expression/pose sheets, and a local visual preview. Copy it into
`brands/<name>/`, replace the identity and approved assets, and reuse it across
productions. Its small Python builder updates the vector assets from configuration.

## Your first video

Open the agent in this directory and describe the video. `GUIDE.md` determines the
workflow. Shared instructions live in `AGENTS.md`; `CLAUDE.md` imports them.

To create a production directory manually:

```powershell
python scripts/videos.py new "my-promo" --tipo edicion --formato 16:9 --intencion "Product promo"
python scripts/videos.py list
python -m http.server 8765 --bind 127.0.0.1 --directory videos
```

Each production has `00_plan/`, `01_referencias/`, `02_keyframes/`, `03_clips/`,
`04_audio/`, `05_montaje/`, and `final/`. For promos and trailers, choose the music
first, then set shot timings and edit against that recording. Narrated videos use
the voice as the primary timing reference. See the recipes in `GUIDE.md`.

Run the root CLI with `npm exec -- hyperframes ...`; keep the shared pin rather
than substituting `npx ...@latest`. Each production can pin its own CLI version.
Existing CLI flags, stored values, and production folder names retain their
original spelling for compatibility.

## Producing for another project

The workshop can also serve a project that keeps its own folders, such as a
campaign with an established brand kit. Dependencies stay here; the client project
keeps its references, records and deliverables. Add a `video-factory.json` to the
client project describing its folders and deliverables, then pass it explicitly:

```powershell
python scripts/videos.py new "intro" --project "F:\Client" --tipo ia-storyboard --formato 16:9
python scripts/videos.py paths client/intro
python scripts/videos.py check client/intro --stage planning --shots 8
```

One-off destinations can be given with `--out`, `--role ROLE=PATH`, `--refs` and
`--deliverables`, and the user's instructions always win over the manifest. Short
aliases for client folders go in the ignored `projects.local.json`. The manifest
format, precedence and an agent checklist are in `docs/client-projects.md`.

## What is shared

| In Git | Local to each machine |
|---|---|
| Instructions, scripts, and our own `storyboard` skill | `videos/`, `videos.csv`, `.work/` and `projects.local.json` |
| External skill commits and hashes | Installed external skills and `vendor/` clones |
| Node configuration and lockfile | `.venv/`, `node_modules/`, models, and caches |
| Lightweight brand kit and future productions in `examples/` | Personal/client brands and production media |
| `.env.example` templates | `.env`, tokens, sessions, and private paths |

The existing `marca-army/` and `marca-oscar-twitter/` directories remain available
locally. Store new brands in `brands/<name>/`, which is also ignored, and share
only the minimum branding each example needs. Current individual productions and
machine-specific preview servers (`.claude/launch.json`) are excluded. Serve the
storyboard using the HTTP command above.

Git does not back up ignored productions: keep them in the team's shared storage
or backup system. Add lightweight examples later using `examples/README.md`.

## Accounts and maintenance

Each person signs in to their own providers. For HeyGen, use its CLI and
`heygen auth login --oauth` when the catalogue or voice generation is needed.
`video-use` reads `.claude/skills/video-use/.env` (or
`.agents/skills/video-use/.env` in Codex); copy its `.env.example` and fill in the
variables locally. Other connections and credentials are covered in `GUIDE.md`
and the relevant skill.

The root `.env.example` is a reference: the workshop does not load that file
automatically. Export variables into the agent's process or follow the provider's
authentication mechanism.

```powershell
python scripts/skills.py status --target both
python -m unittest discover -s tests -v
python scripts/doctor.py --publication
```

The final command requires a local Git repository and checks tracked files plus
unignored candidates. It checks size limits, private paths, and credential
filenames; review file contents before publishing as well.

Follow `docs/skills.md` to update dependencies. Third-party sources and licences
are listed in `THIRD_PARTY.md`. The three Suno candidates are evaluated in
`research/suno-skills-evaluation.md`; only `suno-songwriter` is installed, as a pilot.
