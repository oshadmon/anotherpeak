Build a single-file HTML dashboard for AnotherPeak, an operator of two diesel-electric passenger boats (Helios and HydraAix) on Lac du Bourget, France. The dashboard serves two audiences: the captain (live decisions) and the fleet manager (daily/weekly review). All data comes from an AnyLog network via REST POST.

## Goals, in priority order
1. Minimize diesel use. Diesel costs about €2.50/L (make this configurable). The generator currently runs 59–74 hours and burns 720–820 L per boat over 6 weeks.
2. Extend battery life: watch battery current and temperature per pack.
3. Passenger comfort: arrive at the end of each cruise on electric power (generator off). Treat this as a constraint ("keep enough reserve for the last X minutes"), not a goal that competes with diesel savings.

## Data access
POST to the configured node (default http://172.233.253.95:32349) with:
  {"command": "sql <DBMS> format=json \"<SQL>\"", "AnyLog-Agent": "AnyLog/1.23", "destination": "network"}
The response is {"Query": [ ...rows... ], "Statistics": [...]}. Default DBMS: <anotherpeak_v2>.

AnyLog SQL rules (verified — do not deviate):
- increments(<unit>, <n>, timestamp) goes in the SELECT list for time-bucketed aggregation, with GROUP BY for other columns.
- period(<unit>, <n>, '<YYYY-MM-DD HH:MM:SS>', timestamp) goes in the WHERE clause for "last N units before a time".
- increments() and period() cannot be combined in one query; use an explicit timestamp range with increments().
- Arithmetic in the SELECT list is rejected (e.g. power*1000/voltage). Fetch raw columns and compute in JavaScript.
- No joins. Combine tables client-side by matching timestamps.
- The boat column may be space-padded ("Helios  "); trim in JS. WHERE boat = 'Helios' works.
- Timestamps are UTC. Data currently spans 2026-07-10 to 2026-08-20, so default the time window to end at the latest data, with an option for "now".

## Tables
Long-format device tables (one row per measurement). Columns: boat, ip, id, side, component (= measurement name), value (float), timestamp. A physical unit is identified by (ip, id, side). Text values live in <table>_state with the same columns.
- bmwix — battery packs, 4 per side (8 per boat). Measurements: gCurrent (A; negative = discharging), gMaxCellTemperature, gAverageTemperature (°C), gStateOfCharge, gStateOfHealth (%), gPackVoltage (V), gTimeToFullMinute, actualCurrent, actualSoc, actualTempBattery, actualTempBatteryMax, ekmvPresHigh.
- ach65 — propulsion motors, one per side. ggMotorPower (kW), gMotorVoltage (V), ggMotorTemperature, ggElectronicTemperature (°C), totalTimeEnabledHours.
- gd — generator, one per boat, no side. EngineRPM (fixed 1500 when running; running = EngineRPM > 0), Load (%), FuelRate (L/h), TotalFuelUsed (L, cumulative), EngineRunHours, T-Coolant, ExhaustTemp, OilPress, NumSuccStarts, NumUnscStarts, ServiceTime.
- bcl25 — AC chargers. Helios: 2 on port, 1 on starboard. HydraAix: 3 units with no side, IDs "1", "2", "3". gActDcPower (kW), gActAcCurrent, gActAcVoltage, currentL1-3, voltageL1-3, gActElectronicTemperature. State in bcl25_state (gState: Running, PreOperational, …).
- elptx — power converter (HydraAix starboard only). powerActual, gPowerActual (kW, always ≤ 0; direction unconfirmed), dcVoltage, powerRequest. State in elptx_state.

Single-value tables (columns: component, ip, id, side, boat, timestamp, value):
- batterystateofchargepercent, powerbalance (kW, negative = discharging), speedoverground, rangebattery, trip (cumulative log), stbdrpmshaft, starterbatteryvoltage, systemstate (text), vesselstate (text).
- location has no ip/id/side; value is the text "lat, lon".
- Side values: B = port, T = starboard.
Ignore: hmi* clock tables, hmismuip, servercpuload, distancedestination (never set), headingdestination.

Data quirks:
- Treat 32.767 in ekmvPresHigh as "not available" unless the data shows otherwise.
- Occasional zero readings for temperature or state of health are dropouts, not real values; exclude them from minimums.
- Sampling is roughly every 5 minutes; don't present anything as second-level precision.

## Dashboard layout
Top bar: boat switcher (discovered from the data, plus a configured "known boats" list), time window (1 h / 6 h / 24 h / 7 d / 30 d), window end (latest data / now), refresh and auto-refresh.

Panel 1 — Diesel (goal 1):
- Generator hours, litres (from TotalFuelUsed max − min) and euros for the window, per day and per cruise.
- Generator start/stop events with state of charge at each; flag "generator ran while the battery had more than <X>% charge".
- Charging source: charger running while generator off = shore; charger running while generator on = diesel. Show hours and kWh of each.
- Waste figure: litres burned while the battery had room and shore power followed within the same day.

Panel 2 — Battery health (goal 2):
- Per-pack current (A) and hottest-cell temperature over time; per-pack state of health.
- Alerts, with configurable thresholds: pack current above <X> A; cell temperature above <X> °C; port/starboard charge difference above <X> points; any pack running more than <X> °C warmer than its siblings; time spent above 95% or below 15% charge.
- Motor and charger electronics temperatures with the same threshold logic.

Panel 3 — Arrival reserve (goal 3):
- Configurable cruise end time or duration, plus a reserve target (default: the last 20 minutes on battery).
- Projected charge at cruise end at the current speed, the speed needed to arrive electric, and the latest time to stop the generator.
- Speed-to-power curve fitted per boat from history (ggMotorPower vs speedoverground, matched by timestamp); use it for "at X kn instead of Y you save Z kWh" advice.

Map: GPS track for the window from location, colored by speed, with markers where the generator started and stopped.

## Recommendations
Rule-based and explainable only: each recommendation states the numbers behind it (e.g. "Slowing from 10 to 8 kn cuts propulsion power from ~35 to ~20 kW; you'd reach the dock at 24% without the generator"). No black-box scoring. Show at most three at once, highest euro impact first.

## Technical requirements
- One self-contained HTML file. Leaflet and Chart.js from cdnjs. OpenStreetMap tiles, with optional OpenSeaMap seamarks overlay.
- Settings panel, saved to localStorage: REST protocol/host/port, DBMS, destination, AnyLog-Agent, Content-Type (application/json or text/plain), optional Authorization header, timeout, known boats, diesel price, alert thresholds, cruise end and reserve, theme (system/light/dark; dark mode dims the base map but not the seamarks).
- A request log showing each command, with a "copy as curl" button.
- Run independent queries in parallel; one failing query must not blank the whole page. Show clear empty and error states, including a hint about CORS when the fetch itself fails.
- Show all times in UTC and label them as UTC. Port = red, starboard = green.
- If you have access to the AnyLog MCP connector, verify table and column names with listColumns before writing queries, and test each query shape once before relying on it.

## Still unknown (make configurable, don't guess)
- Generator rated power (kW), needed for litres per kWh and the generator's most efficient load: <GENERATOR_KW or leave configurable>.
- The cruise schedule: <fixed routes/durations, or leave configurable>.
- Whether shore power is available at the home dock: <yes/no>.
- Speed units in speedoverground (the dashboard should label them configurably; default kn).