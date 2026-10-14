# Home controls dashboard

The dashboard controls three air conditioners, garage lights, the geyser and the pool. It also shows combined solar readings, aircon room temperatures, and power/daily energy for the pool and geyser. It uses built-in Home Assistant cards.

## Layout and controls

The Devices tab provides room controls and statistics at every screen size. The Floor plan tab adapts to the screen:

- At 1280px and above, it shows the vector plan with live overlays.
- Below 1280px, it shows readable control tiles and statistics, followed by a plan that opens at full size when tapped. It does not compress fixed-size overlay text and controls onto a phone.

Switch icons are gold when on, grey when off, and red for unknown/unavailable states. On/off icons toggle the switch; red icons open details. Both garage-light icons operate the same switch. Pool and geyser have static labels; only the garage controls retain separate state badges. Aircon icons open their controls; temperature badges show the aircon's current_temperature in Celsius, not its target setting.

The plan at `/local/floorplans/house-clean.svg` is a simplified redraw of the supplied layout, including the user's room and door corrections. It is a visual dashboard background, not a measured architectural drawing. The main-bedroom door is hinged at the top of its corridor-facing opening so its leaf does not cross the neighboring doorway.

## Solar and device measurements

Solar now shows generation, house usage, battery SOC, battery flow and grid flow. Solar today shows generation, house usage, grid import/export and battery charge/discharge. Existing combined-system sensors provide the totals; the dashboard does not sum them again.

The new `sensor.home_dashboard_battery_flow` and `sensor.home_dashboard_grid_flow` interpret the same sign conventions as the existing Sunsynk flow card: battery negative means charging, battery positive means discharging; grid positive means importing, grid negative means exporting. Zero is Idle. Invalid or missing input makes the derived sensor unavailable. Magnitudes at or above 1000 W display in kW. Numeric power remains available on Devices.

Pool power uses `sensor.pool_power`; pool daily energy reuses `sensor.solar_pool_energy_today`, defined by the existing solar_controller package. Cumulative pool energy is not shown as a daily total.

`packages/dashboard_energy.yaml` creates `sensor.geyser_energy_today` from `sensor.geyser_total_energy`. Its first day is partial, and usage before activation is not reconstructed. Verify that the total-energy source increases when the geyser consumes energy: its exported reading was zero. Verify the three newly created sensor IDs after deployment.

## Prepare and deploy

1. Compare the current NAS configuration.yaml with the local version and preserve any newer server changes. Make dated backups of all destination files being replaced.
2. Review and commit the branch. Prepare a fresh payload from the intended commit:

```sh
python3 tools/prepare_deployment.py \
  configuration.yaml \
  dashboards/home-controls.yaml \
  packages/dashboard_energy.yaml \
  www/floorplans/house-clean.svg \
  www/floorplans/solar-panel.svg \
  www/floorplans/pool-stats.svg \
  www/floorplans/geyser-stats.svg
```

3. Immediately before copying, run the verification command printed by the tool:

```sh
python3 tools/prepare_deployment.py --verify .deploy/<timestamp>
```

Verification checks that the source files and staged payload match the manifest, and refuses unlisted files. If configuration has changed since preparation, generate a new payload. The manifest records the Git commit at preparation; it is a local audit record, not a NAS upload.

4. Copy only the seven listed files from the payload's HomeAssistant folder into matching paths in Shared folder/HomeAssistant. Create subfolders as needed. Do not replace or mirror the whole configuration folder, and do not copy manifest.json into Home Assistant.
5. Run Home Assistant's configuration check. If it passes, restart through the Home Assistant UI.
6. Open Home controls in the sidebar or http://holtz-storage.local:8123/home-controls/devices. Verify all controls and readings, both garage icons, the new sensor IDs, phone and desktop layouts, and the displayed power directions against the inverter.
7. Record the result and tag the verified deployment commit. If it fails, restore the backed-up files and restart.

No database, runtime storage, secrets, logs or caches are deployed. Utility-meter state belongs to the running Home Assistant instance and must be preserved. Local checks do not replace validation and device testing on the NAS.

## References

- https://www.home-assistant.io/dashboards/dashboards/
- https://www.home-assistant.io/dashboards/conditional/
- https://www.home-assistant.io/dashboards/picture-elements/
- https://www.home-assistant.io/dashboards/picture/
- https://www.home-assistant.io/integrations/utility_meter/
- https://github.com/slipx06/sunsynk-power-flow-card/blob/main/docs/configuration.md
