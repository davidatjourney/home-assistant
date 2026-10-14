# Working on this Home Assistant configuration

## Request live information through templates

When a task needs information from the running Home Assistant instance that is missing or potentially stale in this repository, proactively ask the user to run a template in Home Assistant. Do not wait for the user to suggest exporting it.

- Inspect relevant local files first. Ask only for information still needed to implement or verify the requested change.
- Provide a complete, ready-to-paste Jinja template and direct the user to **Settings → Tools → Template**: <http://holtz-storage.local:8123/config/tools/template>.
- Explain briefly what the template collects and ask the user to paste the rendered result or attach it as a JSON file.
- Prefer structured JSON using `to_json(pretty_print=True)`. Collect only necessary fields, such as entity IDs, friendly names, device names, areas, domains, device classes, units, and relevant capabilities.
- For dashboards and controls, request an entity inventory if actual entity IDs and room assignments are not available. Never invent IDs or assume that a device ID is an entity ID.
- Do not request credentials, tokens, authentication files, or a full `.storage` export. Avoid exporting all attributes or states indiscriminately; these can contain private information.
- Explain coverage accurately: iterating over `states` lists loaded entities, including unavailable entities, but does not provide a complete registry of disabled entities or devices without loaded entities. If registry information is necessary, request a narrowly scoped export separately.
- Use read-only templates for discovery. Do not ask the user to trigger actions or change device states merely to collect inventory.
- Continue independent work while awaiting the export, but wait for the necessary output before completing changes that depend on it. Do not repeatedly request information already supplied unless it needs refreshing.

## Configuration and deployment

- Treat `config/` as editable configuration, not a complete or current copy of live server state.
- Use Git branches for changes and prepare only reviewed files for manual deployment.
- Keep credentials, databases, logs, caches, and UI-managed `.storage` state out of Git and routine deployment payloads.
- Compare files that Home Assistant can also edit, such as `automations.yaml`, `scripts.yaml`, and `scenes.yaml`, with the live versions before replacing them.
- The user manually copies files to the Ugreen NAS and restarts Home Assistant through its UI. Do not assume direct NAS access or that a local change has been deployed.
