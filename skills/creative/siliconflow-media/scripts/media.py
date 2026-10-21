# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Provider-independent SiliconFlow media CLI. Stdout is always concise JSON."""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.siliconflow.com/v1"
IMAGE_MODEL = "Tongyi-MAI/Z-Image-Turbo"
SPEECH_MODELS = ("FunAudioLLM/CosyVoice2-0.5B", "fishaudio/fish-speech-1.5")
VIDEO_MODELS = ("Wan-AI/Wan2.2-T2V-A14B", "Wan-AI/Wan2.2-I2V-A14B")
VOICES = ("alex", "anna", "bella", "benjamin", "charles", "claire", "david", "diana")
SETUP = "Run provision-key.ps1 beside media.py in an interactive PowerShell, then credential-check."


class MediaError(Exception):
    def __init__(self, category, message, **metadata):
        super().__init__(message)
        self.result = {"ok": False, "category": category, "message": message, **metadata}


def credential_path():
    if not os.environ.get("LOCALAPPDATA"):
        raise MediaError("credentials", "Windows LOCALAPPDATA is unavailable. " + SETUP)
    return Path(os.environ["LOCALAPPDATA"]) / "SiliconFlowMedia" / "api-key.dpapi"


def powershell_env():
    # Codex can run under bundled PowerShell 7. Its inherited modules conflict
    # with Windows PowerShell 5.1's built-in security types.
    child = os.environ.copy()
    child["PSModulePath"] = str(Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32/WindowsPowerShell/v1.0/Modules")
    return child


def load_key():
    # An explicitly supplied process variable is supported; never inspect provider auth.
    value = os.environ.get("SILICONFLOW_API_KEY", "").strip()
    if value:
        return value
    path = credential_path()
    if not path.is_file():
        raise MediaError("credentials", "SiliconFlow credential is missing. " + SETUP)
    if sys.platform != "win32":
        raise MediaError("credentials", "DPAPI requires the provisioning Windows user and computer.")
    script = r"""
$ErrorActionPreference = 'Stop'
$credentialFile = Join-Path $env:LOCALAPPDATA 'SiliconFlowMedia\api-key.dpapi'
$secret = (Get-Content -LiteralPath $credentialFile -Raw).Trim() | ConvertTo-SecureString
$buffer = [IntPtr]::Zero
try {
    $buffer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    [Console]::Out.Write([Runtime.InteropServices.Marshal]::PtrToStringBSTR($buffer))
} finally {
    if ($buffer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($buffer) }
    if ($secret) { $secret.Dispose() }
}
"""
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW,
            env=powershell_env(),
        )
    except (OSError, subprocess.TimeoutExpired):
        raise MediaError("credentials", "Credential helper failed. " + SETUP) from None
    if result.returncode or not result.stdout.strip():
        raise MediaError("credentials", "DPAPI decryption failed for this Windows user/computer. " + SETUP)
    # Only our process receives the plaintext. Never emit the child process output.
    os.environ["SILICONFLOW_API_KEY"] = result.stdout.decode("utf-8").strip()
    return os.environ["SILICONFLOW_API_KEY"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HttpsRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        require_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def require_https(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise MediaError("download", "Media URL must use HTTPS without embedded credentials.")


def http_error(code, generation=False):
    if code in (401, 403):
        return MediaError("authentication", "SiliconFlow rejected access. Check the key and model permissions; stop retries.", http_status=code)
    if code in (400, 404, 422):
        return MediaError("validation_model", "SiliconFlow rejected the input or model. Recheck the current model schema.", http_status=code)
    if code == 429:
        return MediaError("rate_limit", "Rate limited. Wait before an explicit retry; generation was not automatically resubmitted.", http_status=code)
    return MediaError("service", "SiliconFlow service request failed." + (" Generation may have been accepted; do not blindly resubmit." if generation else ""), http_status=code)


class Client:
    def __init__(self, key):
        self.key = key
        self.api_opener = urllib.request.build_opener(NoRedirect())
        self.download_opener = urllib.request.build_opener(HttpsRedirect())

    def api(self, endpoint, payload, binary=False, timeout=120):
        request = urllib.request.Request(
            BASE_URL + endpoint, json.dumps(payload).encode("utf-8"),
            {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"}, method="POST",
        )
        generation = endpoint != "/video/status"
        # Generation POSTs are attempted exactly once, including timeouts.
        try:
            with self.api_opener.open(request, timeout=timeout) as response:
                body = response.read()
                if binary:
                    if "json" in response.headers.get("Content-Type", "").lower():
                        raise MediaError("response", "Expected binary audio; received JSON. No resubmission was made.")
                    return body
                result = json.loads(body)
                if not isinstance(result, dict):
                    raise MediaError("response", "Expected a JSON object; no automatic generation retry.")
                return result
        except urllib.error.HTTPError as exc:
            # Never include a response body, request repr, key, or signed URL in errors.
            error = http_error(exc.code, generation)
            retry_after = exc.headers.get("Retry-After", "")
            if retry_after.isdigit():
                error.result["retry_after_seconds"] = int(retry_after)
            raise error from None
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            raise MediaError("network", "Request failed or timed out." + (" Acceptance is unknown; do not automatically resubmit generation." if generation else " Resume the saved video job.")) from None
        except (ValueError, UnicodeError):
            raise MediaError("response", "Malformed SiliconFlow response; no automatic generation retry.") from None

    def download(self, url, output, overwrite=False):
        require_https(url)
        # Separate opener and request: no API Authorization is present, even on redirects.
        try:
            with self.download_opener.open(urllib.request.Request(url), timeout=120) as response:
                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" in content_type or "application/json" in content_type:
                    raise MediaError("download", "Media URL returned a document instead of media.")
                return save_stream(output, response, overwrite)
        except (urllib.error.URLError, OSError, TimeoutError):
            raise MediaError("download", "Media download failed. Preserve saved state and retry its download, not generation.") from None


def destination(project, value, overwrite=False):
    root = Path(project).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise MediaError("validation", "--project must be an existing directory.")
    path = Path(value).expanduser()
    path = (path if path.is_absolute() else root / path).resolve()
    if not path.is_relative_to(root) or path == root:
        raise MediaError("validation", "Output and job files must stay inside --project.")
    if path.is_dir() or (path.exists() and not overwrite):
        raise MediaError("collision", "Destination exists; choose a new path or explicitly use --overwrite.", local_path=str(path))
    parent = path.parent
    while not parent.exists():
        parent = parent.parent
    if not parent.is_dir() or not os.access(parent, os.W_OK):
        raise MediaError("validation", "Destination parent is not writable.")
    return path


def save_stream(path, stream, overwrite=False):
    import shutil
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
            temp_path = Path(temp.name)
            shutil.copyfileobj(stream, temp)
        if not temp_path.stat().st_size:
            raise MediaError("response", "Empty media response; output was not saved.")
        if overwrite:
            os.replace(temp_path, path)
        else:
            # Hard-link promotion is atomic and refuses a file created concurrently.
            os.link(temp_path, path)
        return str(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def save_bytes(path, value, overwrite=False):
    import io
    return save_stream(path, io.BytesIO(value), overwrite)


def save_state(path, state, overwrite=False):
    save_bytes(path, json.dumps(state, indent=2).encode("utf-8"), overwrite)


def read_text(path, root):
    path = Path(path)
    path = path if path.is_absolute() else Path(root) / path
    value = path.read_text(encoding="utf-8-sig").strip()
    if not value:
        raise MediaError("validation", "Input text file is empty.")
    return value


def metadata(modality, model, output, **kwargs):
    return {"ok": True, "modality": modality, "model": model, "local_path": str(output), **kwargs}


def media_url(response, video=False):
    try:
        items = response["results"]["videos"] if video else response["images"]
        url = items[0]["url"]
        require_https(url)
        return url
    except (KeyError, IndexError, TypeError):
        raise MediaError("response", "Response has no media URL; generation will not be resubmitted.") from None


def poll(client, state, job_file, output, wait_seconds, interval, overwrite):
    deadline = time.monotonic() + wait_seconds
    while True:
        remaining = deadline - time.monotonic()
        try:
            response = client.api("/video/status", {"requestId": state["job_id"]}, timeout=max(0.1, min(60, remaining)))
        except MediaError as exc:
            remaining = deadline - time.monotonic()
            if exc.result["category"] in ("rate_limit", "service", "network") and remaining > interval:
                delay = max(interval, exc.result.get("retry_after_seconds", 0))
                if delay < remaining:
                    time.sleep(delay)
                    continue
            raise
        status = response.get("status")
        if status not in ("Succeed", "InQueue", "InProgress", "Failed"):
            raise MediaError("response", "Unknown video status; saved job can be resumed.")
        state["status"] = status
        save_state(job_file, state, True)
        if status == "Succeed":
            client.download(media_url(response, True), output, overwrite)
            state["downloaded"] = True
            save_state(job_file, state, True)
            return metadata("video", state["model"], output, job_id=state["job_id"], job_file=str(job_file))
        if status == "Failed":
            raise MediaError("generation_failed", "Video generation failed. Review the job in SiliconFlow; no replacement was submitted.")
        if time.monotonic() + interval >= deadline:
            raise MediaError("polling_timeout", "Video is still pending. Run video resume with this job file.")
        time.sleep(interval)


def execute(args, client_factory=Client, key_loader=load_key):
    if args.command == "credential-check":
        key_loader()
        return {"ok": True, "credential_available": True, "network_used": False}
    root = Path(args.project).expanduser().resolve(strict=True)
    resume = args.command == "video" and args.action == "resume"
    state = None
    if resume:
        job_file = (root / args.job_file).resolve()
        if not job_file.is_relative_to(root):
            raise MediaError("validation", "Job file must stay inside --project.")
        state = json.loads(job_file.read_text(encoding="utf-8"))
        if state.get("model") not in VIDEO_MODELS or not isinstance(state.get("job_id"), str) or not state["job_id"]:
            raise MediaError("validation", "Invalid video job file.")
        output = destination(root, state["local_path"], args.overwrite)
        if output == job_file:
            raise MediaError("validation", "Output cannot be the job file.")
        payload = {"requestId": state["job_id"]}
        endpoint, model = "/video/status", state["model"]
    else:
        output = destination(root, args.output, args.overwrite)
        text = read_text(args.text_file if args.command == "speech" else args.prompt_file, root)
        model = args.model
        payload = {"model": model}
        if args.command == "image":
            if output.suffix.lower() != ".png":
                raise MediaError("validation", "Image output must use .png.")
            payload.update(prompt=text, image_size=args.size)
            endpoint = "/images/generations"
        elif args.command == "speech":
            if output.suffix.lower() != "." + args.format:
                raise MediaError("validation", "Speech output extension must match --format.")
            if args.language == "cantonese":
                if model != SPEECH_MODELS[0]:
                    raise MediaError("validation", "Use CosyVoice2 for documented Cantonese support.")
                text = "请用广东话自然地说。<|endofprompt|>" + text
            if len(text) > 128000:
                raise MediaError("validation", "Speech input exceeds 128000 characters.")
            payload.update(input=text, voice=model + ":" + args.voice, response_format=args.format, stream=False)
            endpoint = "/audio/speech"
        else:
            if output.suffix.lower() != ".mp4":
                raise MediaError("validation", "Video output must use .mp4.")
            job_file = destination(root, args.job_file)
            if job_file == output:
                raise MediaError("validation", "Output and job files must differ.")
            payload.update(prompt=text, image_size=args.size)
            if model == VIDEO_MODELS[1]:
                if not args.image_file:
                    raise MediaError("validation", "I2V requires --image-file (PNG or JPEG).")
                image = (root / args.image_file).resolve()
                if output == image or job_file == image:
                    raise MediaError("validation", "Output/job files cannot replace the source image.")
                data = image.read_bytes()
                mime = "image/png" if data.startswith(b"\x89PNG\r\n\x1a\n") else "image/jpeg" if data.startswith(b"\xff\xd8\xff") else None
                if not mime or len(data) > 20 * 1024 * 1024:
                    raise MediaError("validation", "I2V input must be PNG/JPEG and at most 20 MiB (local runner limit).")
                payload["image"] = "data:" + mime + ";base64," + base64.b64encode(data).decode("ascii")
            elif args.image_file:
                raise MediaError("validation", "Use the I2V model with --image-file.")
            endpoint = "/video/submit"
        input_name = getattr(args, "text_file", None) or args.prompt_file
        input_path = (root / input_name).resolve()
        if output == input_path or (args.command == "video" and job_file == input_path):
            raise MediaError("validation", "Output/job files cannot replace the input text.")
    if args.dry_run:
        # Deliberately omit prompts, source images, secrets, and signed URLs.
        result = metadata(args.command, model, output, dry_run=True, network_used=False, credential_decrypted=False,
                          endpoint=BASE_URL + endpoint, request_fields=sorted(payload))
        if args.command == "video":
            result["job_file"] = str(job_file)
        return result
    client = client_factory(key_loader())
    if args.command == "speech":
        save_bytes(output, client.api(endpoint, payload, binary=True), args.overwrite)
    elif args.command == "image":
        response = client.api(endpoint, payload)
        url = media_url(response)
        try:
            client.download(url, output, args.overwrite)
        except MediaError as exc:
            # No signed URL/prompt is persisted. Do not regenerate after a download failure.
            exc.result.update(model=model, local_path=str(output), generation_completed=True)
            raise
    else:
        if not resume:
            # Reserve state before the billable POST, and preserve it on ambiguous failure.
            state = {"modality": "video", "model": model, "local_path": str(output), "status": "submission_started"}
            save_state(job_file, state)
            try:
                response = client.api(endpoint, payload)
                job_id = response.get("requestId")
                if not isinstance(job_id, str) or not job_id:
                    raise MediaError("response", "Submission returned no requestId. Acceptance is unknown; do not resubmit automatically.")
                state.update(job_id=job_id, status="submitted")
                save_state(job_file, state, True)
            except MediaError as exc:
                exc.result.update(job_file=str(job_file), **({"job_id": state["job_id"]} if "job_id" in state else {}))
                raise
            except OSError:
                raise MediaError("local_state", "Could not persist submission state; preserve this job ID and do not resubmit.",
                                 job_file=str(job_file), **({"job_id": state["job_id"]} if "job_id" in state else {})) from None
        try:
            return poll(client, state, job_file, output, args.wait_seconds, args.poll_interval, args.overwrite)
        except MediaError as exc:
            exc.result.update(job_id=state["job_id"], job_file=str(job_file), local_path=str(output))
            raise
    return metadata(args.command, model, output)


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    commands.add_parser("credential-check", help="Check local credential loading without HTTP; may decrypt DPAPI.")

    def common(p, output=True):
        p.add_argument("--project", required=True, help="Existing project root; all output/job paths resolve here.")
        if output:
            p.add_argument("--output", required=True)
        p.add_argument("--overwrite", action="store_true", help="Allow replacing output, never an existing submission job.")
        p.add_argument("--dry-run", action="store_true", help="Validate only; no decryption, writes, or network.")

    image = commands.add_parser("image", help="Generate one Z-Image-Turbo PNG.")
    common(image)
    image.add_argument("--prompt-file", required=True)
    image.add_argument("--model", choices=[IMAGE_MODEL], default=IMAGE_MODEL)
    image.add_argument("--size", choices=["512x512", "768x1024", "1024x576", "576x1024", "1024x1024"], default="1024x1024")
    speech = commands.add_parser("speech", help="Generate binary speech with a preset voice.")
    common(speech)
    speech.add_argument("--text-file", required=True)
    speech.add_argument("--model", choices=SPEECH_MODELS, default=SPEECH_MODELS[0])
    speech.add_argument("--voice", choices=VOICES, default="anna")
    speech.add_argument("--language", choices=["auto", "cantonese"], default="auto")
    speech.add_argument("--format", choices=["mp3", "wav", "opus", "pcm"], default="mp3")
    video = commands.add_parser("video", help="Submit or resume a persisted asynchronous video job.")
    actions = video.add_subparsers(dest="action", required=True)
    for name in ("submit", "resume"):
        p = actions.add_parser(name)
        common(p, name == "submit")
        p.add_argument("--job-file", required=True)
        p.add_argument("--wait-seconds", type=bounded_wait, default=600)
        p.add_argument("--poll-interval", type=bounded_interval, default=10)
        if name == "submit":
            p.add_argument("--prompt-file", required=True)
            p.add_argument("--model", choices=VIDEO_MODELS, default=VIDEO_MODELS[0])
            p.add_argument("--size", choices=["1280x720", "720x1280", "960x960"], default="1280x720")
            p.add_argument("--image-file", help="Local PNG/JPEG for the I2V model; transmitted to SiliconFlow.")
    return cli


def bounded_wait(value):
    number = int(value)
    if not 1 <= number <= 3600:
        raise argparse.ArgumentTypeError("Expected 1..3600 seconds.")
    return number


def bounded_interval(value):
    number = int(value)
    if not 1 <= number <= 60:
        raise argparse.ArgumentTypeError("Expected 1..60 seconds.")
    return number


def main(argv=None):
    try:
        result = execute(parser().parse_args(argv))
    except MediaError as exc:
        result = exc.result
    except (OSError, ValueError, KeyError, TypeError):
        result = {"ok": False, "category": "local_or_response", "message": "Invalid local input, state, filesystem operation, or response. No automatic generation retry."}
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
