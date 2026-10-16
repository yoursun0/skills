# Reusable production records

Use these fields when creating or repairing planning and evidence files. Adapt the file structure to the project; the invariants matter more than the exact schema. Times are seconds on the complete delivery timeline unless explicitly labeled otherwise.

## Reference evidence

In `REFERENCES.md`, record each source's URL/title, accessed range, actual review method, and limitations. Use rows with:

| Field | Purpose |
|---|---|
| Timestamp/range | A concrete, reproducible location, including supplied timestamps. |
| Evidence | Still, ordered temporal samples, continuous audiovisual observation, or inference. |
| Observation | What is actually visible or audible under that method. |
| Effectiveness | Why composition, hierarchy, motion, or pacing works. |
| Transfer | A craft principle useful for this topic, independent of source branding or characters. |

## Audio and text timing

`audiomap.json` should describe:

- Source path/hash, decoded duration, analysis method, and container-duration difference when relevant.
- BPM/beat positions with confidence; half-time/double-time interpretation if useful.
- Sections with IDs, start/end, musical character, energy, and pacing implications.
- Important events with time, evidence/method, and confidence.
- Location of authoritative text and phrase/word timing data, if applicable.

Phrase records should have an ID, exact authoritative text, section/repeat identity, phonetic or speech start/end, chosen display start/end, timing method, and uncertainty/confidence. Word records are optional and must retain their relationship to the authoritative phrase. Keep ASR guesses separate from displayed text. Re-align changed phrases after a text revision; preserve useful earlier evidence under historical labels.

Validate that all intended recording sections are represented, shot/section intervals cover the full duration without accidental gaps, text spans stay within their intended range, and displayed phrases match the authority. A display lead for readability is a design choice, not a measured vocal onset.

## Design and storyboard

`DESIGN.md`: canvas, typography roles, palette/materials, asset/character benchmark, layout families, lighting/depth, camera rules, semantic motion families, quieter passages, and timing constraints.

Each `STORYBOARD.md` shot records:

| Field | Required decision |
|---|---|
| ID and interval | Start/end and section identity. |
| Focal point | What the viewer notices first. |
| Exact copy and treatment | Position, scale, hierarchy, interaction, readable hold. |
| Action/transformation | Origin, action, consequence, or intentional stillness. |
| Soundtrack cue | Vocal, beat, phrase, musical change, or authored cue. |
| Framing/camera | Wide/close/object/type view and motivated movement. |
| Transition | What connects this shot to the next and why. |

## Asset provenance

Record filename, source/provider/model when relevant, prompt or license, intended role, processing steps, selected/rejected status, and QA results. Keep credentials and signed download links out of shared provenance. Package local accepted assets so future editing does not require generation access. Historical candidates may be kept if clearly distinguished from mounted assets.

## Review and revision evidence

For each concern record the cue, actual encoded evidence, finding, disposition/change, and verification after the change. Include enough detail to distinguish a detected defect from an intentional treatment.

Retain exact extraction times separately from rounded filenames or sheet labels. Document how many scenes, cuts, action windows, and full-resolution details were inspected. Record whether audio received listening review or only model/signal analysis. Link review evidence to the accepted candidate's hash so an older prototype does not accidentally certify a newer render.

## Final verification record

`VERIFICATION.md` and optional machine-readable JSON should include final file paths/hash/size; codec, dimensions, frame rate/count, video/audio durations; full-decode result; source coverage; intentional mix changes; CLI version/check results/coverage; visual-review coverage; archive validation; and specific limitations. Record failed attempts separately from successful checks.
