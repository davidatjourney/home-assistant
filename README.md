# Home Assistant configuration workspace

This workspace holds configuration copied from the Ugreen NAS. Use a single `config/` folder and Git branches for changes, then manually copy the changed, reviewed files back to the NAS, overwriting their matching destinations.

## Installation

- Host: Ugreen NAS.
- Installation: Home Assistant Container.
- Container name: `homeassistant`.
- Image: `ghcr.io/home-assistant/home-assistant:stable`.
- Home Assistant Core: `2026.10.1`, as shown on 14 October 2026.
- Frontend: `20260930.3`.
- NAS configuration folder, as displayed in the container UI: `Shared folder/HomeAssistant`.
- Container mount destination: `/config`.
- Restart method: Home Assistant UI.
- The Home Assistant installation supplied with Ugreen is deactivated.

The NAS's absolute filesystem path and container networking settings have not yet been recorded. The `stable` image tag does not pin a specific Core version.

## Versions and branches

The original `HomeAssistant_14_oct/` snapshot has been renamed to `config/`. Git will preserve versions instead of duplicating folders:

```text
home_assistant/
  README.md
  .gitignore
  config/                     # Configuration being edited
  tools/prepare_deployment.py # Optional local helper for collecting dashboard files
  deploy/                    # Ignored deployment output
  .local-snapshot/            # Ignored archive of copied runtime files
```

Use `main` for reviewed configuration and branches such as `change/solar-controller` for adjustments. Once a deployment is verified on the NAS, tag its commit with a name such as `deployed-YYYY-MM-DD-01`. A merge alone does not mean the change has been deployed.

Record each change and deployment in a tracked `DEPLOYMENTS.md`, including:

- The intended change, commit, and deployed baseline used.
- Files changed and why.
- Validation performed and results.
- Whether and when the changes were copied to the NAS.
- Results after restart and the files needed to roll back.

The user copies any configuration files changed on the NAS or through Home Assistant back into this workspace before requesting further edits. Make additions here and provide complete replacement files; the user does not need to merge changes manually. Request updated live files only if there is evidence of changes that have not been copied here.
The baseline contains YAML files, a `packages/solar_controller.yaml` package, and custom Sunsynk and HACS integrations. Their contents have not yet been reviewed: several copied files and directories currently lack local read permissions.

Copied databases, logs, Python caches, `deps/`, and `tts/` were moved out of `config/` into `.local-snapshot/2026-10-14-runtime/`. This local archive makes the cleanup reversible; it is not a verified full backup. Configuration, blueprints, integration source, and the ignored `secrets.yaml` remain in `config/`. This cleanup does not change the live NAS files.

## Applying changes

1. Edit the files in `config/` on a Git branch and review the changes. These are complete replacement files, including the additions made here.
2. Back up the destination files, then copy only the changed files directly from `config/` into their matching locations in `Shared folder/HomeAssistant`, overwriting those files. Create subfolders as needed. No manual merge or deployment script is required.
3. Open **Settings → Tools → YAML** ([direct link](http://holtz-storage.local:8123/config/tools/yaml)). Under **Configuration validation**, select **Check configuration** and wait for the result. If it fails, keep the error text and fix the reported issue before restarting. If it passes, go to **Settings → ⋮ (top right) → Restart Home Assistant**, then select **Restart Home Assistant**.
4. Verify the affected controls and readings, then record the deployment result.

The user copies any server-side configuration edits here before further work, so routine deployment does not require a separate live comparison. If an uncopied server edit is discovered, obtain that updated file before preparing its replacement.

`python3 tools/prepare_deployment.py` is an optional local helper that always collects all eight files needed by the home dashboard, including its sensor package and SVGs, into `deploy/` and records their hashes. No file list is required or accepted. Keep the script's file list updated when dashboard dependencies change. Neither the script nor its manifest is needed on the NAS.

Copy individual changed files, not the entire `config/` folder. Leave secrets, `.storage`, databases, logs and caches on the NAS. If a change fails, restore the backed-up files and restart.

## Git

Git branches record edits and tags identify versions confirmed to work on the NAS. The NAS stays a runtime installation; it does not need to be a Git checkout.

Git has not been initialized for this workspace. The existing root `.git` directory is empty and read-only in this environment, so repository setup needs a writable location or a change to the workspace restrictions.

The root `.gitignore` excludes `secrets.yaml`, `.storage`, databases and journals, logs, generated caches, local environments, deployment output, and editor clutter. YAML configuration, packages, blueprints, and custom integration source remain eligible for tracking. Review configuration files for embedded credentials as well. Keep the repository private if it contains household or device details.

Ignored files remain on disk and may still be needed on the NAS. In particular, `.storage` contains UI-managed configuration, so Git is not a complete Home Assistant backup. Ignore rules also do not remove files already committed to Git.

## Backups and remaining details

The NAS has redundant hard drives. Redundancy protects against some drive failures; a separate versioned backup is needed to recover overwritten or deleted configuration. A backup and full-restore process has not yet been confirmed.

Still to document:

- Backup location, schedule, and restore procedure.
- Main devices, integrations, and automation requirements.
- The first planned adjustment.
