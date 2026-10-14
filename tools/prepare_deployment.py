"""Stage explicitly selected configuration files for manual NAS deployment."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL = {"configuration.yaml", "automations.yaml", "scripts.yaml", "scenes.yaml"}
DIRECTORIES = {"packages", "blueprints", "themes", "custom_components", "www"}
SUFFIXES = {
    ".yaml", ".yml", ".py", ".json", ".js", ".css", ".html", ".svg",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".woff", ".woff2", ".ttf",
}
BLOCKED = {"secrets.yaml", "__pycache__", "deps", "tts", "backups", "node_modules"}


def source_file(name):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError(f"Use a relative file path inside config/: {name}")
    if any(part.startswith(".") or part in BLOCKED for part in relative.parts):
        raise ValueError(f"Runtime, hidden, or secret path is forbidden: {name}")
    allowed = name in TOP_LEVEL or (
        len(relative.parts) > 1
        and relative.parts[0] in DIRECTORIES
        and relative.suffix in SUFFIXES
    )
    if not allowed:
        raise ValueError(f"File is outside the deployment allowlist: {name}")
    source = ROOT / "config" / relative
    if any(path.is_symlink() for path in [source, *source.parents]):
        raise ValueError(f"Symbolic links are forbidden: {name}")
    if not source.is_file():
        raise ValueError(f"Expected an existing file, not a folder: {name}")
    return relative, source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="Individual paths relative to config/")
    args = parser.parse_args()
    # Read and validate everything before creating the deployment folder.
    selected = {}
    for name in args.files:
        relative, source = source_file(name)
        selected[relative.as_posix()] = source.read_bytes()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    destination = ROOT / ".deploy" / stamp
    payload = destination / "HomeAssistant"
    manifest = []
    try:
        payload.mkdir(parents=True, exist_ok=False)
        for name, contents in selected.items():
            target = payload / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
            manifest.append({"path": name, "sha256": hashlib.sha256(contents).hexdigest()})
        (destination / "manifest.json").write_text(
            json.dumps({"files": manifest, "deletions": []}, indent=2) + "\n"
        )
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        raise
    print(f"Prepared {len(manifest)} file(s): {payload}")
    print("Copy only these files to matching NAS paths; do not replace the whole folder.")
    for entry in manifest:
        print(f"  {entry['path']}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"Cannot prepare deployment: {error}", file=sys.stderr)
        sys.exit(1)
