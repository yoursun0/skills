---
name: skill-upstream-sync
description: >-
  Use when weekly (or on demand) syncing unmodified external agent skills from
  public GitHub into local `.agents/skills`. Tip lane auto-replaces on content
  hash change; pin lane only reports when upstream moved past a pinned SHA.
---
# Skill upstream sync

Helic-authored **tool** that fetches third-party skills at install time. It does
**not** republish anyone else's skill bodies into [yoursun0/skills](https://github.com/yoursun0/skills).
That public repo stays Helic-invented skills only.

## Two lanes

| Lane | Behavior |
| --- | --- |
| `tip` | Track upstream default-branch HEAD for the skill path. When the content hash of installed files differs from upstream, replace the local `install_as` folder. |
| `pin` | Never auto-overwrite. If upstream tip SHA ≠ `pin_sha`, print `PIN_STALE` and leave the local copy alone. Use for skills you adapted (e.g. grilling on Grok Bot) or want frozen. |

## When

- Weekly cron / scheduled agent pass over Hippo-PC or a MacBook.
- On demand after Matt / poteto / other authors ship skill updates.
- Before trusting that local `.agents/skills/<name>` matches public tip.

**Grok Bot** is separate: it uses Cursor-managed / fleet skill stores, not this
script's default dest. Document Grok pins in the fleet manifest comments and
sync Grok copies only when Helic explicitly asks (adapted skills stay `pin`).

## Manifest discovery (first existing wins)

1. `$AGENT_SKILLS_UPSTREAMS` (file path)
2. `./upstreams.yml` (cwd)
3. `~/.config/agent-skills/upstreams.yml`
4. `%USERPROFILE%\.config\agent-skills\upstreams.yml` (Windows)

Override with `--manifest PATH`. Default install dest is `~/.agents/skills` or
`%USERPROFILE%\.agents\skills`; override with manifest `dest:` or `--dest`.

## Schema

See [assets/upstreams.example.yml](assets/upstreams.example.yml). Each upstream
needs `id`, `repo` (`owner/name`), `path` (directory inside the repo),
`install_as` (folder under dest), `lane` (`tip`|`pin`). `pin_sha` is required
for `pin` (full or 7+ hex chars).

## Run

```sh
# from a checkout of this skill, or any path to sync.py
python3 scripts/sync.py --dry-run
python3 scripts/sync.py --manifest /path/to/upstreams.yml --dest ~/.agents/skills
```

Windows (PowerShell), after copying the skill or cloning yoursun0/skills:

```powershell
python scripts/sync.py --manifest $env:USERPROFILE\.config\agent-skills\upstreams.yml
```

macOS / Linux cron example (weekly Monday 09:00 local):

```cron
0 9 * * 1 cd "$HOME" && /usr/bin/python3 /path/to/skill-upstream-sync/scripts/sync.py --manifest "$HOME/.config/agent-skills/upstreams.yml" >>"$HOME/.cache/agent-skills-sync.log" 2>&1
```

Exit code is **0** when the run finishes without hard failure. One line per
skill: `UPDATED|UNCHANGED|PIN_STALE|ERROR` + `id` + short SHA.

Optional: set `GITHUB_TOKEN` or have `gh` authenticated for higher GitHub API
rate limits. Public repos work unauthenticated at lower quotas.

## Policy

- Never `git add` fetched upstream skill trees into yoursun0/skills.
- Only list upstreams you install **unmodified**. Forks you edited stay `pin`
  (or live only on Grok / a private store).
- Hash is over sorted relative paths + file bytes; rename-only upstream churn
  still updates when content differs.
