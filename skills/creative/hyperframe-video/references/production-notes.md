# Assets, choreography, and implementation lessons

Read this when generating people/animals, building kinetic type, or implementing the film. These are production lessons, not a requirement to reuse the original film's style or story.

## Establish an asset benchmark

For recurring people, choose an accepted image as the benchmark before generating many poses. Record identity markers (face/hair, clothes, proportions), rendering style, line quality, texture, and shading. A cartoon cast needs other humans rendered in the same visual family unless a deliberate contrast is part of the brief. Flexible scenery does not excuse an accidentally photographic supporting actor.

Use clean transparent raster cutouts for complex generated characters, or reliable supplied/rigged assets. SVG is useful for environments, props, paths, masks, and text. Generated SVG anatomy proved fragile in this production; replacing it with reviewed PNG poses removed extra-limb problems. Raster generation still requires anatomy and object QA.

Generate purposeful poses: neutral, running, reaching, surprise, embrace, grief, or topic-specific actions. Inspect full bodies, hands, faces, arm counts, feet, object contact, head proportions, and silhouettes before mounting an asset. Reject unsuitable generations instead of assuming a prompt enforced anatomy or style. Retain selected/rejected provenance with reasons.

Prefer the configured image provider. This workspace used SiliconFlow `Tongyi-MAI/Z-Image-Turbo`, base `https://api.siliconflow.com/v1`, through a configured image-generation integration. For direct API use, read credentials only from the local `SILICONFLOW_API_KEY` environment variable. Provider access, models, and billing authorization must be verified in the destination environment. A configured MCP may work when a shell environment variable is absent. Report the actual access blocker if neither route is available; do not ask for secrets in chat or silently change providers.

If direct alpha output is unavailable, generate against a uniform chroma background and remove it deterministically using the available transparent-assets/background-removal workflow. Inspect alpha corners, thin edges, holes, colour spill, and semi-transparent pixels over both light and dark backgrounds. Inspect the full subject too: transparent corners alone cannot establish a clean cutout. Freeze accepted assets locally; rendering should not call a generation API.

## Make action physically understandable

Attach a carried object to its actor's transform hierarchy. Animate the actor/hand/object together after contact; preserve the visible origin and exit. Where the hand belongs to a full-body PNG, align the prop against the actual painted palm in the encoded frame.

Facing direction and travel direction must agree for normal running. Isolate flips on an inner wrapper when GSAP owns the outer transform; otherwise an animated transform can override a CSS flip. Inspect the encoded direction, not just transform values.

Use distinct poses, reactions, paths, contact, and consequence. Whole-body translation with a running pose communicates travel but is not an articulated gait. If the brief needs convincing continuous character animation, use compatible pose cycles, sprite frames, or a rig and review the cycle. Describe the implemented technique honestly.

For a sustained action spanning several shots, evaluate it from a shared absolute-time origin so cuts do not restart the action. A sudden event should affect the relevant image, expression, motion, lighting, and sound coherently. Allow emotional consequences to occupy screen time.

## Kinetic type and camera

Use a few distinct semantic treatments rather than an identical entrance on every word. Useful families include scale/rotation impact, directional travel, masked scrolling, physical deformation, paired phrases meeting, and restrained reveals. Repeated copies in a word reel are a mechanism; the displayed lyric remains exact.

Separate entrance, readable hold, transformation, and exit. Prioritize the spoken/sung phrase over mechanical word animation where timing is uncertain. Judge legibility through motion, not only at the final pose.

Animate an inner camera/world wrapper rather than the framework's timed clip. Keep lyrics in screen space when a camera move would otherwise push them through objects or off-screen. Assign a purpose to a push-in, pull-back, or pan: a reaction, reveal, route, or change in scale. Compose for the moving frame, including foreground layers.

A hook can retain a visual signature while changing colour, crop, action, or meaning. A quieter section can reduce type size, movement, light, and density while still showing a story change. Avoid using the same neutral pose and layout as a substitute for a sequence.

## Deterministic HyperFrames authoring

Follow the installed core contract for timed elements, tracks, sub-compositions, registration, and framework-owned media. Search the registry before hand-building a named mechanism. Adapt useful mechanisms to the project's typography and timing rather than mounting demo copy or imposing a preset's BPM/frame rate.

Use paused, seekable timelines and finite motion or pure functions of composition time. Resolve random variation with a fixed seed. Keep assets local, fonts explicit, and asynchronous loading complete before declaring readiness. Wall-clock timers and runtime network generation cannot define render state reliably.

Use canonical timing data to generate the compositions and storyboard where practical. Keep historical experiments outside the normal build path and clearly label scripts that overwrite source. The editable rebuild must reproduce the delivered treatment, including final audio gains.

## Diagnose the observed output

Inspect reported layout problems at the reported time. Fix unintended collisions. Mark deliberate layering narrowly on the participating element so unrelated errors remain visible. A transient entrance can differ from a held readability defect.

The production used HyperFrames 0.8.162: one expanded transition audit exceeded its fixed 120-second browser deadline. A retry using explicit cue times completed with the motion and contrast audits. Preserve failed reports, record the changed coverage, and supplement with decoded transition sequences; a timeout is not a clean browser pass. Recheck behavior in the installed version rather than assuming the same deadline or flags.

Keyframes diagnostics returned empty trajectory arrays for this film's nested templates. An onion image showed markers without reliable actor trails. Such diagnostics cannot establish correct motion; decoded sequences established facing/travel, attachment, event timing, and fades.

For an audio-only balance change after picture approval, a local stream-copy remux may avoid recapturing unchanged picture. Verify that the video stream is unchanged, verify the new mix and duration, update editable audio settings, and review any changed sound cue. A remux is not grounds to claim a fresh picture render.
