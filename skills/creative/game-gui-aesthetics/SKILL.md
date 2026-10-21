---
name: game-gui-aesthetics
description: >-
  Design or review game HUD, menu, shop, and results chrome; match mock SoT to
  live screens; strengthen dark-rogue or card-game GUI aesthetics before
  generating assets. Use when a game UI looks like generic web pills instead of
  intentional chrome, or when handing art to an implementer.
---

# Game GUI aesthetics

Distilled practice for game interface chrome (not landing pages). Prefer this skill when the deliverable is HUD plaques, modal shells, ticket buttons, board frames, or a mock-to-live visual handoff.

## Study sources (optional deepen)

Read when you need more depth; they are not required to follow this skill:

- [directing-game-visuals](https://www.skills.sh/abagames/agentic-gamedev-skills/directing-game-visuals) — palette roles, readable play-state, anti-generic game art
- [game-ui-ux](https://www.skills.sh/akillness/jeo-skills/game-ui-ux) — HUD/menu information architecture, screen stack, mock vs runtime
- [frontend-design](https://www.skills.sh/anthropics/skills/frontend-design) — distinctive direction, anti AI-slop
- [design-taste-frontend](https://www.skills.sh/leonxlnx/taste-skill/design-taste-frontend) — audit existing UI then rebuild direction

Short notes: [references/sources.md](references/sources.md).

## Before any game chrome art

1. **Name the visual phrase** (one line): material + mood + genre (e.g. cracked cream-on-wine ticket plaques, dark memory-match rogue).
2. **Palette roles** (3–5 colors only): assign each a gameplay job (danger / reward / neutral / rare / surface). Never decorative-only accents.
3. **Screen inventory**: list real runtime screens and states. A mock must not delete states it omits — map every live control onto the mock visual language.
4. **Center readable**: board or hero decision stays clear; noise and ornament go to the edges.
5. **Genre materials stay pure**: metal, parchment, and ticket for dark rogue-card UIs; no mustard web pills, generic glassmorphism, or default Inter/Roboto stacks.

## Construction (chrome PNG / CSS)

- Layered surfaces: fill + inset highlight + hard offset shadow + ambient drop (not flat fill + 1px border).
- Gradients with at least three stops; borders may carry their own light–dark–light bevel.
- Texture as a background layer (grain, crackle, paper), not a blur filter.
- Buttons as physical plaques (notched ticket or riveted metal); primary, secondary, and danger must differ in silhouette or color role.
- Mobile portrait first; touch targets at least 44px; respect safe areas.

## Handoff checklist

- Name the SoT mock path and a live screenshot path per screen.
- Split drop-in PNG (path, size, RGBA) from assets that need CSS wiring.
- Acceptance: side-by-side live vs mock for title, difficulty, gameplay, shop, and results.
- Original art only — no third-party game IP silhouettes.

Preserve live information architecture unless the product owner explicitly changes it. Borrow mock color, texture, bevel, and plaque language; do not relocate HUD columns or invent controls the runtime does not have.

## Anti-patterns

- Swapping icons while leaving web-form layout and buttons.
- Solid white or black card mats when transparent RGBA was specified.
- Decorating without communicating state (miss, combo, ante, rarity).
- Asking the user to restyle the live site themselves.
