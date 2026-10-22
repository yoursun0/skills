# Agent Skills

Eight reusable workflows for AI agents by [Helic Leung](https://github.com/yoursun0), organized into Creative, Engineering, Sensor, and Text. Each skill bundles its instructions, references, and runtime scripts so it can be installed into another project.

## Skill catalog

Choose Creative to produce visual media, Engineering to verify a deployment, Sensor to understand video, or Text to write and edit prose. Follow each skill's linked instructions for its full workflow and setup.

### Creative

| Skill | What it does | Prerequisites |
| --- | --- | --- |
| [blender-render](skills/creative/blender-render/SKILL.md) | Builds a Blender model from reference photos and delivers a `.blend` file plus ten PNG camera angles. | Blender 5.2 and reference images; OptiX GPU rendering when available, CPU fallback otherwise. |
| [hyperframe-video](skills/creative/hyperframe-video/SKILL.md) | Produces complete HyperFrames videos through reference study, storyboarding, animation, rendering, and delivery review. | A working HyperFrames environment; the skill documents supporting workflows and fallbacks. |
| [game-gui-aesthetics](skills/creative/game-gui-aesthetics/SKILL.md) | Designs and reviews game HUD/menu/shop/results chrome and mock-to-live visual handoffs for dark-rogue or card-game UIs. | None beyond an agent that can read `SKILL.md`; optional deepen links are listed in the skill. |
| [siliconflow-media](skills/creative/siliconflow-media/SKILL.md) | Generates images, video clips, and speech through SiliconFlow. | Python 3.11+, uv, and a SiliconFlow API key. Optional encrypted credential storage uses Windows PowerShell. |
| [ace-music](skills/creative/ace-music/SKILL.md) | Generates music / game BGM / instrumental loops through the free ACE Music hosted API. | An ACE Music API key from [acemusic.ai/playground/api-key](https://acemusic.ai/playground/api-key); set `ACE_MUSIC_API_KEY` (or `ACE_MUSIC_API_KEY_FILE`). Python 3 for the bundled script. |

### Engineering

| Skill | What it does | Prerequisites |
| --- | --- | --- |
| [ship-then-uat](skills/engineering/ship-then-uat/SKILL.md) | Ships a change and tests acceptance criteria against the live deployment of that commit. | A live URL and a way to verify the deployed commit; supports solo or split deploy/UAT ownership. |

### Sensor

| Skill | What it does | Prerequisites |
| --- | --- | --- |
| [watch](skills/sensor/watch/SKILL.md) | Answers questions about videos from a URL or local file, using Gemini analysis or local timestamped frames and transcripts. | Python 3.10+ and uv. Local analysis needs FFmpeg/ffprobe and yt-dlp; Gemini needs a Google API key. Optional speech fallbacks use WhisperX, Groq, or OpenAI. |

### Text

| Skill | What it does | Prerequisites |
| --- | --- | --- |
| [my-writing](skills/text/my-writing/SKILL.md) | Writes 散文、小說、詩詞 and 週記 in Helic Leung / 凌晨's voice; edits Chinese or bilingual prose; reviews wording without rewriting. | Bundled voice notes and editing references. Supply source text for editing or continuation. |

## Install

With [Bun](https://bun.sh/) installed, run the [Skills CLI](https://github.com/vercel-labs/skills) to choose skills and a target agent:

```sh
bunx skills@latest add yoursun0/skills
```

Install one skill by name, regardless of its category:

```sh
bunx skills@latest add yoursun0/skills --skill watch
```

Add `--global` for user-wide installation. For manual installation, copy the complete skill directory into your agent's skills directory, including its scripts, references, and assets.

From a local checkout, list the available skills or install one directly:

```sh
bunx skills@latest add . --list
bunx skills@latest add . --skill watch
```

Installation supplies workflow files. Configure tools and credentials separately; cloud analysis, transcription, and media generation may upload content and incur provider charges. The individual skills describe their data flows and setup choices.

## Use a skill

Ask your agent to use the installed skill by name and supply the source material or acceptance criteria it needs:

| Task | Example request |
| --- | --- |
| Model a subject | Use blender-render to model this building from the attached reference photos and render ten angles. |
| Produce a video | Use hyperframe-video to create a 30-second product explainer from this brief. |
| Design game GUI chrome | Use game-gui-aesthetics before drawing HUD plaques or handing mocks to an implementer. |
| Generate media | Use siliconflow-media to generate an illustration from this prompt. |
| Generate music / BGM | Use ace-music to generate a 30-second instrumental game BGM from this prompt. |
| Verify a release | Use ship-then-uat to deploy this change and test these acceptance criteria against the deployed commit. |
| Understand a video | Use watch to summarize this video and cite the key timestamps. |
| Edit prose | Use my-writing to edit this Chinese draft for natural expression while preserving its meaning and author voice. |

## Layout

```text
skills/
├── creative/
│   ├── blender-render/
│   ├── game-gui-aesthetics/
│   ├── hyperframe-video/
│   └── siliconflow-media/
├── engineering/
│   └── ship-then-uat/
├── sensor/
│   └── watch/
└── text/
    └── my-writing/
```

Each skill lives at `skills/<category>/<skill-name>/SKILL.md`. Categories organize the catalog; skill names are unique across the repository. Supporting code belongs in `scripts/`, detailed guidance in `references/`, reusable files in `assets/`, and agent metadata in `agents/` when needed.

## Contribute

Issues and pull requests are welcome. Describe the task, intended user, and an example request the skill should handle. Follow [AGENTS.md](AGENTS.md) when editing this repository.

1. Keep the skill self-contained and portable. Match its frontmatter `name` to its directory and write a description that explains when it applies.
2. Document dependencies, external services, and limitations. Keep credentials, local environments, and generated media outside version control.
3. Update the catalog and affected references whenever skills are added or moved.
4. Check frontmatter, relative links, and relevant offline behavior. Confirm discovery without installing:

   ```sh
   bunx skills@latest add . --list
   ```

## Attribution and license

The collection and folder organization draw inspiration from [Matt Pocock's skills](https://github.com/mattpocock/skills) and [Anthropic's skills](https://github.com/anthropics/skills). The editing guidance in `my-writing` adapts [mrgediao/shuorenhua](https://github.com/mrgediao/shuorenhua); preserve its upstream attribution.

Original contributions are available under the [MIT license](LICENSE). Third-party tools, models, services, and bundled material retain their applicable licenses and terms.
