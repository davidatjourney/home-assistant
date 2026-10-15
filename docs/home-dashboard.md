# Home controls dashboard

The dashboard controls three air conditioners, garage lights, the geyser and the pool. It also shows combined solar readings, aircon room temperatures, and power/daily energy for the pool and geyser. It uses built-in Home Assistant controls with a small local wrapper to fit the desktop floor plan to the screen.

## Layout and controls

The Devices tab provides room controls and statistics at every screen size. The Floor plan tab adapts to the screen:

- At 1280px and above, it centers the complete vector plan with live overlays and scales them together to fit the available screen width and height. Resizing the browser or sidebar recalculates the fit.
- Below 1280px, it shows readable control tiles and statistics, followed by a plan that opens at full size when tapped. It does not compress fixed-size overlay text and controls onto a phone.

Floor-plan switch controls use a solid bright green (`#22c55e`) circle with a white icon when on, grey when off, and red for unknown/unavailable states. The icon color is set through `--state-icon-color` so Home Assistant’s default icon color does not override it. The Pool name sits below its circle with a 12px gap at the plan’s base size. The geyser switch, status, power, and daily energy share a compact white panel above the bathroom, leaving the Stoep clear. On/off icons toggle the switch; red icons open details. Both garage-light icons operate the same switch. Pool and geyser keep their device names and show separate On/Off statuses near their icons. Both garage icons also have state badges. Missing or unavailable switch states show `-`. Aircon icons open their controls; temperature badges show the aircon's current_temperature in Celsius, not its target setting.

Floor-plan readings show `-` when an entity or value is missing, unknown or unavailable, including temperature attributes. Valid zero readings retain their units. These display elements keep the original entities and open their details when tapped; they do not change sensor states. Switch tiles on Devices and the narrow-screen layout use green when active. Aircon floor-plan icons use green for active modes.

The plan at `/local/floorplans/house-clean.svg` is a simplified redraw of the supplied layout, including the user's room and door corrections. It is a visual dashboard background, not a measured architectural drawing. The main-bedroom door is hinged at the top of its corridor-facing opening so its leaf does not cross the neighboring doorway.

## Weather

`weather.forecast_home` supplies current conditions and temperature. Devices and the narrow-screen Floor plan layout show the native daily forecast card. The desktop floor plan shows the same entity in a compact native current-weather card in the empty top-left area; tap it for details. The local wrapper forwards live Home Assistant updates and leaves weather rendering and forecast retrieval to Home Assistant.

For this update, copy `configuration.yaml`, `dashboards/home-controls.yaml` and `www/viewport-fit-card.js` together. Follow the configuration-check and restart steps below, then hard-refresh the browser. Confirm current weather and daily forecasts load; forecast data is fetched by the native card, not included in the entity-inventory export.

## Solar and device measurements

The floor-plan solar panel uses a white surface, softly tinted live-reading cells, two wider flow cells, and a six-cell grid for daily totals. Its SVG labels and dashboard overlays share the same layout; copy both `www/floorplans/solar-panel.svg` and `dashboards/home-controls.yaml` together when updating it.

Solar now shows generation, house usage, battery SOC, battery flow and grid flow. Solar today shows generation, house usage, grid import/export and battery charge/discharge. Existing combined-system sensors provide the totals; the dashboard does not sum them again.

The new `sensor.home_dashboard_battery_flow` and `sensor.home_dashboard_grid_flow` interpret the same sign conventions as the existing Sunsynk flow card: battery negative means charging, battery positive means discharging; grid positive means importing, grid negative means exporting. Zero is Idle. Invalid or missing input makes the derived sensor unavailable. Magnitudes at or above 1000 W display in kW. Numeric power remains available on Devices.

Pool power uses `sensor.pool_power`; pool daily energy reuses `sensor.solar_pool_energy_today`, defined by the existing solar_controller package. Both readings sit inside the lower part of the pool, below its control and name, instead of in a separate panel beneath the pool. Cumulative pool energy is not shown as a daily total.

`packages/dashboard_energy.yaml` creates `sensor.geyser_energy_today` from `sensor.geyser_total_energy`. Its first day is partial, and usage before activation is not reconstructed. Verify that the total-energy source increases when the geyser consumes energy: its exported reading was zero. Verify the three newly created sensor IDs after deployment.

## Copy to the NAS

The files here include the dashboard additions and are ready to overwrite their matching NAS files. No manual merging or deployment script is required. The user copies any server-side edits here before further changes are made.

Optionally, run `python3 tools/prepare_deployment.py` to collect all eight required files, including the sensor package and SVGs, into a timestamped `deploy/` folder. The script always prepares the complete set; it does not accept a partial file list.

1. Back up existing destination files.
2. Copy these eight files directly from `config/` into the matching paths in `Shared folder/HomeAssistant`, overwriting existing files and creating subfolders as needed:

   - `configuration.yaml`
   - `dashboards/home-controls.yaml`
   - `packages/dashboard_energy.yaml`
   - `www/viewport-fit-card.js`
   - `www/floorplans/house-clean.svg`
   - `www/floorplans/solar-panel.svg`
   - `www/floorplans/pool-stats.svg`
   - `www/floorplans/geyser-stats.svg`

3. Open **Settings → Tools → YAML** ([direct link](http://holtz-storage.local:8123/config/tools/yaml)). Under **Configuration validation**, select **Check configuration** and wait for the result. If it fails, keep the error text and fix the reported issue before restarting. If it passes, go to **Settings → ⋮ (top right) → Restart Home Assistant**, then select **Restart Home Assistant**.
4. Open Home controls in the sidebar or http://holtz-storage.local:8123/home-controls/devices. Verify all controls and readings, both garage icons, the new sensor IDs, phone and desktop layouts, and the displayed power directions against the inverter.

For the screen-fit update, overwrite `configuration.yaml` and `dashboards/home-controls.yaml`, and add `www/viewport-fit-card.js`. Follow the configuration-check and restart steps above, then hard-refresh the browser (**Ctrl+Shift+R**). The frontend loads the local module automatically; no HACS installation or resource entry is needed. Verify that the complete plan fits after resizing the window and opening/closing the sidebar. Very short windows reduce text and control sizes; the Devices tab offers full-size controls.

If the configuration check passes but the dashboard is broken, copy the exact dashboard error message. Check **Settings → System → Logs** for startup or integration errors. The configuration check validates server configuration; it does not verify that browser JavaScript or dashboard controls render correctly.

For later changes, copy only the files changed for that update. A dashboard layout edit usually requires only `dashboards/home-controls.yaml`.

Leave all other NAS files in place, including secrets, runtime storage and databases. If the change fails, restore the backed-up files and restart.

## References

- https://www.home-assistant.io/dashboards/dashboards/
- https://www.home-assistant.io/dashboards/conditional/
- https://www.home-assistant.io/dashboards/picture-elements/
- https://www.home-assistant.io/dashboards/picture/
- https://www.home-assistant.io/integrations/utility_meter/
- https://github.com/slipx06/sunsynk-power-flow-card/blob/main/docs/configuration.md

- https://www.home-assistant.io/integrations/frontend/#loading-extra-javascript
- https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/

- https://www.home-assistant.io/dashboards/weather-forecast/

For the brighter switch controls and label-spacing fix, overwrite `dashboards/home-controls.yaml` and `www/floorplans/house-clean.svg` together, then reload the dashboard. The plan URL includes a cache version for the changed labels. Verify the Pool and Geyser labels clear their circles and active switches show solid green with white icons.

For the consolidated geyser panel, copy `dashboards/home-controls.yaml`, `www/floorplans/geyser-stats.svg`, and `www/floorplans/house-clean.svg` together, then hard-refresh the dashboard. The panel background appears before its interactive controls so the switch remains visible and usable.
