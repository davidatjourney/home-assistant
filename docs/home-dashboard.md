# Home controls dashboard

This YAML dashboard uses the six primary controls provided by the user on 14 October 2026: three air conditioners, garage lights, the geyser, and the pool switch. It uses built-in cards and requires no custom frontend installation.

The three switches have explicit on/off controls. The thermostat cards provide temperature controls and a mode dropdown that uses each air conditioner's supported modes, including off when supported. Inverter configuration switches and aircon display/sound settings are omitted from this everyday view.

## Deployment

1. Compare the live NAS configuration.yaml with the local version before replacing it. Preserve any newer server edits and merge the lovelace dashboard registration if needed.
2. Review and commit the branch, then run:

```sh
python3 tools/prepare_deployment.py configuration.yaml dashboards/home-controls.yaml www/floorplans/house-clean.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/solar-panel.svg www/floorplans/pool-stats.svg www/floorplans/geyser-stats.svg packages/dashboard_energy.yaml
```

3. Back up the existing NAS configuration.yaml. If a dashboard file already exists at the destination, back it up too.
4. Copy only the prepared configuration.yaml, dashboards/home-controls.yaml, www/floorplans/house-clean.svg, www/floorplans/solar-panel.svg, www/floorplans/pool-stats.svg, www/floorplans/geyser-stats.svg, and packages/dashboard_energy.yaml to matching locations inside Shared folder/HomeAssistant. Create the dashboards folder if needed. Do not replace or mirror the full HomeAssistant folder.
5. Run Home Assistant's configuration check. If it succeeds, restart through the Home Assistant UI.
6. Open Home controls from the sidebar, or http://holtz-storage.local:8123/home-controls/devices. Confirm that all six cards resolve and show the correct devices. Test intended switch and climate changes when appropriate and verify the actual devices respond.
7. Record the verified deployment commit and tag it.

The local YAML has been checked for syntax and entity references. Rendering and device behavior still require verification on the running Home Assistant instance.

## Floor-plan view

The Floor plan tab uses a simplified vector redraw based on the user's drawing at www/floorplans/house-clean.svg and built-in Picture Elements controls. It shows the three bedroom aircons, the pool switch, the roof geyser above BAD KR, and two garage-light icons outside either side of the garage door. Both garage icons control switch.garage_ligte_switch_1 because the user confirmed the lights turn on together. Tap an aircon to open its controls; tap a switch to toggle it. Hold any icon to open details. State coloring is handled by Home Assistant.

The original supplied drawing remains in the local /tmp preparation bundle as a reference. The deployed plan is a simplified visual layout, with survey annotations removed and margins cropped; it is not a measured architectural drawing. Device positions are percentages of its width and height; aircon icons are positioned in their rooms rather than claiming exact mounting positions. The geyser and garage-light placements follow the user's descriptions. Fine-tune icon positions after viewing the dashboard on the intended screen.

Check the Floor plan tab after deployment. Verify the image loads and icons align in both desktop and phone layouts. The www image URL is /local/floorplans/house.png. Static www assets can be served without authentication, so do not add secrets or security details to the image.

The pool entity currently has no assigned Home Assistant area; it is included explicitly here. New devices do not appear automatically in this curated YAML dashboard.

## References

- https://www.home-assistant.io/dashboards/dashboards/
- https://www.home-assistant.io/dashboards/sections/
- https://www.home-assistant.io/dashboards/tile/
- https://www.home-assistant.io/dashboards/thermostat/
- https://www.home-assistant.io/dashboards/features/

## Room temperatures and combined solar

Each aircon has a Celsius label bound to its current_temperature attribute. These are the temperatures reported by the aircons, not their target settings or independent room sensors. The user confirmed readings of 20°C, 20°C and 21°C during setup.

The central panel sits below the house outline and uses eleven existing combined-system sensors. The live readings are PV total power, load total power, battery SOC, battery power and grid power. The Today section shows solar generation, house usage, grid import/export and battery charge/discharge in kWh. It reuses the integration's combined readings without calculating additional sums. AC output and rated inverter power are omitted. Direction sensors interpret the same signs as the existing Sunsynk flow dashboard: battery negative means charging and positive means discharging; grid positive means importing and negative means exporting. Invalid source readings make the derived sensors unavailable. Numeric power remains visible in the Devices tab.

A small SVG supplies only the panel background and headings; the values are live Home Assistant state labels. The same readings appear as tiles in the Devices view for small screens. Units and unavailable readings are displayed by Home Assistant. Tap a reading for its details.

The standalone HTML preview uses the user's exported sample readings; it has no live connection to Home Assistant. Verify the live labels, units, unavailable-state behavior and layout after deployment.

- https://www.home-assistant.io/dashboards/picture-elements/

Daniël's floor-plan control is on the right of its room-temperature badge to keep both clear of the room boundary.

## Pool and geyser stats

The floor plan and Devices tab show power now (W) and energy today (kWh) for both devices. Pool power uses sensor.pool_power; pool daily energy reuses sensor.solar_pool_energy_today already defined by solar_controller.yaml. Pool readings in the static preview are 0 W and 5.581 kWh from the user's export. The cumulative sensor.pool_total_energy is not labeled as daily consumption.

The new packages/dashboard_energy.yaml creates a daily utility meter from sensor.geyser_total_energy. The dashboard expects sensor.geyser_energy_today. Verify that entity ID after deployment; the exported inventory did not contain a pre-existing geyser daily meter. The preview displays a dash for the new meter because it has no live value yet.

The first daily cycle is incomplete. Usage before activation is not reconstructed; the first full daily cycle starts at the next local midnight. Home Assistant persists meter state across restarts; routine deployment must not replace its runtime storage. Verify the source sensor actually increases when the geyser consumes energy, since the provided total-energy reading was zero.

Pool stats sit below the pool outline. Geyser stats sit above its roof control so they do not obscure the bathroom. The exported current and voltage sensors remain available in Home Assistant but are omitted from this compact summary. No switch-control automations are added.

Reference: https://www.home-assistant.io/integrations/utility_meter/

Pool and geyser power/daily readings share a single box per device with a small heading. The solar panel has a pale yellow background. The SVG assets are static backgrounds; Home Assistant overlays live sensor readings.

## Final usability refinements

Switch controls show gold backgrounds when on, grey when off, and red for other states such as unknown/unavailable. State labels show the actual switch state independently of power consumption. Both garage-light controls still target the same switch. Aircon controls and their temperature badges are raised slightly to clear the bedroom walls.

The two new template sensors, sensor.home_dashboard_battery_flow and sensor.home_dashboard_grid_flow, show direction and magnitude. Values at or above 1000 W are formatted in kW. Zero reports Idle; invalid or missing input is unavailable. The sign conventions match the bundled flow card's non-inverted defaults and the existing dashboard's configuration. Verify the new sensors and direction against the inverter display after deployment.

The standalone preview provides demonstration toggles only. Its initial switch status is Unknown because actual switch states were not exported. Clicking either garage icon updates both preview icons together. Actual Home Assistant controls use live states and actions.

Sign reference: https://github.com/slipx06/sunsynk-power-flow-card/blob/main/docs/configuration.md
