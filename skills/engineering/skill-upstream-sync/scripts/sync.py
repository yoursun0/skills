#!/usr/bin/env python3
"""Fetch unmodified external agent skills from public GitHub into .agents/skills.

Helic-authored tool. Does not republish third-party skill bodies into yoursun0/skills.
Python 3.10+ stdlib + urllib; optional `gh` for auth token.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT = "yoursun0-skill-upstream-sync/1.0"
GITHUB_API = "https://api.github.com"


# ---------------------------------------------------------------------------
# Minimal YAML subset (enough for this manifest schema; no PyYAML required)
# ---------------------------------------------------------------------------


def _parse_scalar(raw: str) -> Any:
    s = raw.strip()
    if not s or s == "null" or s == "~":
        return None
    if s in ("true", "True", "TRUE"):
        return True
    if s in ("false", "False", "FALSE"):
        return False
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


def load_simple_yaml(text: str) -> Any:
    """Parse a restricted YAML subset: mappings, lists, scalars, # comments."""
    lines = text.splitlines()
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    def current_container() -> Any:
        return stack[-1][1]

    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        # strip inline comment outside quotes (simple)
        stripped = raw.split("#", 1)[0].rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        content = stripped.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        container = current_container()

        if content.startswith("- "):
            item_raw = content[2:].strip()
            if not isinstance(container, list):
                raise ValueError(f"list item at unexpected place: {content}")
            if ":" in item_raw and not item_raw.startswith("{"):
                key, _, rest = item_raw.partition(":")
                key = key.strip()
                rest = rest.strip()
                obj: dict[str, Any] = {}
                container.append(obj)
                stack.append((indent, obj))
                if rest:
                    obj[key] = _parse_scalar(rest)
                else:
                    # peek: empty value → nest
                    obj[key] = None
                    # will be replaced if next lines nest under key — handle via next key under this obj
                    # For `key:` with nested block, set to {} or [] based on next line
                    # Defer: store marker
                    pass
                # If rest empty, prepare nested for this key
                if not rest:
                    # Look ahead to decide list vs map
                    nested: Any = {}
                    obj[key] = nested
                    stack.append((indent + 2, nested))  # soft guess; real indent fixes on next line
                    # Fix: don't push fake indent — instead leave key None and let next lines
                    # Actually simpler approach below for mapping keys
                    stack.pop()
                    obj[key] = {}
                    stack.append((indent, obj))
                    # We'll handle nested keys with indent > list item indent under obj
                    # Reset: obj is on stack at list-item indent
                    while stack and stack[-1][1] is not obj:
                        stack.pop()
                    if not stack or stack[-1][1] is not obj:
                        stack.append((indent, obj))
            else:
                container.append(_parse_scalar(item_raw))
            continue

        if ":" in content:
            key, _, rest = content.partition(":")
            key = key.strip()
            rest = rest.strip()
            if not isinstance(container, dict):
                # promote: if we incorrectly have list context, error
                raise ValueError(f"mapping key under non-dict: {content}")
            if rest:
                container[key] = _parse_scalar(rest)
            else:
                # nested — peek next non-empty line
                nested_indent = None
                j = i
                while j < len(lines):
                    peek = lines[j].split("#", 1)[0].rstrip()
                    if peek.strip():
                        nested_indent = len(peek) - len(peek.lstrip(" "))
                        break
                    j += 1
                if nested_indent is not None and nested_indent > indent:
                    peek_content = lines[j].split("#", 1)[0].strip()
                    child: Any = [] if peek_content.startswith("- ") else {}
                else:
                    child = {}
                container[key] = child
                stack.append((indent, child))
            continue

        raise ValueError(f"unparsed YAML line: {raw}")

    return root


def load_manifest(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(text)
        except ImportError:
            data = load_simple_yaml(text)
    if not isinstance(data, dict):
        raise SystemExit(f"manifest root must be a mapping: {path}")
    return data


# ---------------------------------------------------------------------------
# Paths / auth
# ---------------------------------------------------------------------------


def default_dest() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("USERPROFILE", str(Path.home())))
    else:
        base = Path.home()
    return base / ".agents" / "skills"


def discover_manifest(explicit: Path | None) -> Path:
    if explicit is not None:
        if not explicit.is_file():
            raise SystemExit(f"manifest not found: {explicit}")
        return explicit
    env = os.environ.get("AGENT_SKILLS_UPSTREAMS", "").strip()
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.append(Path.cwd() / "upstreams.yml")
    candidates.append(Path.home() / ".config" / "agent-skills" / "upstreams.yml")
    if os.name == "nt":
        up = os.environ.get("USERPROFILE")
        if up:
            candidates.append(Path(up) / ".config" / "agent-skills" / "upstreams.yml")
    for c in candidates:
        if c.is_file():
            return c
    raise SystemExit(
        "No upstreams manifest found. Tried AGENT_SKILLS_UPSTREAMS, ./upstreams.yml, "
        "~/.config/agent-skills/upstreams.yml. Pass --manifest PATH."
    )


def github_token() -> str | None:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    try:
        out = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def api_request(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            if resp.headers.get_content_type() == "application/json" or body[:1] in (b"{", b"["):
                return json.loads(body.decode("utf-8"))
            return body
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"HTTP {e.code} for {url}: {err_body}") from e


def short_sha(sha: str | None) -> str:
    if not sha:
        return "-"
    return sha[:7]


# ---------------------------------------------------------------------------
# GitHub fetch
# ---------------------------------------------------------------------------


def tip_sha_for_path(repo: str, path: str, token: str | None) -> str:
    """Latest commit SHA that touched path on the default branch."""
    q = urllib.parse.urlencode({"path": path, "per_page": "1"})
    url = f"{GITHUB_API}/repos/{repo}/commits?{q}"
    data = api_request(url, token)
    if not isinstance(data, list) or not data:
        # fallback: default branch tip
        meta = api_request(f"{GITHUB_API}/repos/{repo}", token)
        default = meta.get("default_branch") or "main"
        ref = api_request(f"{GITHUB_API}/repos/{repo}/commits/{urllib.parse.quote(default)}", token)
        return ref["sha"]
    return data[0]["sha"]


def list_remote_files(repo: str, path: str, ref: str, token: str | None) -> list[tuple[str, str]]:
    """Return list of (relative_path, download_url) for files under path at ref."""
    path = path.strip("/")
    results: list[tuple[str, str]] = []

    def walk(api_path: str) -> None:
        url = f"{GITHUB_API}/repos/{repo}/contents/{urllib.parse.quote(api_path)}?ref={urllib.parse.quote(ref)}"
        data = api_request(url, token)
        if isinstance(data, dict) and data.get("type") == "file":
            rel = data["path"]
            if rel.startswith(path + "/"):
                rel = rel[len(path) + 1 :]
            elif rel == path:
                rel = Path(rel).name
            download = data.get("download_url")
            if not download:
                # raw fallback
                download = f"https://raw.githubusercontent.com/{repo}/{ref}/{data['path']}"
            results.append((rel.replace("\\", "/"), download))
            return
        if not isinstance(data, list):
            raise RuntimeError(f"unexpected contents payload for {api_path}")
        for entry in data:
            if entry.get("type") == "dir":
                walk(entry["path"])
            elif entry.get("type") == "file":
                full = entry["path"]
                if full.startswith(path + "/"):
                    rel = full[len(path) + 1 :]
                else:
                    rel = Path(full).name
                download = entry.get("download_url") or (
                    f"https://raw.githubusercontent.com/{repo}/{ref}/{full}"
                )
                results.append((rel.replace("\\", "/"), download))

    walk(path)
    results.sort(key=lambda x: x[0])
    return results


def download_bytes(url: str, token: str | None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    # raw.githubusercontent.com usually needs no auth; API blob URLs might
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def content_hash(files: dict[str, bytes]) -> str:
    h = hashlib.sha256()
    for rel in sorted(files.keys()):
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(files[rel])
        h.update(b"\0")
    return h.hexdigest()


def hash_installed(dest_dir: Path) -> str | None:
    if not dest_dir.is_dir():
        return None
    files: dict[str, bytes] = {}
    for p in sorted(dest_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(dest_dir)).replace("\\", "/")
            files[rel] = p.read_bytes()
    if not files:
        return None
    return content_hash(files)


def fetch_files(repo: str, path: str, ref: str, token: str | None) -> dict[str, bytes]:
    listing = list_remote_files(repo, path, ref, token)
    if not listing:
        raise RuntimeError(f"no files under {repo}:{path}@{short_sha(ref)}")
    out: dict[str, bytes] = {}
    for rel, url in listing:
        out[rel] = download_bytes(url, token)
    return out


def atomic_replace(dest: Path, files: dict[str, bytes], dry_run: bool) -> None:
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(dest.parent)) as tmp:
        staging = Path(tmp) / "staging"
        staging.mkdir()
        for rel, data in files.items():
            target = staging / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # swap: remove old, rename staging into place
        final_staging = dest.parent / f".{dest.name}.sync-new"
        if final_staging.exists():
            shutil.rmtree(final_staging)
        shutil.copytree(staging, final_staging)
        old = dest.parent / f".{dest.name}.sync-old"
        if old.exists():
            shutil.rmtree(old)
        if dest.exists():
            dest.rename(old)
        final_staging.rename(dest)
        if old.exists():
            shutil.rmtree(old)


def sha_matches(pin: str, tip: str) -> bool:
    pin = pin.strip().lower()
    tip = tip.strip().lower()
    if len(pin) < 7:
        return False
    return tip.startswith(pin) or pin.startswith(tip[: len(pin)])


# ---------------------------------------------------------------------------
# Sync one upstream
# ---------------------------------------------------------------------------


def sync_one(
    entry: dict[str, Any],
    dest_root: Path,
    token: str | None,
    dry_run: bool,
) -> int:
    """Print one status line; return 0 ok, 1 soft error line already printed."""
    uid = entry.get("id") or entry.get("install_as") or "?"
    try:
        repo = entry["repo"]
        path = entry["path"]
        install_as = entry["install_as"]
        lane = (entry.get("lane") or "tip").strip().lower()
        pin_sha = entry.get("pin_sha")
        if pin_sha in ("", "null"):
            pin_sha = None

        tip = tip_sha_for_path(repo, path, token)
        dest_dir = dest_root / install_as

        if lane == "pin":
            if not pin_sha or not isinstance(pin_sha, str) or pin_sha.startswith("REPLACE"):
                print(f"ERROR {uid} pin_sha missing or placeholder tip={short_sha(tip)}")
                return 1
            if not sha_matches(pin_sha, tip):
                print(f"PIN_STALE {uid} {short_sha(pin_sha)}→{short_sha(tip)}")
                return 0
            print(f"UNCHANGED {uid} {short_sha(tip)}")
            return 0

        if lane != "tip":
            print(f"ERROR {uid} unknown lane={lane!r}")
            return 1

        files = fetch_files(repo, path, tip, token)
        remote_hash = content_hash(files)
        local_hash = hash_installed(dest_dir)
        if local_hash == remote_hash:
            print(f"UNCHANGED {uid} {short_sha(tip)}")
            return 0
        atomic_replace(dest_dir, files, dry_run=dry_run)
        suffix = " (dry-run)" if dry_run else ""
        print(f"UPDATED {uid} {short_sha(tip)}{suffix}")
        return 0
    except Exception as e:  # noqa: BLE001 — per-skill isolation
        print(f"ERROR {uid} {e}")
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync unmodified upstream agent skills")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and compare; do not write")
    parser.add_argument("--manifest", type=Path, help="Path to upstreams.yml / .json")
    parser.add_argument("--dest", type=Path, help="Agents skills directory")
    args = parser.parse_args(argv)

    try:
        manifest_path = discover_manifest(args.manifest)
        data = load_manifest(manifest_path)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"ERROR manifest {e}", file=sys.stderr)
        return 1

    dest = args.dest
    if dest is None:
        raw = data.get("dest")
        dest = Path(raw).expanduser() if raw else default_dest()
    else:
        dest = dest.expanduser()

    upstreams = data.get("upstreams") or []
    if not isinstance(upstreams, list) or not upstreams:
        print("ERROR no upstreams in manifest", file=sys.stderr)
        return 1

    token = github_token()
    errors = 0
    for entry in upstreams:
        if not isinstance(entry, dict):
            print(f"ERROR invalid-entry {entry!r}")
            errors += 1
            continue
        errors += sync_one(entry, dest, token, dry_run=args.dry_run)

    # Completed run exits 0 even when individual skills printed ERROR (task contract).
    # Hard manifest / fatal failures already returned 1 above.
    _ = errors
    return 0


if __name__ == "__main__":
    # Hard failures (bad manifest path) exit non-zero via SystemExit above.
    # Completed runs exit 0 even when individual skills printed ERROR.
    try:
        raise SystemExit(main())
    except SystemExit as e:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"ERROR fatal {e}", file=sys.stderr)
        raise SystemExit(1) from e
