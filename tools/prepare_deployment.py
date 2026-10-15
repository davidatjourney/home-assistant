"""Stage all files needed by the home dashboard for manual NAS copying."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
HOME_DASHBOARD_FILES = (
    "configuration.yaml",
    "dashboards/home-controls.yaml",
    "packages/dashboard_energy.yaml",
    "www/viewport-fit-card.js",
    "www/floorplans/house-clean-layout-v2.svg",
    "www/floorplans/solar-panel-layout-v2.svg",
    "www/floorplans/pool-stats-layout-v2.svg",
    "www/floorplans/geyser-stats-layout-v2.svg",
)
TOP_LEVEL = {"configuration.yaml", "automations.yaml", "scripts.yaml", "scenes.yaml"}
DIRECTORIES = {"packages", "blueprints", "themes", "custom_components", "www", "dashboards"}
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


def verify_deployment(directory):
    """Reject a stale or altered payload before the user copies it to the NAS."""
    directory = directory.resolve()
    if not directory.is_relative_to((ROOT / "deploy").resolve()):
        raise ValueError("Deployment must be inside this workspace's deploy/ folder")
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("deletions"):
        raise ValueError("Automatic server deletions are forbidden")
    files = manifest.get("files", [])
    if not files:
        raise ValueError("Deployment manifest has no files")
    for entry in files:
        relative, source = source_file(entry["path"])
        staged = directory / "HomeAssistant" / relative
        if staged.is_symlink() or not staged.resolve().is_relative_to(directory / "HomeAssistant"):
            raise ValueError(f"Unsafe staged file: {relative}")
        expected = entry["sha256"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Stale deployment: {relative} changed; prepare a new payload")
        if hashlib.sha256(staged.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Altered deployment file: {relative}; prepare a new payload")
    expected_paths = {entry["path"] for entry in files}
    actual_paths = {
        path.relative_to(directory / "HomeAssistant").as_posix()
        for path in (directory / "HomeAssistant").rglob("*") if path.is_file()
    }
    if any(path.is_symlink() for path in (directory / "HomeAssistant").rglob("*")):
        raise ValueError("Deployment contains symbolic links")
    if expected_paths != actual_paths:
        raise ValueError("Deployment contains missing or unlisted files")
    print(f"Verified {len(files)} file(s) against the current configuration: {directory}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path, help="Check a prepared deployment folder before copying")
    args = parser.parse_args()
    if args.verify:
        verify_deployment(args.verify)
        return
    # Read and validate everything before creating the deployment folder.
    selected = {}
    for name in HOME_DASHBOARD_FILES:
        relative, source = source_file(name)
        selected[relative.as_posix()] = source.read_bytes()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    destination = ROOT / "deploy" / stamp
    payload = destination / "HomeAssistant"
    manifest = []
    try:
        payload.mkdir(parents=True, exist_ok=False)
        for name, contents in selected.items():
            target = payload / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
            manifest.append({"path": name, "sha256": hashlib.sha256(contents).hexdigest()})
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
        )
        (destination / "manifest.json").write_text(json.dumps({
            "files": manifest, "deletions": [],
            "git_commit": commit.stdout.strip() if commit.returncode == 0 else None,
        }, indent=2) + "\n")
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        raise
    print(f"Prepared {len(manifest)} file(s): {payload}")
    print("Copy only these files to matching NAS paths; do not replace the whole folder.")
    for entry in manifest:
        print(f"  {entry['path']}")
    print(f"Before copying, verify: python3 tools/prepare_deployment.py --verify {destination}")
    print("After copying: Settings > Tools > YAML > Configuration validation > Check configuration.")
    print("Open: http://holtz-storage.local:8123/config/tools/yaml")
    print("If the check fails, save the error and fix it before restarting.")
    print("If it passes: Settings > three dots (top right) > Restart Home Assistant > Restart Home Assistant.")
    print("Then hard-refresh the browser (Ctrl+Shift+R) and verify the dashboard.")
    print("If it is broken, copy the dashboard error; check Settings > System > Logs for server errors.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"Cannot prepare deployment: {error}", file=sys.stderr)
        sys.exit(1)
