---
name: resolve-conflict
description: >-
  Reconcile overlapping code when a remote commit, local edits, and conflict
  markers touch the same files. Keep the tested behavior, carry unique work
  onto that interface, prove it, and commit. Use when the user says resolve
  conflicts, remote and local both changed, or /resolve-conflict.
---

# Resolve conflict

Two bodies of code changed the same files. Produce one commit on the branch the user named. Each side's **intent** survives when the behaviors compose. When they cannot, the **kept interface** is the one a test or an already-merged commit states: signatures, storage keys, and file schema.

Classify the dirty tree before discarding, stashing, or merging. That tree is the evidence.

## 1. Record the tree

Read `git status`, the upstream tracking line, recent log on both sides, and whether a merge or rebase is already in progress.

**Done when** you can name the base commit, the incoming tip, and every dirty or untracked path.

Fetch. When credentials block the fetch and the remote-tracking ref is already present, use that ref and say the fetch did not refresh it.

## 2. State each intent

Read the incoming commit messages and any linked pull request. Read the local diff against the base.

**Done when** each side has one sentence that names the behavior it adds.

## 3. Diff against the incoming tip

For a dirty tree, diff the worktree against the incoming tip. For local commits, diff that range against the incoming tip.

**Done when** you have the paths that would still change if the incoming tip were the base. Set aside paths whose result already matches that tip.

## 4. Classify every remaining path

Label each path:

- **overlap** — one outcome, two edits. Renames, comments, and the same data in another file are overlap. Prove generated or one-line data by parsing it. Equal parsed values are overlap even when the bytes differ by whitespace.
- **unique** — only one side has it. It comes along.
- **incompatible** — both sides change the same behavior. Keep the side a test or the merged commit already specifies. The commit message names that choice.

A second implementation of a feature already on the incoming tip is overlap, plus any unique extras. Channel order, storage keys, and limits are behavior: compare them on purpose. A local edit that removes a key the incoming commit added is incompatible. Keep the key.

**Done when** every remaining path has one label, and every incompatible choice names the test or commit that decided it.

## 5. Integrate onto the kept interface

Save unique files, then move the branch onto the incoming tip. Fast-forward when this branch has no commits of its own. When a merge or rebase is already in progress, finish that operation. Resolve each hunk by its label.

Retarget unique scripts, tests, and comments onto the kept interface. A generator writes the schema the kept code loads. Run it when its inputs exist.

**Done when** no conflict markers remain, the branch contains the incoming tip, and a second generator run leaves its outputs unchanged apart from edits you meant to keep. Restore a file that differs only by line endings.

## 6. Prove

Run the repo's typecheck, tests, and build, in that order, via the scripts it already defines.

**Done when** those commands exit 0. Fix failures the integration caused before committing. Report a check the repo does not have.

## 7. Commit

Stage the unique work and the resolutions. Commit on the branch the user named. The message states the kept behavior and the unique work that landed.

**Done when** `git status` is clean and the new commit's history contains the incoming tip.

Push when the user asks to publish.
