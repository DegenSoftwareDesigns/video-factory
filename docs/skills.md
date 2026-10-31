# Installing and updating skills

`skills.lock.json` pins seven sources, their full commits, and the SHA-256 hashes of
the 28 installed payloads. Hashes cover each file's path and contents, normalizing
CRLF to LF in UTF-8 text so Windows and Unix installations agree. Secrets, Git
metadata, and caches are excluded. Clipify's exclusions omit its promotional
image/README; video-use's exclusions omit upstream tests. suno-songwriter's exclusions
omit its website, changelog, evaluation dataset, and ZIP packager, matching the
upstream installable ZIP. This reproduces the
original working copies while retaining their included licences.

## Installation

```powershell
python scripts/skills.py install --target both
python scripts/skills.py status --target both
```

Downloads use separate Git checkouts per source/commit in `.cache/skill-sources/`.
Root licences and notices remain available in those checkouts. External skill
directories are copied into `.claude/skills/` or `.agents/skills/`. The installer
does not execute upstream installation scripts or use submodules, junctions, or
symlink privileges.

Running the installer again preserves matching directories. If it detects a
difference, it stops and reports the path without overwriting the directory or
deleting its `.env`. `status` runs locally without network access. `CHANGED` can
mean a local edit, an automatic agent update, or a different installed version.

To install a single source:

```powershell
python scripts/skills.py install --source clipify --target claude
```

`storyboard` is currently our only project-owned skill. Its versioned source is
in `.claude/skills/storyboard/`; a full installation also copies it for Codex.
If the Codex copy is outdated, back it up and move it outside `.agents/skills/`
before reinstalling. The original source stays in place.

## Updating a source

1. Review upstream changes, scripts, requirements, and licences. Test the change
   in a local trial production. Historical `vendor/` directories can remain for
   reference, but no longer determine the workshop's dependency versions.
2. Update that source's full commit in `skills.lock.json`.
3. Run `python scripts/skills.py fetch --source <id>`. This only downloads code.
4. After reviewing the new contents, calculate each hash:

   ```powershell
   python scripts/skills.py digest --source <id>
   ```

   Copy the hashes into the lockfile. This command neither changes the lockfile
   nor installs anything.
5. Back up previous installations outside the skill directories, including their
   `.env` files, then reinstall the source. Restore credentials locally.
6. Run the workshop tests and validate/render the sample or trial production
   used in step 1. Inspect the result. Share the lockfile change with the old/new
   versions and the checks performed.

Automatic update instructions bundled with some skills do not change the team's
lockfile. Keep the tested pin during a production. Add a new skill with a unique
name, source, commit, path, hash, and licence.

To update the HyperFrames CLI, change its version in `package.json` and regenerate
`package-lock.json` with `npm install --package-lock-only --ignore-scripts`.
Then run `npm ci` and validate a project. Skills and the CLI have different release
cycles, so review both pins explicitly.
