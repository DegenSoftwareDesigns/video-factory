# Common entry and specialist agents: evaluation

Date: 2026-10-31. Status: recommendation, not implemented.

## Question

Should the workshop offer one common entry point plus specialist agents for
(1) cinematic AI video, (2) motion graphics and (3) editing, each reusing the
installed skills and respecting a client project's destination and deliverables?

## What already exists

- **Routing:** `GUIDE.md` already maps requests to skills and resolves overlaps.
- **Destination contract:** `videos.py paths <id>` gives every role folder,
  reference, record and declared deliverable; `videos.py check <id>` verifies them
  (`docs/client-projects.md`). Any specialist can take this JSON as its brief.
- **Skills per track:**

| Track | Skills reused | Main roles written | Approval gates |
|---|---|---|---|
| Cinematic AI | `storyboard`, `kling-ai`, Melies lookup, Higgsfield MCP, `suno-songwriter`/`media-use`, `music-to-video` | plan, references, keyframes, clips, audio | Idea, shots, storyboard, audio timing, every paid image/clip batch |
| Motion graphics | `hyperframes` router, `motion-graphics`, `explainer-*`, `general-video`, `hyperframes-registry`, `hyperframes-animation`, `sound-effects`, `hyperframes-audio` | plan, assembly, audio, final | Brief/design, text on screen, render review |
| Editing | `video-use`, `clipify`, `embedded-captions`, `talking-head-recut`, `motion-broll`, `watch`, `media-use`, `hyperframes-audio` | assembly, audio, final | Cut list, captions style, final review |

## Constraints that decide the design

1. **Gates need the user.** Every track stops for approval between phases, and
   paid generation needs an explicit OK in chat. A Claude Code subagent runs
   without talking to the user and returns one report, so it cannot hold a gate.
2. **Cold context.** A subagent re-reads guide, skills, brief and references.
   For short gated steps this costs more than it saves.
3. **Two agents.** Codex and Claude Code share `AGENTS.md` and skills, but not
   `.claude/agents/` definitions. Anything essential must live in shared files.
4. **Destinations.** Specialists must not invent folders; the contract above
   already removes that risk if every brief includes the `paths` output.

## Recommendation

**One common entry, in the main conversation.** Add a project-owned skill (for
example `video-factory`) that: resolves or creates the production
(`videos.py new/paths`, with `--project` when a client is named), reads
`learnings` and the client's `context`, classifies the request into one of the
three tracks using `GUIDE.md`, loads that track's skills, and runs `check` before
each STOP. It replaces nothing; it makes the existing routing discoverable as a
single command, shared by Claude Code and Codex.

**Specialists as tracks, not autonomous agents, for gated work.** Each track is a
short section of that skill (or three small project-owned skills) listing which
existing skills to load, the roles it writes, its gates and its deliverable checks.
The conversation stays with the user, so approvals and costs remain explicit.

**Subagents only for bounded, approved, non-interactive work.** Good candidates:

- *Prompt writer:* turn an approved storyboard into the declared prompt document
  (e.g. Stogie's single `animation-prompts.txt`) using Melies templates and `kling-ai`.
- *Render and check:* lint/render a HyperFrames composition, make contact sheets,
  run `videos.py check`, and report problems.
- *Edit pass:* execute an approved cut list with `video-use` or FFmpeg into the
  assembly role.

Each receives the `paths` JSON and the approved decision in its brief, writes only
to the listed roles, never submits paid generations, and returns a report the main
conversation reviews before the next gate.

## Proposed next step

Implement the `video-factory` entry skill with the three track sections and the
destination checklist, then pilot it on Stogie's next approved step (FHD keyframes)
without paid generation until the user approves quantity, model and cost.
Add subagent definitions only after a track shows a repeated bounded task.
