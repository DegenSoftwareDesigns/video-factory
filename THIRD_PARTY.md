# Dependencies and attribution

External skills are downloaded from their original repositories at the commits
in `skills.lock.json`. Installed copies and caches stay outside this repository.
The installer copies files without executing upstream installers, scripts, or
hooks. Root licences are available in `.cache/skill-sources/<id>/<commit>/`.

| Source | Skills | Repository licence |
|---|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | `hyperframes*`, `media-use`, video workflows | Apache-2.0 |
| [bradautomates/claude-video](https://github.com/bradautomates/claude-video) | `watch` | MIT |
| [louisedesadeleer/clipify](https://github.com/louisedesadeleer/clipify) | `clipify` | MIT |
| [maciejdzierzek/kling-ai-prompt-generator](https://github.com/maciejdzierzek/kling-ai-prompt-generator) | `kling-ai` | MIT |
| [Barty-Bart/motion-graphics](https://github.com/Barty-Bart/motion-graphics) | `explainer-*`, `motion-broll`, `object-separation`, `sound-effects` | MIT |
| [browser-use/video-use](https://github.com/browser-use/video-use) | `video-use` | MIT |
| [regiellis/suno-songwriter-agent-skill](https://github.com/regiellis/suno-songwriter-agent-skill) | `suno-songwriter` | MIT |

Media assets may have different licences from the code. Check each skill's
manifests, credits, and `LICENSES.md` before redistributing assets. If future
project-owned skills or examples include third-party material, preserve the
relevant attribution and licence notices alongside it.

`storyboard` and the workshop scripts are project-owned code. These changes do not
assign a new licence to that code or the local brands. Before publishing the
repository publicly, its owner should choose a licence for their contributions.

Services such as HeyGen, Higgsfield, Suno, and ElevenLabs have separate accounts,
costs, and terms. Each teammate configures their own connections and credentials.
