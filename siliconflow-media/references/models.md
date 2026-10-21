# Documented models and constraints

Documentation checked 2026-10-21. These are schema/documentation checks, not proof of account access or live quality. Current prices and provider-defined video duration are unverified; obtain a current quote or explicitly disclose unknown cost before paid tests.

## Images

- Implemented: `Tongyi-MAI/Z-Image-Turbo` with `POST /images/generations`; response `images[0].url` is downloaded immediately to PNG. URLs expire after one hour.
- CLI default: `1024x1024`. Z-Image's schema accepts a resolution string; its recommended sizes are `512x512`, `768x1024`, `1024x576`, `576x1024`. Those and the user-preferred square size are the runner's supported choices. No batch, image editing, or unsupported model-specific options are exposed.
- [Image API, Z-Image schema](https://docs.siliconflow.com/en/api-reference/images/images-generations.md).

## Video

- Text input: `Wan-AI/Wan2.2-T2V-A14B`.
- Image input: `Wan-AI/Wan2.2-I2V-A14B`, plus text prompt and local PNG/JPEG. The runner transmits a base64 data URI; its 20 MiB cap is a local protection, not a documented provider maximum.
- `POST /video/submit`: `model`, `prompt`, `image_size`, and for I2V `image`. Response `requestId` must be saved before polling.
- `POST /video/status`: body `{"requestId":"..."}`. Statuses: `InQueue`, `InProgress`, `Succeed`, `Failed`. Success URL: `results.videos[0].url`.
- Both modes expose sizes `1280x720`, `720x1280`, `960x960`. I2V output follows source aspect ratio per the capability guide; prepare the source accordingly.
- The current schema exposes no duration parameter. Do not promise a chosen duration or invent an argument. Submit docs mention ten-minute result retention, status docs one-hour URL expiry: download promptly and resume promptly.
- Job files contain model, absolute output path, job ID, status, and download completion, without prompts, source images, credentials, or signed URLs. Keep them in the chosen project. A project moved to another directory requires updating its saved output path before resumption.
- [Submit API](https://docs.siliconflow.com/en/api-reference/videos/videos_submit.md), [status API](https://docs.siliconflow.com/en/api-reference/videos/get_videos_status.md), [video capabilities](https://docs.siliconflow.com/en/userguide/capabilities/video.md).

## Speech

- Default: `FunAudioLLM/CosyVoice2-0.5B`; alternative: `fishaudio/fish-speech-1.5`.
- `POST /audio/speech`: `model`, `input`, model-prefixed `voice`, `response_format`, `stream:false`. Returns binary audio, not a media URL.
- Presets for both models: `alex`, `anna`, `bella`, `benjamin`, `charles`, `claire`, `david`, `diana`. The runner builds the full ID, e.g. `FunAudioLLM/CosyVoice2-0.5B:anna`.
- `--format`: `mp3` (default), `wav`, `opus`, `pcm`; the output extension must match. PCM is raw audio and may need a player configured with the provider's sample-rate/channel details; use MP3/WAV for ordinary playback.
- `--language auto`: sends the supplied text unchanged. `--language cantonese`: CosyVoice2 only, prepends `请用广东话自然地说。<|endofprompt|>`. The capability guide explicitly lists Cantonese for CosyVoice2. A particular preset's Cantonese quality remains pending live evaluation; `cn_cantonese` is not a documented voice ID.
- Input length: 1–128000 characters including added instruction. Fish Speech documentation says balance payment is required. Music, SFX, transcription, custom references and cloning are unimplemented.
- [Speech API](https://docs.siliconflow.com/en/api-reference/audio/create-speech.md), [language/dialect support and instruction syntax](https://docs.siliconflow.com/en/userguide/capabilities/text-to-speech.md).

## Integration ownership

The [official SiliconCloud CLI](https://github.com/siliconflow/siliconcloud-cli) documents upload/file/model management, not these generation endpoints. The standalone standard-library runner needs no new MCP registration, service, or reasoning-provider setting.

For installation, use one canonical skill directory. Inspect CC Switch's management paths before linking/promoting it. [Codex skills](https://developers.openai.com/codex/skills/) support explicit invocation and automatic selection by name/description. Discovery in a fresh chat and provider switch/back are separate verification steps, not implied by offline runner tests.
