---
name: create-home-repo
description: >-
  Set up a Home Repo: one git repo that holds shared skills, AGENTS.md (or CLAUDE.md),
  and shared docs, with pointers to other repos. Use when the user wants a single place
  to run agents across multiple repositories, following Matt Pocock's Home Repo Pattern.
---
# Create Home Repo

Set up a Home Repo following [Matt Pocock's Home Repo Pattern](https://aihero.dev/the-home-repo-pattern).

A Home Repo is one repository that holds your shared skills, steering files (AGENTS.md / CLAUDE.md),
and shared docs. You run your agent from it. Its steering file holds navigation pointers to each
of your other repos so the agent can open or clone them as needed.

## When to use

- User has multiple repos and wants one place for shared skills, tooling, and agent sessions.
- User asks to set up a home repo, agent hub, or multi-repo agent workspace.
- User wants to centralize skills and avoid duplicated AGENTS.md / skills across repos.

## How to work

- Look up every fact yourself (filesystem, git, gh). Bring the user only decisions.
- Put decisions to the user in rounds. Number each question, give your recommended answer,
  and word it so "yes" accepts it. A question that depends on one still open waits for a later round.
- Until the user approves the plan in Step 3, only read. Do not write or commit anything.
- Secrets stay where they are: leave .env and other secret files unread.

## Step 1: Inventory the repos

Find every git repo under the user's home directory (or the working directory they indicate),
skipping dependency folders (node_modules, vendor, .git inside others, etc.).
For each, record its path, remote, visibility (public or private), and last commit date.

In the first round, ask:
- which repos the Home Repo points at (recommend those with recent commits)
- where it lives, and whether it's new or an existing repo (recommend a new private repo beside the others)
- whether it's personal or shared with a team
- which file the harness loads at session start: AGENTS.md, CLAUDE.md or both (recommend what the setup shows)

Done when every repo found is marked in or out, and the other three questions are answered.

## Step 2: Inventory the shared material

Across the chosen repos and user-level skill folders (such as `~/.claude/skills`, `~/.agents/skills`,
or equivalent), list every skill (a folder with a SKILL.md), every AGENTS.md and CLAUDE.md,
and every doc written for agents: coding standards, glossaries, ADRs.

Sort each item into one bucket:
- shared: true across repos
- duplicate: the same item in several places; diff the copies and mark the newest
- repo-specific: about one repo's code, commands or domain
- installed: from a published skills repo or marketplace

Done when every item sits in exactly one bucket.

## Step 3: Agree the plan

Show a table of every item, where it is now, and its destination:
- shared and duplicate: move to the Home Repo, one copy, newest version
- repo-specific: stays in its repo
- installed: stays installed

Under it, show the Home Repo's AGENTS.md: a short intro, then an "Other Repos" section
with one pointer per repo:

```
<name> (<what it is>): <local path>. Clone from <remote> if missing.
```

Add a hint where a repo needs one, such as "read its AGENTS.md first".
Past about 20 repos, group the pointers into one file per area and point at those files instead.

Settle open items in further rounds. Done when the user approves the table and the AGENTS.md.

## Step 4: Apply the plan

1. Create the Home Repo and its AGENTS.md. If the harness loads a different file,
   add that file as a one-line pointer to AGENTS.md.
2. Copy each shared item in, keeping skill folders whole.
3. In each child repo, on a new local branch, remove the copies that moved.
   Repo-specific material stays.
4. Commit in the Home Repo. Pushing is the user's call.

Done when every row of the table is applied. Report each row's outcome,
the branches you created in each repo, and anything you skipped, with the reason.

## Pointer format

One line per repo:

```
Storefront (Next.js app): ~/repos/acme/storefront. Clone from git@github.com:acme/storefront.git if missing.
Payments API: ~/repos/acme/payments-api. Read its AGENTS.md before changing it.
```

For scale (>20 repos), use progressive disclosure:

```
## Other Repos

Billing (invoices, payments, tax): see repos/billing.md
Storefront (web and mobile apps): see repos/storefront.md
```

## What lives where

| Lives in the Home Repo | Stays in each repo |
| --- | --- |
| Skills used across repos | The repo's code |
| AGENTS.md / CLAUDE.md with pointers | Its own AGENTS.md, build and test commands |
| Shared docs: coding standards, glossary, system-wide decisions | Docs about that repo alone |
| Tooling / custom CLI | |

## Notes

- Run agents from the Home Repo, not individual repos.
- The agent can clone missing repos and use worktrees for parallel work.
- Avoid git submodules for this; plain pointers suffice for most cases.
- Home Repo is preferred over monorepo when mixing public/private repos or when team adoption of a monorepo is low.

Source: https://aihero.dev/the-home-repo-pattern and Matt Pocock's video "The Home Repo Pattern".
