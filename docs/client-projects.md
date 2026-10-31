# Using the workshop from another project

The workshop's methodology (storyboard gates, music-before-editing, Melies prompts,
finishing order, learning log) does not depend on where files are stored. Each
production resolves seven **roles** to folders:

| Role | Standalone default | Holds |
|---|---|---|
| `plan` | `00_plan/` | Planning deliverables (storyboard sheets, prompt documents) |
| `references` | `01_referencias/` | New character, product or location references |
| `keyframes` | `02_keyframes/` | One starting image per shot |
| `clips` | `03_clips/` | Generated or trimmed clips |
| `audio` | `04_audio/` | Accepted music/voice, provenance, timing map, SFX |
| `assembly` | `05_montaje/` | HyperFrames projects and intermediate renders |
| `final` | `final/` | Deliverables |

Without `--project`, everything works as before: `videos/<date>_<name>/` with the
numbered folders. With `--project`, the client project decides.

## Precedence

1. The user's instructions in the conversation. Agents apply them through the
   flags below or, for lasting rules, by updating the client manifest.
2. Flags on the current command: `--out`, `--role ROLE=PATH`, `--refs`,
   `--deliverables FILE`.
3. Flags given when the production was created (kept in `.work/<project>/<name>/production.json`).
4. The client manifest, `video-factory.json`.
5. The standalone defaults.

`--out DIR` moves every role that is not also named with `--role`. `--refs`
replaces the manifest's reference list. Relative paths resolve against the client
project root; the manifest's own paths also accept `{production}`.

## Manifest

Place `video-factory.json` at the client root or one folder below it (for example
next to the project's other records). Paths are relative to `root`, which is
relative to the manifest.

```jsonc
{
  "schema_version": 1,
  "name": "Client", "slug": "client",
  "root": "..",
  "references": ["Brand/Character/turnaround.png", "Brand/References"],   // existing inputs, read-only
  "context": {"brief": "Brand/brief.md", "brand_guide": "Brand/brand-guide.md"},
  "records": {"state": "Brand/campaign.json", "log": "Brand/delivery.md"},  // client-owned records to update
  "env": ".env",                                   // provider keys for this project (the default)
  "layout": {
    "default": "Videos/Storyboard/{production}",    // every role not listed below
    "clips": "Videos/Production/{production}/clips",
    "final": "Videos"
  },
  "deliverables": {
    "planning": {
      "exclusive": true,                           // nothing else in those folders
      "items": [
        {"id": "storyboard", "role": "plan", "glob": "storyboard*.png", "min": 1, "max": 2},
        {"id": "keyframes", "role": "keyframes", "pattern": "shot{nn}.png", "per_shot": true, "size": [1920, 1080]},
        {"id": "prompts", "role": "plan", "glob": "*.txt", "min": 1, "max": 1, "name": "animation-prompts.txt"}
      ]
    }
  }
}
```

A project without a manifest can still be used with `--project <folder> --out <folder>`.
A machine-local alias file, `projects.local.json` (ignored by Git), maps short names
to client folders: `{"stogie": "F:/Proyectos/Memes/stogie"}`.

## Open the workshop from the project

Enable the `video-factory` plugin in the project (README, "Producing for another
project"). A session opened in the project then has the `/video-factory` entry skill,
which reads this workshop's guide and skills and runs the `bin/` commands:

| Command | Runs |
|---|---|
| `vf` | `scripts/videos.py` |
| `vf-storyboard` | the storyboard skill's `storyboard.py` |
| `vf-melies` | the storyboard skill's `melies.py` |
| `vf-hyperframes` | the pinned HyperFrames CLI |
| `vf-run` | any command, with the project's provider keys (`scripts/run.py`) |

Each has a `.cmd` twin for PowerShell and cmd (`vf.cmd`, ...). They use the
workshop's `.venv`, set `PYTHONUTF8=1`, and set
`VIDEO_FACTORY_PROJECT` to the open folder unless it is the workshop itself, so
`--project` becomes optional. Explicit flags still win.

### Provider keys and spending per project

Each project keeps its own provider keys (ElevenLabs, OpenAI, Gemini, Groq, Kling and
other API keys) in a `.env` at its root, or the file named by the manifest's `env`.
Each project's usage is then billed to, and can be counted on, its own accounts. Keep
that file out of the project's Git (`.env` in its `.gitignore`) and copy key names, not
values, into a `.env.example` if the project is shared.

Run every tool or script that needs a key through `vf-run`:

```powershell
& "$env:VIDEO_FACTORY_HOME\bin\vf-run.cmd" --list      # the .env used and its key names, never values
& "$env:VIDEO_FACTORY_HOME\bin\vf-run.cmd" -- python "$env:VIDEO_FACTORY_HOME\.claude\skills\video-use\helpers\transcribe.py" clip.mp4
```

`vf-run` overrides the inherited environment with the project's keys and warns when the
project has no `.env`. Standalone work uses the workshop's own `.env` the same way.
Some skills prefer a key file inside their own folder (`video-use` reads its
`.claude/skills/video-use/.env` before the environment), so leave those files without
keys, or the project would be billed to whoever owns that file.

Generations through tools connected to the agent session (Higgsfield, HeyGen or
ElevenLabs connectors) are billed to the account signed in there and cannot read a
project `.env`. Log each one, with model, quantity and cost, in the project's `records`
(for example an `api_usage` CSV). That log plus the provider dashboards for each
project's keys give the spending per project.

When a provider is reachable both ways (its key in the project's `.env` and its
connector in the agent session), the agent asks which route to use together with the
cost approval for the batch; with only one route it names that one.

### Codex and other agents

Claude Code plugins do not load in Codex. Give the project a short `AGENTS.md`
that points to the entry skill, the Codex skills in `.agents/skills/`, and the
`bin/` commands; Codex reads it whenever it opens the project. Name the workshop
through the `VIDEO_FACTORY_HOME` environment variable, never a fixed path, so the
same file works on every teammate's machine (README, "For the team"):

```markdown
## Video work

For any video, storyboard, keyframes, clips, music or edit, use the video-factory
workshop for instructions and tools, never as storage. WORKSHOP is the folder in the
`VIDEO_FACTORY_HOME` environment variable; if it is empty, ask the user for the path.

1. Read `WORKSHOP/plugin/skills/video-factory/SKILL.md` and follow it. Workshop skills
   are in `WORKSHOP/.agents/skills/<skill>/SKILL.md` (Codex) or
   `WORKSHOP/.claude/skills/<skill>/SKILL.md` (Claude Code).
2. Run its commands from this folder, which they treat as the client project:
   `& "$env:VIDEO_FACTORY_HOME\bin\vf.cmd" paths "<production>"` in PowerShell,
   `"$VIDEO_FACTORY_HOME/bin/vf" paths "<production>"` in Bash. `vf-storyboard`,
   `vf-melies`, `vf-hyperframes` and `vf-run` sit next to it.
3. Destinations and deliverables come from this project's `video-factory.json`.
4. Provider keys live in this project's `.env`. Run keyed tools through `vf-run` and
   log every paid generation, with its cost, in this project's usage record.
```

## Commands

```powershell
python scripts/videos.py new "intro" --project stogie --tipo ia-storyboard --formato 16:9 --intencion "..."
python scripts/videos.py paths stogie/intro          # JSON with every folder, reference, record and deliverable
python scripts/videos.py check stogie/intro --stage planning --shots 8
python .claude/skills/storyboard/scripts/storyboard.py build intro --project stogie
```

`new` registers the production in the local `videos.csv` (column `proyecto`), creates
only the `plan` folder and the workshop-side working folder, and never moves client
files. `check` is read-only and exits non-zero while deliverables are missing,
oversized, duplicated or accompanied by undeclared files. `clean` on a finished
client production keeps declared deliverables, the final-version keyframes and
clips referenced by `storyboard.json`, files directly in the final folder, and the
client's references, context and records. It removes everything else only inside
folders named after the production (`{production}` in the layout) and the
workshop's working folder; shared folders are never emptied. It refuses while the
final folder has no result.

## What stays where

- **Client project:** declared deliverables, client records (state, logs, usage
  records) and reused references. Follow the client's naming and folder rules.
- **Workshop:** dependencies (`.venv`, skills, HyperFrames CLI), the methodology,
  `videos.csv` learnings, and `.work/<project>/<name>/` working files such as
  `storyboard.json` and the HTML review board. Nothing there is a deliverable.
- When the client declares deliverables, produce exactly those. Extra planning
  files go to the client only when the user asks or a tool genuinely needs them.

## Agent checklist

1. Read `python scripts/videos.py paths <id> --project <p>` before writing any file.
2. Read the manifest's `context` documents and reuse its `references` as generation
   inputs; do not regenerate an identity that already exists.
3. Write each output to its role folder with the deliverable's naming pattern.
4. Record approvals, costs and decisions in the client's `records`, in the client's format.
   Run keyed tools through `vf-run` so they use the client's own `.env`.
5. Run `check` before reporting a stage as finished.
