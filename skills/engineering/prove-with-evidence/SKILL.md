---
name: prove-with-evidence
description: >-
  Use when an implementer or reviewer must prove a code/UI change actually works
  — before/after screenshots, live URL, or CLI evidence — before calling a task
  done or Ready for Review.
---
# Prove with evidence

Close the feedback loop without the human as meat proxy. Adapted from Lingxi (screenshot proof) and poteto (hands and eyes).

## When

Any claim of "done", "fixed", "Ready for Review", or "shipped" for a user-visible or behavior change.

## Required evidence (pick what fits; do not skip)

1. **Target** — Exact live URL, commit SHA, or local command that runs the build under test.
2. **Path** — Steps a user takes (or Feature Map entry if the repo has one).
3. **Before / after** — Screenshot pair, short clip note, or CLI transcript showing the failure gone / feature present.
4. **Scope note** — What was *not* tested.

## Rules

- Prefer driving the **real** app (browser, Playwright/CDP, simulator, or project `verify` skill) over reading code and asserting.
- If the stack has `/create-verification-skill` output, use that project verify skill and keep its Feature Map honest.
- Multimodal: when a screenshot is attached, **look** at it and reject if it does not show the asked change.
- Push back and keep iterating until proof matches the ask — do not hand a soft "looks fine" to Helic.
- Implementer proof ≠ acceptance. A **non-author** reviewer still runs UAT for user-facing / portfolio ships (on Helic's fleet: **QA仔**).

## Report shape (one short block)

- Claim (one line)
- Evidence links / paths
- Pass / fail / blocked
- Next owner if fail

## Anti-patterns

- "Tests passed" with no behavior check.
- Screenshot of code or terminal only, when the bug is visual.
- Asking Helic to open the site and confirm as the primary verify step.
