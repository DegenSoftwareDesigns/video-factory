# video-factory

Shared workshop for planning, generating and editing videos. For creation, editing,
audio decisions or skill selection, read `GUIDE.md` before starting the workflow.
For installation and dependency updates, read `README.md` and `docs/skills.md`.

## Production

- Write shared documentation, code comments, examples, and published copy in English.
  Match the user's language in conversation; local production notes can follow it.
- Standalone (default): keep every production in `videos/<date>_<name>/`, created with
  `python scripts/videos.py new "<name>" --tipo <type> --formato <aspect> --intencion "..."`.
  Read `python scripts/videos.py learnings` before planning.
- Client project: when the user names another project, or the production belongs to
  one, add `--project <folder|alias>` and follow `docs/client-projects.md`. Its
  `video-factory.json` sets folders, references, records and deliverables. The user's
  instructions on organization override the manifest, and the manifest overrides
  the standalone folders.
- In music-led promos and trailers, select the track and map its musical changes
  before final shot durations, clip animation and editing. The detailed sequence
  and narration-led exception live in `GUIDE.md`.
- Before writing files, read `python scripts/videos.py paths <id>` and put each
  output in its role folder: plan, references, keyframes, clips, audio, assembly,
  final. Standalone roles are the numbered folders, with deliverables in `final/`
  and HyperFrames projects inside `05_montaje/`. Produce exactly the declared
  deliverables and confirm them with `videos.py check <id>`.
- Use the project's own `storyboard` for AI-shot planning and the installed
  `hyperframes` router for composition work. Resolve skill-name overlap using
  `GUIDE.md`.
- Record ratings and technical lessons with `scripts/videos.py update`; edit
  `videos.csv` through that script. Each collaborator has a local learning log.
  Client approvals, costs and decisions also go in the client's own records.
- Do not accumulate junk. When the user approves the final video, mark it
  `terminado`; that prints the cleanup dry run. Show it and run
  `videos.py clean <id> --yes` after the user's OK. Cleanup keeps the final
  video, declared deliverables, the keyframe images and clips the final version
  uses, and `storyboard.json`; it removes discarded or replaced takes, drafts,
  references made for the video, audio, assembly projects and intermediate renders.
  Keep `storyboard.json` pointing at the final takes so they survive, and use
  `--keep` for final-version clips built outside it. In `final/`, keep only the
  latest light version per format (under 20 MB); name older versions and heavy
  masters with `--drop`. Cleanup never removes anything else from `final/`. In client
  projects it only touches folders named after the production, never shared folders
  or client references. Move anything reusable (approved references, music) to a
  brand kit before cleaning. Preserve active productions.

## Environment and dependency ownership

- Use Python from `.venv` and install Python packages into that environment.
  On Windows set `PYTHONUTF8=1`; use `.venv/Scripts/python.exe` or activate it.
  Adapt upstream macOS examples to the actual OS (FFmpeg CPU decode on Windows,
  project-local scratch folders, no Homebrew commands on Windows).
- `skills.lock.json` owns external skill versions; `package-lock.json` owns the
  root HyperFrames CLI dependency. Use `npm exec -- hyperframes ...` from the
  workshop root, or a production's own pinned scripts from its folder. Client
  projects reuse these dependencies; do not install workshop tools into them.
- Keep the shared pins stable while producing a video. Treat upstream automatic
  skill-update instructions as a proposal to update the shared lock through
  `docs/skills.md`; do not overwrite installed copies during a production.
- External skills in `.claude/skills/` and `.agents/skills/` are generated local
  dependencies. Put deliberate reusable changes in project-owned skills or
  documented patches rather than editing those installed copies.
- Machine-specific paths belong in ignored local configuration, such as
  `projects.local.json` aliases for client projects. Connections to Higgsfield,
  HeyGen and other providers are configured per user.

## Repository boundary

- `videos/`, `videos.csv`, `.work/`, brand workspaces, `vendor/`, virtual
  environments, credentials, caches and renders stay local. Preserve existing files there.
- Store new local brands in `brands/<name>/`. Existing brand folders can remain
  where they are; include only the required branding in shared examples.
- Add shared samples to `examples/<name>/` with minimal media, source credits
  and execution instructions. Follow `examples/README.md`.
- Store credentials only in ignored `.env` files or provider authentication.
  Publish placeholders in `.env.example`; never print actual secret values.
- Before a commit intended for sharing, run
  `python scripts/doctor.py --publication` and inspect the Git inventory.
