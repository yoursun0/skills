# Verification and handoff

Read before final rendering or delivery. Technical correctness and artistic quality are separate gates.

## Technical gate

Use installed HyperFrames documentation and `--help` for exact flags. Typical command shapes, when supported by the project's Bun setup:

```powershell
bun run check --samples 25 --snapshots --json
bun run render --fps 30 --quality delivery --output renders/candidate.mp4
ffprobe -v error -show_streams -show_format -of json renders/candidate.mp4
ffmpeg -v error -i renders/candidate.mp4 -f null -
```

Replace 30 with the requested frame rate; use the project's actual scripts. Run the build first if compositions are generated. Inspect structured check results, not only process exit codes. `browserSkipped: true` or zero completed browser samples cannot certify runtime/layout quality. Read findings and captured pixels; resolve blocking defects. Add meaningful motion assertions for important presence, order, attachment, or liveness when supported. Coarse sampling cannot prove exact frame timing.

Record CLI versions and actual checks/samples. If a broad audit times out, retain the failure and use supported explicit-time or segmented checks to obtain useful coverage, supplemented by encoded visual inspection. Do not silently remove assertions or report a skipped audit as passing. Usage/account status reported as unknown stays unknown; a local render's success is separate evidence.

Probe the encoded output for actual dimensions, frame rate, frame count, video/audio codecs, sample rate, channels, durations, and start times. Verify the complete file decodes. A successful mux or nonempty file is insufficient.

For uncut music at constant frame rate, the expected frame count normally covers decoded source duration: `ceil(duration_seconds * fps)`. Container framing, audio padding, and encoder behavior require interpretation; do not trim the music to make a rounded container duration match. Measure the source and output, and explain a justified sub-frame picture extension.

Where source preservation matters, compare decoded PCM at matching times without optimizing away an offset or speed change. Check early, middle, and late windows to expose drift. AAC will change samples; correlation/gain measurements support alignment and approximate level, not bit identity or listening quality. Exclude or model intentional added effects; use different acceptance criteria for an authorized remix.

## Visual and audiovisual gate

Review the actual candidate encode:

1. A representative view of every shot and every sub-composition mount.
2. Before/after states across every shot boundary, plus intermediate states for longer transitions.
3. Ordered frames or playback through each important action, type reveal, camera move, and dramatic event.
4. Full-resolution details where anatomy, alpha, thin lines, object contact, text edges, or depth matter.
5. Opening, final resolution, and final encoded frame.

Choose temporal density to reveal the action. Check adjacent frames around sudden cues; retain the exact seek values. A rounded timestamp can accidentally select the next frame. For text, inspect entrance, readable hold, and exit. For a carried object, follow its origin, contact, route, and departure. For continuity, check character identity, expressions, direction, and emotional consequence.

If continuous audiovisual playback is available, use it to assess timing and perceived pacing. If it is unavailable, disclose that review used ordered frames and the actual audio-analysis methods. Do not attribute hearing or continuous watching to frame inspection. Likewise, a static styleframe cannot certify an entrance or transition.

Revise specific weaknesses before final acceptance. Generate a new candidate when picture changes; recheck changed intervals and any affected transitions. Previous evidence remains useful only for unchanged content.

## Contact sheet and editable package

Extract the contact sheet from the accepted encoded video. Choose meaningful held moments: a geometric shot midpoint may fall between phrases, after an actor exits, or during a low-opacity transition. Include timestamps and readable labels, then inspect the sheet itself. For long films, use multiple sheets or a useful key-scene overview with a separate exhaustive review index.

Keep editable source, timing data, accepted local assets, font licenses, build/render instructions, design/storyboard, reference study, and verification evidence together. Exclude secrets, dependency folders, caches, and unrelated downloads. If creating a ZIP, validate its members and integrity. A project that needs a generation API merely to render prepared local assets is not a portable handoff.

Promote the verified candidate with a safe file replacement and preserve the previous delivery. Reconfirm the final hash matches the reviewed candidate. Update reports and the editable audio/video settings to match the promoted file; avoid leaving old revision metrics in the final report.

Final response: link the video, contact sheet, editable project, and verification report; state output properties and material limitations concisely. The user's requested scope determines whether local delivery is the endpoint. Publication is a separate operation requiring its own authorization.
