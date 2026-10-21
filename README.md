# Agent Skills

Reusable AI agent skills by [Helic Leung](https://github.com/yoursun0), distilled from practical engineering and creative work. Each skill packages a focused workflow, supporting references, and any scripts needed to carry it out.

Install the skills you need, adapt them to your projects, and contribute improvements from real use.

## Available skills

### Creative

| Skill | Use it for | Requirements |
| --- | --- | --- |
| [hyperframe-video](skills/creative/hyperframe-video/SKILL.md) | Producing or substantially revising a complete HyperFrames video, from reference study and storyboarding through rendering and delivery verification. | A working HyperFrames environment; supporting skills and fallback guidance are listed in the workflow. |
| [siliconflow-media](skills/creative/siliconflow-media/SKILL.md) | Generating images, video clips, and speech through SiliconFlow with a bundled Python runner. | Python 3.11+, `uv`, and a SiliconFlow API key for live generation. Optional encrypted credential storage requires Windows PowerShell. |

## Installation

With [Bun](https://bun.sh/) installed, use the [Skills CLI](https://github.com/vercel-labs/skills) to select skills and a target agent:

```sh
bunx skills@latest add yoursun0/skills
```

Install a specific skill:

```sh
bunx skills@latest add yoursun0/skills --skill siliconflow-media
```

Add `--global` to install at user scope instead of in the current project. Installation provides the skill files; follow the selected skill's prerequisites to set up its tools and credentials.

For manual installation, copy an individual skill directory from `skills/creative/` into your agent's skill directory. Include its complete contents so relative references and bundled scripts work. Consult your agent's documentation for the destination and invocation syntax.

After installation, ask your agent to use the skill by name, for example:

```text
Use siliconflow-media to generate an illustration for this project.
```

Read the skill before running it. Live media generation requires your own provider account and may incur charges; installation does not authorize paid requests.

## Repository structure

```text
.
├── README.md
├── AGENTS.md
├── LICENSE
└── skills/
    └── creative/
        ├── hyperframe-video/
        │   ├── SKILL.md
        │   └── references/
        └── siliconflow-media/
            ├── SKILL.md
            ├── agents/
            ├── references/
            └── scripts/
```

Each skill lives in `skills/<category>/<skill-name>/`. `SKILL.md` is the entry point; supporting files stay beside it. Categories organize browsing, while skill names remain unique across the repository. Add categories as the collection grows.

## Contributing

Issues and pull requests are welcome. Describe the problem, intended user, and an example of when the skill should apply. For a new skill:

1. Create `skills/<category>/<skill-name>/SKILL.md` with YAML frontmatter containing `name` and `description`. Match the name to the directory, using lowercase letters, numbers, and hyphens.
2. Write actionable instructions with clear completion criteria. Keep detailed references and scripts in the skill directory, and use relative links.
3. Document prerequisites, external services, and material limitations. Keep credentials, generated output, and local configuration out of the repository.
4. Add the skill to the catalog above. Check its links and discovery, and exercise relevant scripts with offline or dry-run checks before submitting.

Agents editing this repository should follow [AGENTS.md](AGENTS.md).

## Acknowledgments

The collection and folder organization are inspired by [Matt Pocock's skills](https://github.com/mattpocock/skills) and [Anthropic's skills](https://github.com/anthropics/skills).

## License

[MIT](LICENSE). Third-party tools, models, and assets remain subject to their own licenses and service terms.
