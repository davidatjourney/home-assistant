# Home controls dashboard

The dashboard controls three air conditioners, garage lights, the geyser and the pool. It also shows combined solar readings, current room temperatures, and power/daily energy for the pool and geyser. It uses built-in Home Assistant controls and a small local wrapper to fit the desktop floor plan to the screen.

## Layout

Devices provides full-size controls, forecasts and all energy statistics at every screen size. Floor plan adapts to the screen:

- At 1280px and above, the complete vector plan and live overlays scale together to fit the available width and height. Browser and sidebar resizing recalculate the fit. The base canvas is 1110 × 1040.
- Below 1280px, readable control tiles and statistics appear above a static plan that opens at full size when tapped. The fixed-size desktop overlays are not compressed onto a phone.

Weather and geyser information share a 378px-wide stack at the upper left. Each bedroom has the same aircon/temperature group below its room name, clear of doors and windows. One labelled Garage lights control operates the shared switch. Pool and geyser both present their name, switch/status, power now and energy today in that order. The compact solar panel sits below the house; tap its background or “Daily totals on Devices” footer to open Devices. Tapping an individual reading opens that entity's details.

The background uses consistent room colours:

| Rooms | Colour |
| --- | --- |
| All bedrooms | Soft blue `#eaf2fc` |
| Kitchen, living room, family room | Warm neutral `#f6f3ea` |
| Bathrooms, utility room, workshop, garage | Cool grey `#edf1f5` |
| Stoep | Soft green `#eef4ed` |
| Pool | Water blue `#dff4ff` |

These are room categories, not live device states. Room names also identify each space. The SVG is a simplified redraw with the user's room and door corrections, not a measured architectural drawing. The main-bedroom door remains hinged at the top of its corridor-facing opening.

## Controls and readings

Switch controls show solid green (`#22c55e`) with white icons when on, grey when off, and red when unknown/unavailable. On/off icons toggle their switch; red icons open details. Status text appears alongside the icon. An On status reports the switch state; power readings separately show consumption.

Aircon icons open their controls and use green for active modes. The adjacent temperature is the aircon's `current_temperature` in Celsius, not its target setting. The temperature group also opens details. Readings support keyboard activation and show a visible focus outline.

Missing, unknown or unavailable readings show `-`; valid zero readings retain their units. Pool and geyser daily energy display two decimal places using the user's language settings. Formatting changes only the display, not the sensor values.

`weather.forecast_home` supplies the native weather cards. Desktop shows current weather; Devices and the narrow-screen layout also show daily forecasts. The local wrapper forwards live Home Assistant updates and leaves weather rendering and forecast retrieval to Home Assistant.

## Solar and device measurements

Desktop solar shows generation, house usage, battery SOC, battery flow and grid flow. The six daily totals remain on Devices and in the narrow-screen Floor plan layout: generation, house usage, grid import/export and battery charge/discharge. Existing combined-system sensors provide totals; the dashboard does not sum them again.

`sensor.home_dashboard_battery_flow` and `sensor.home_dashboard_grid_flow` follow the existing Sunsynk flow card's sign conventions: battery negative means charging, positive means discharging; grid positive means importing, negative means exporting. Zero is Idle. Invalid input makes the derived sensor unavailable. Flow magnitudes at or above 1000 W display in kW. Numeric power remains available on Devices.

Pool power uses `sensor.pool_power`; pool daily energy uses `sensor.solar_pool_energy_today` from the existing solar_controller package. Geyser power uses `sensor.geyser_power`. The dashboard_energy package creates `sensor.geyser_energy_today` from `sensor.geyser_total_energy`; its first day is partial. Confirm the total-energy source increases when the geyser consumes energy if the daily reading remains missing or zero.

## Copy this layout update to the NAS

The following seven files are complete replacements. Back up their destinations, then copy them to the matching paths under `Shared folder/HomeAssistant`, overwriting existing files and adding the four newly named SVGs. Copy the files together so the SVGs, overlays and frontend module stay aligned:

- `configuration.yaml`
- `dashboards/home-controls.yaml`
- `www/viewport-fit-card.js`
- `www/floorplans/house-clean-layout-v2.svg`
- `www/floorplans/solar-panel-layout-v2.svg`
- `www/floorplans/pool-stats-layout-v2.svg`
- `www/floorplans/geyser-stats-layout-v2.svg`

The SVG filenames identify this layout revision. The screenshot with a yellow kitchen, clipped panels and bedroom controls on walls combined the new dashboard overlays with previous SVGs. Distinct asset paths make this dashboard request the matching drawings instead of reusing an earlier image under the same name. Leave the old SVGs on the NAS; this update does not reference them. Future changes to image dimensions or overlay coordinates should use new SVG filenames too.

No sensor package changes are required for this update. Keep other NAS files in place. Credentials, databases, logs, caches and UI-managed `.storage` are not part of the replacement set.

1. Open **Settings → Tools → YAML** ([direct link](http://holtz-storage.local:8123/config/tools/yaml)) and select **Check configuration**. Resolve any reported errors before restarting.
2. After a successful check, restart through **Settings → ⋮ (top right) → Restart Home Assistant**. This loads the versioned frontend module.
3. Hard-refresh the browser (**Ctrl+Shift+R**).
4. Verify the bedroom temperatures, switch states, pool/geyser readings and weather. Check that the solar footer opens Devices and daily totals are present there. Resize the browser and sidebar to confirm the complete plan fits; check the phone layout too.

The source files are local configuration, not proof of deployment. Local YAML/XML/JavaScript checks and a preview do not verify the running Home Assistant frontend. If configuration checking fails, save the error. For dashboard problems, copy the exact browser/dashboard error and check **Settings → System → Logs** where applicable. Restore the backed-up files and restart if needed.

For a first installation, also copy the existing `packages/dashboard_energy.yaml`. The optional `tools/prepare_deployment.py` stages the full eight-file installation; it is not required for copying this seven-file update.

## References

- [Picture elements and actions](https://www.home-assistant.io/dashboards/picture-elements/)
- [Native weather card](https://www.home-assistant.io/dashboards/weather-forecast/)
- [Custom cards and elements](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/)
- [Loading extra JavaScript](https://www.home-assistant.io/integrations/frontend/#loading-extra-javascript)
- [Utility meters](https://www.home-assistant.io/integrations/utility_meter/)
