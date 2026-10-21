---
name: blender-render
description: Build a Blender model from reference photos and render ten camera angles as PNGs. Use when the user supplies images and wants a .blend plus a multi-angle still set, including a repeat of the clock-tower workflow for a new subject. Do not use for material-only edits of an existing scene or for 2D image generation.
---

# Blender Render

Turn reference images into one `.blend` and exactly ten PNGs. The model has to be the object in the photos. The ten filenames are fixed.

## Output

Done only when all of these exist in the subject folder:

- `<name>.blend`, textures packed, a `README` text block stating the scale
- `renders/angle_01_low_hero.png` through `renders/angle_10_aerial.png`

A PNG counts only if the subject is fully in frame and the angle matches the filename. Re-render a failed camera. Do not add an eleventh shot to cover a crop.

| File | Angle |
| --- | --- |
| `angle_01_low_hero` | Low 3/4, wide lens, camera near the ground |
| `angle_02_front` | Front elevation, mild telephoto |
| `angle_03_corner` | 3/4 from the front-right |
| `angle_04_opposite` | 3/4 of the opposite corner |
| `angle_05_side` | Side elevation |
| `angle_06_detail` | Close-up of the front feature |
| `angle_07_top` | Crown: top third, dome or roof included |
| `angle_08_base` | Base or entrance |
| `angle_09_distant` | Far establishing shot, more sky |
| `angle_10_aerial` | High 3/4, landscape |

## Steps

1. Read every input image. Note the front face, real size if known, materials, and the part that must be recognizable in a close-up.
2. Put the subject in its own folder when the project already separates subjects, for example `clocktower/` for a clock tower. Keep a new subject in its own folder rather than the project root.
3. Build the model with Blender 5.2 in background mode. Read [references/blender52.md](references/blender52.md) before writing that script. Match the photos. Save `<subject>/<name>.blend`.
4. Render with the skill script, not a new camera script:

```text
blender --background --python <skill>/scripts/render_angles.py -- --blend <name>.blend --out <subject>/renders --front -Y --detail-z 0.62
```

`--front` is the outside direction of the front face (`-Y`, `+Y`, `-X`, `+X`). `--detail-z` is the height fraction of the close-up, 0 at the base and 1 at the top. Point it at the clock, face, or other primary feature.

5. Open all ten PNGs. If one crops the subject or misses the named feature, change only that camera in the blend and re-render that file. The shared renderer already frames from the subject bounds; a second full pass is for a wrong `--front` or a bounds error, not for taste.

## Bounds

The renderer ignores flat objects named like ground, plaza, paving, or floor, and other thin slabs wider than 12 m. Name the ground that way, or the ten cameras will frame the plaza instead of the subject.
