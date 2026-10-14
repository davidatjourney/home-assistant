# Home Assistant configuration workspace

This workspace holds configuration copied from the Ugreen NAS. Use a single `config/` folder and Git branches for changes, then manually copy a prepared set of reviewed files back to the NAS.

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
  tools/prepare_deployment.py # Prepare selected files for manual copying
  .deploy/                    # Ignored deployment output
  .local-snapshot/            # Ignored archive of copied runtime files
```

Use `main` for reviewed configuration and branches such as `change/solar-controller` for adjustments. Once a deployment is verified on the NAS, tag its commit with a name such as `deployed-YYYY-MM-DD-01`. A merge alone does not mean the change has been deployed.

Record each change and deployment in a tracked `DEPLOYMENTS.md`, including:

- The intended change, commit, and deployed baseline used.
- Files changed and why.
- Validation performed and results.
- Whether and when the changes were copied to the NAS.
- Results after restart and the files needed to roll back.

If configuration has changed through the Home Assistant UI, compare the current NAS files with the local files before editing or deploying. In particular, the UI may change `automations.yaml`, `scripts.yaml`, and `scenes.yaml`; these are shared with the server until a stricter ownership rule is established.

The baseline contains YAML files, a `packages/solar_controller.yaml` package, and custom Sunsynk and HACS integrations. Their contents have not yet been reviewed: several copied files and directories currently lack local read permissions.

Copied databases, logs, Python caches, `deps/`, and `tts/` were moved out of `config/` into `.local-snapshot/2026-10-14-runtime/`. This local archive makes the cleanup reversible; it is not a verified full backup. Configuration, blueprints, integration source, and the ignored `secrets.yaml` remain in `config/`. This cleanup does not change the live NAS files.

## Preparing and applying changes

1. Compare each file to be changed with the current NAS version, and incorporate any newer server edits.
2. Edit on a Git branch, review and commit the changes, and make a dated backup of the live files that will be replaced.
3. Prepare only the selected files using the command below. Manually copy those files into their matching locations in `Shared folder/HomeAssistant`. Copy the contents of the prepared `HomeAssistant/` folder, not that enclosing folder itself. Confirm replacement of only the listed files. Do not use a whole-folder replace or mirror/delete operation.
4. Run Home Assistant's configuration check before restarting. The exact UI procedure remains to be documented.
5. If validation succeeds, restart through the Home Assistant UI.
6. Check the affected integrations, entities, automations, and logs, then record the result in `DEPLOYMENTS.md` and tag the deployed commit.

For example, to prepare only the solar controller package, run from this workspace:

```sh
python3 tools/prepare_deployment.py packages/solar_controller.yaml
```

The tool creates `.deploy/<timestamp>/HomeAssistant/` with only the explicitly selected files and writes a sibling `manifest.json` listing their paths and hashes. It does not connect to the NAS or delete server files. Paths are relative to `config/`. It refuses hidden paths, secrets, runtime files, folders, and symbolic links. It permits the four top-level configuration YAML files and selected source/asset file types under `packages`, `blueprints`, `themes`, `custom_components`, and `www`.

The deployment allowlist is separate from `.gitignore`: being tracked in Git does not automatically make a file eligible for deployment. Review selected file contents for embedded credentials. Handle deliberate deletions separately, with an explicit record and backup. Custom integration upgrades that require removing old files need a separate reviewed procedure.

The tool packages the current local files. Prepare from a clean checkout of the intended commit so the payload corresponds to the version recorded in Git. Local copied files must be readable before the tool can package them.

If validation fails, restore or correct the copied files before restarting. If the change fails after restart, restore the backed-up files and restart again.

Do not deploy the local snapshot wholesale over the running installation. Database files, database journals, logs, caches, and `.storage` are runtime state and should not be overwritten during routine configuration changes. A full restore needs its own procedure.

## Git

Git branches record edits and tags identify versions confirmed to work on the NAS. The NAS stays a runtime installation; it does not need to be a Git checkout.

Git has not been initialized for this workspace. The existing root `.git` directory is empty and read-only in this environment, so repository setup needs a writable location or a change to the workspace restrictions.

The root `.gitignore` excludes `secrets.yaml`, `.storage`, databases and journals, logs, generated caches, local environments, deployment output, and editor clutter. YAML configuration, packages, blueprints, and custom integration source remain eligible for tracking. Review configuration files for embedded credentials as well. Keep the repository private if it contains household or device details.

Ignored files remain on disk and may still be needed on the NAS. In particular, `.storage` contains UI-managed configuration, so Git is not a complete Home Assistant backup. Ignore rules also do not remove files already committed to Git.

## Backups and remaining details

The NAS has redundant hard drives. Redundancy protects against some drive failures; a separate versioned backup is needed to recover overwritten or deleted configuration. A backup and full-restore process has not yet been confirmed.

Still to document:

- Backup location, schedule, and restore procedure.
- Configuration validation procedure.
- Main devices, integrations, and automation requirements.
- The first planned adjustment.
