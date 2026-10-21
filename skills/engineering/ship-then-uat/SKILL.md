---
name: ship-then-uat
description: >-
  Use when a site or change is about to go live, or when starting acceptance
  testing, so review and UAT run against the current production commit rather
  than a stale deploy.
---
# Ship then UAT

Use this after the code change exists and the remaining work is to put it on the public host and check it. Do not start the acceptance pass against a host you already know is stale.

## Order

1. Get a live URL for the current intended commit, or confirm the live host is still on an older commit and say so.
2. If leftover absolute URLs, docs, or config still name the old host, open a small follow-up pull request. Do not mix that into an unrelated change.
3. Merge only when the reviewer has said so. A comment that the pull request is ready is not a merge.
4. Redeploy production from the merged commit before testing anything the checklist treats as live.
5. Only then run UAT, against that same live URL. Split HTTP checks and the browser pass if needed, but both must name the commit or deploy they actually hit.
6. If a check was started before the redeploy, re-check the affected items. Do not report a pre-redeploy failure as current.

## Split ownership when multiple agents work

- One agent (or person) owns the credentialed deploy.
- Another owns the code change, the pull request, and the browser pass.
- Do not both chase the same token, login, or connector.
- A browser pass still running on an old deploy must be redirected to the new production URL, not finished and filed as the result.
- Solo use is fine: keep the same order, and do not mark UAT done until the redeploy for the intended commit is live.

## What to report

- Pass or fail per checklist item, with what was actually seen.
- One line on whether live matches the merged commit.
- Notes that are not user-visible (for example a client redirect instead of an HTTP 301) stay notes unless the user asked for that change. Do not open a follow-up pull request for a note.
