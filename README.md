# Agent Skills

Reusable workflows for AI agents by [Helic Leung](https://github.com/yoursun0). Each skill includes an entry point, task-specific guidance, and any scripts or references needed to use it in another project.

## Skill catalog

### Creative

| Skill | What it does | Prerequisites |
| --- | --- | --- |
| [blender-render](skills/creative/blender-render/SKILL.md) | Builds a Blender model from reference photos and delivers a `.blend` file plus ten PNG camera angles. | Blender 5.2 and reference images; OptiX GPU rendering when available, CPU fallback otherwise. |
| [hyperframe-video](skills/creative/hyperframe-video/SKILL.md) | Produces complete HyperFrames videos through reference study, storyboarding, animation, rendering, and delivery review. | A working HyperFrames environment; the skill documents supporting workflows and fallbacks. |
| [siliconflow-media](skills/creative/siliconflow-media/SKILL.md) | Generates images, video clips, and speech through SiliconFlow. | Python 3.11+, uv, and a SiliconFlow API key. Optional encrypted credential storage uses Windows PowerShell. |

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

Read the installed `SKILL.md` for setup and usage. For example:

```text
Use watch to summarize this video and cite the key timestamps.
```

Installation supplies workflow files. Configure tools and credentials separately; cloud analysis, transcription, and media generation may upload content and incur provider charges. The individual skills describe their data flows and setup choices.

## Layout

```text
skills/
├── creative/
│   ├── blender-render/
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
