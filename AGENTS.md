# Working in this repository

This public repository publishes reusable agent skills. Optimize changes for someone installing a skill into a different project, machine, or agent environment.

## Skill boundaries

- Keep each skill self-contained in `skills/<category>/<skill-name>/`, with `SKILL.md` as its entry point. Add a category only when a skill needs it.
- Match the frontmatter `name` to the skill directory; keep names unique across categories. Write descriptions that identify the task and when the skill applies.
- Put executable helpers in `scripts/`, detailed guidance in `references/`, reusable files in `assets/`, and agent-specific metadata in `agents/` when needed. Create only directories with content.
- Keep instructions portable: resolve files relative to the skill directory and document platform or tool dependencies. For dependencies on other skills, explain discovery and what to do when they are unavailable.
- Write ordered actions with observable completion criteria. Move branch-specific detail into linked references rather than expanding the entry point indefinitely.
- When adding, renaming, moving, or removing a skill, update the README catalog and every affected path or reference in the same change.

## Tools and credentials

- Use `uv run` for Python scripts, with PEP 723 metadata for standalone dependencies or `uv add` for a Python project. Use `bun run`, `bun add`, and `bunx` for JavaScript tooling.
- Use `pip`, `npm`, `npx`, or `yarn` only if `uv` or Bun cannot perform the required operation; explain the limitation and obtain user approval first.
- Keep credentials in environment variables or documented local secret storage. Never commit credentials, private prompts, signed URLs, machine-specific paths, installed dependencies, or generated media.
- For cloud account access, check for a capable official CLI first. State the command's scope and get explicit approval before authentication, consent, or reading/writing account data. Otherwise prefer an official or well-maintained MCP integration, then a manual console if neither is available.
- If authentication or permissions block an operation, identify the resource and exact access needed, expose the available sign-in interface or shortest user steps, and wait for authorization before retrying. Keep the requested scope; obtain approval for any reduced-scope fallback. Never request passwords, one-time codes, API keys, client secrets, or tokens in chat.
- Live provider tests require authorization for the request and any cost. Prefer offline validation or dry runs when checking packaging and documentation.

## Verification and delivery

- Read the affected skill and its linked references before editing. Preserve its established behavior unless the task calls for a change.
- Verify that frontmatter is present, names match directories, relative file links resolve, and the README lists the published skills accurately.
- After moving a skill, confirm discovery with `bunx skills@latest add . --list`. This lists local skills without installing them.
- For executable changes, run relevant offline checks and exercise changed behavior. Report live testing separately from dry-run evidence.
- Keep the root MIT license applicable to original contributions. Preserve required third-party attribution and document any bundled material with separate terms.
- Report the files changed, checks performed, and material limitations. Leave commits, pushes, and publication to the user's requested workflow.
- always commit your changes after a complete round of actions.
