Build a single-file HTML fleet management dashboard for AnotherPeak, which runs diesel-electric passenger boats (currently Helios and HydraAix) on Lac du Bourget, France. The users are managers. The centerpiece is a unified comparison of all boats that answers one question: which boats should we use, in what order, and which should we pull in or fix? Every recommendation must show the numbers behind it, and managers must be able to record their decision.

## What the business cares about
1. Minimize diesel use. Diesel costs about €2.50/L (configurable).
2. Extend battery life: battery current and temperature per pack.
3. Passenger comfort: arrive at the end of each cruise on electric power (generator off). At current fuel prices this ranks lowest; it is tracked and weighted, not a driver on its own.
Default weights: diesel 3, battery 2, comfort 1 (configurable).

## Data access
POST to the configured node (default http://172.233.253.95:32349):
  {"command": "sql anotherpeak format=json \"<SQL>\"", "AnyLog-Agent": "AnyLog/1.23", "destination": "network"}
Response: {"Query": [...rows...]}. An empty result may come back as {"reply": "Empty data set"}.
Blockchain reads use the same POST without "destination": "blockchain get uns", "blockchain get object", "blockchain get fleet_action". They return a list of policies such as [{"uns": {...}}].
Default database: anotherpeak (configurable).

## Tables (database anotherpeak)
Long-format device tables, one row per measurement. Columns: boat, ip, id, side, component (the measurement name), value (float), str_value (text), timestamp. A physical unit is (ip, id, side). Side B = port, T = starboard; empty = none.
- bmwix — battery packs, 4 per side. Helios: (ip/id) 3/33, 3/49, 4/49, 3/81 on both sides. HydraAix port: 3/33, 3/35, 3/65, 3/81; starboard: 3/33, 3/35, 4/49, 3/65. Measurements: gCurrent (A, negative = discharging), gMaxCellTemperature, gAverageTemperature (°C), gStateOfCharge, gStateOfHealth (%), gPackVoltage (V), gTimeToFullMinute, plus secondary actualCurrent, actualSoc, actualTempBattery, actualTempBatteryMax, and ekmvPresHigh (meaning unconfirmed).
- ach65 — propulsion motor per side: ggMotorPower (kW), gMotorVoltage (V), ggMotorTemperature, ggElectronicTemperature (°C), totalTimeEnabledHours.
- gd — generator, one per boat, no unit keys: EngineRPM (1500 when running; running = EngineRPM > 0), Load (%), FuelRate (L/h), TotalFuelUsed (L, cumulative), EngineRunHours, RunHours, T-Coolant, CoolTemp, ExhaustTemp, OilPress, P-Oil, BatteryVolt (24 V generator start battery, ~26 V normal), NumSuccStarts, NumUnscStarts (cumulative), ServiceTime, EngineState, SpeedRequest, D+, CPUTemp.
- bcl25 — AC chargers: gActDcPower (kW), gActAcCurrent, gActAcVoltage, currentL1-3, voltageL1-3, gActElectronicTemperature, gWake; state text in str_value where component = 'gState' (InitReset, PreOperational, Running). Helios has three units: ip 3 and ip 4 on port, ip 3 on starboard (all id 65). HydraAix currently loads as one unit with empty ip/id/side (a known ingestion issue; it may become three units later — don't hard-code either).
- elptx — power converter: dcVoltage, gPowerActual, gPowerRequested, powerActual, powerRequest; gState in str_value.
Single-value tables (columns: component, ip, id, side, boat, timestamp, value): batterystateofchargepercent (int %, per side), speedoverground (per side), powerbalance (kW, negative = discharging), starterbatteryvoltage (12 V, ~13.4 normal), rangebattery, trip, stbdrpmshaft, currentbatterypower, hvbatterycapacity, systemstate and vesselstate (text values).
location has no ip/id/side; value is the text "lat, lon".
The boat column may be space-padded ("Helios  "); trim in JS. WHERE boat = 'Helios' still matches.
Timestamps are UTC. Data currently runs 2026-07-10 to 2026-08-20, sampled about every 5 minutes.

## Data quirks (still present in the stored data — filter them)
- "Not available" markers: FuelRate 3276.8; Load, T-Coolant, CoolTemp, EngineSpeed 32768; OilPress/P-Oil 327.68; TotalFuelUsed 214748364.8; EngineRunHours 2147483648; gTimeToFullMinute 65535; ekmvPresHigh 32.767 (74% of HydraAix readings).
- Dropout zeros in gStateOfHealth, gMaxCellTemperature, gAverageTemperature and batterystateofchargepercent: exclude value = 0.
- Apply filters in the SQL WHERE clause so aggregates are correct, per component, e.g. ((component = 'FuelRate' and value < 3276.8) or (component = 'Load' and value < 32768)).

## The UNS drives structure
Load "blockchain get uns" and "blockchain get object". UNS nodes have id, name, namespace, parent and object_id; the tree is anotherpeak → boat → component → (sub-component) → measurement, e.g. anotherpeak/helios/battery/bms/current. Each object has table, where (e.g. "boat = 'Helios' and component = 'FuelRate' and value < 3276.8"), and for measurement leaves also component, value_column ("value" or "str_value"), unit, focus (["diesel", "battery_health", "comfort"]) and sometimes invalid_value.
- Build the boat list from the UNS (boat = the name in the object's where clause), merged with boats found in the data; fall back to a configured known-boats list only if the UNS can't be read.
- Use invalid_value from objects to override the built-in filters.
- Map (boat, table, component) → UNS namespace so every figure can show its source.
- Provide an Explorer tab: the UNS tree, and for any node its object, table, where, unit and focus tags, plus live data built from the object's table and where clause (numbers: an increments() chart per unit; text: current state and share of time per state; component nodes without a measurement: min/avg/max per component).

## Query strategy (all shapes below are verified against this network)
A small, fixed set of grouped queries per refresh, independent of fleet size; each device table is read once for all boats. Run in parallel with a concurrency limit of about 6; one failure must not blank the page.
- Time range: every query works on the selected From/To range (see "Time range picker" below). Default: 2026-07-10 00:00:00 → 2026-08-21 00:00:00 UTC, set as a single DEFAULT_RANGE constant that is easy to change.
- Anchor time ("right now"): select boat, max(timestamp) as t from location group by boat. If the fleet's latest timestamp falls inside the range, the anchor is that timestamp rounded up to the next minute (period() excludes its end point), capped at the range end; otherwise the anchor is the range end. A boat more than 30 minutes behind the fleet is "Not reporting".
- Snapshot (last 10 minutes), e.g.:
  select boat, ip, id, side, component, max(timestamp) as t, avg(value) as v, min(value) as mn, max(value) as mx from bmwix where period(minute, 10, '<anchor>', timestamp) and (component = 'gCurrent' or (component = 'gMaxCellTemperature' and value > 0) or (component = 'gStateOfHealth' and value > 0) or component = 'gStateOfCharge') group by boat, ip, id, side, component
  (returns all 16 packs × 4 measurements for both boats in one call)
- Text and numbers together:
  select boat, ip, id, side, component, str_value, max(timestamp) as t, avg(value) as v from bcl25 where period(minute, 10, '<anchor>', timestamp) and (component = 'gActDcPower' or component = 'gState') group by boat, ip, id, side, component, str_value
  (the gState row with the latest t is the current state)
- Range summary: the same shapes with the explicit range in the WHERE clause instead of period(): timestamp >= '<from>' and timestamp < '<to>'. Use period() only for the 10-minute snapshot (and the 6-hour latest-position read).
- Trends: increments() with the explicit range, grouped by boat and component; hourly buckets for ranges up to 3 days, daily beyond:
  select increments(day, 1, timestamp), boat, component, max(timestamp) as t, min(value) as mn, max(value) as mx from gd where timestamp >= '<from>' and timestamp < '<to>' and ((component = 'TotalFuelUsed' and value < 214748364.8) or (component = 'EngineRunHours' and value < 2147483648)) group by boat, component
  Litres per day = that day's max minus the previous day's max (the counter runs between readings).
- Distributions: select boat, value, count(*) as n from batterystateofchargepercent where <range> and (value >= 95 or (value <= 15 and value > 0)) group by boat, value
- Timelines for events: increments(minute, 10) for ranges up to 10 days, 20 minutes up to 45 days, 1 hour beyond, of EngineRPM max and FuelRate avg (gd), gActDcPower avg per charger unit (bcl25), speed avg (speedoverground, side = 'B'), and charge avg (batterystateofchargepercent), each grouped by boat. Bucket rows client-side by flooring max(timestamp) to the bucket size.
Rules: increments() and period() cannot be combined; no arithmetic in the SELECT list; no joins. Compute ratios and combine tables in JavaScript.

## Derived figures (client-side, from the timelines)
- Generator runs: consecutive running buckets (allow a one-bucket gap), with start, duration, charge at start and stop, litres (FuelRate × time). Flag runs that started above 50% charge.
- Charging source: charger power > 0.5 kW while the generator runs = diesel; otherwise shore. Report kWh of each.
- Avoidable diesel: litres burned while charge was above 40%, on a UTC day that later had shore charging while docked.
- Cruises: underway = speed > 1 kn; a stop of 15 minutes or more ends a cruise; ignore cruises under 20 minutes. Electric arrival = generator off during the cruise's last 20 minutes.
- Per pack: health, gap to the boat's median, average temperature vs the median of its side, hottest cell, peak discharge (−min gCurrent), peak charge.

## Status and decision
Each boat gets one status, with reasons that state their values and thresholds:
- Bring in: hottest cell above 45 °C now; underway on battery below 20% charge with the generator off; generator start battery below 23 V; coolant above 100 °C while running; oil pressure below a configurable minimum (off by default; units unconfirmed).
- Needs maintenance: pack health more than 2 points below its siblings; pack more than 3 °C warmer than its side; motor or drive electronics above 85 °C; charger electronics above 80 °C; failed generator starts increased; 12 V starter below 12 V.
- Watch: cell above 40 °C in the range; pack current above 50 A; generator below 40% load for more than half its run time; avoidable diesel above 20 L; generator starts above 50% charge; electric arrival rate below 70% (with at least 3 cruises).
- Not reporting: see anchor time.
Decision per boat: "Pull in now" for Bring in; "Check the boat's link" for Not reporting; every other boat gets a usage order ("Use first", "Use 2nd", …, "Use last"), with boats that need maintenance ranked after healthy ones and labelled "fix soon". Order within each group by a weighted penalty: scale each figure from 0 (best in the fleet) to 1 (worst) — diesel = mean of cost and avoidable cost; battery = mean of weakest health, hottest cell and peak discharge; comfort = electric arrival rate — then total = weights × parts. Show the penalty and its parts in the decision cell, and explain the method in one plain sentence under the table.

## Layout
Top bar: title, a Grafana-style time range picker, Refresh, Settings and connection status.

Time range picker:
- One button showing the current range (e.g. "Last 24 hours" or "Jul 10, 00:00 to Aug 21, 00:00", labelled UTC), with ‹ and › buttons either side that move the range by half its length. Disable › when the range ends at "now".
- Clicking the button opens a popover with two parts:
  - Custom range: From and To text fields, each with a calendar button (native date-time picker; its value is read as UTC). Fields accept absolute UTC times ("2026-08-20 14:00", "2026-08-20 14:00:30") or times relative to now ("now", "now-6h", "now-2d", "now-1w"; units m, h, d, w). Validate before applying: unreadable times and From ≥ To show an inline error and don't apply. Enter applies; Escape or a click outside closes.
  - Quick ranges, all ending at now: Last 1 hour, Last 8 hours, Last 12 hours, Last 24 hours, Last 7 days, Last 30 days. Mark the active one. Below them, "Recently used": the last four custom ranges (localStorage).
- Keep the range in the URL hash (#from=…&to=…) so links and bookmarks reopen the same range; a valid hash overrides DEFAULT_RANGE. The range is not a Settings item.
- Relative ranges re-resolve on every refresh; absolute ranges stay fixed.
- The comparison table header and the fleet totals title show the range ("Jul 10, 00:00 to Aug 21, 00:00 UTC").
- If the fleet's latest data is before the range starts (e.g. a "now" range on old data), show a banner saying so, with a button "Show the <length> before it" that sets an absolute range of the same length ending at the latest reading.

Fleet tab (landing): a comparison table with one column per boat (sorted by decision), headed by the boat name, status word and data freshness. Rows, top to bottom: Decision; Why (top 3 reasons, each with a Source link); Right now (charge port/starboard, generator on/off, charging kW or speed); Diesel (cost, litres and hours, avoidable diesel, share charged from diesel, average load, high-charge starts); Battery life (weakest pack health, largest gap to siblings, hottest cell, warmest pack vs its side, peak discharge, time at ≥95% and ≤15%, packs flagged); Electric arrivals (cruises, arrival rate); Equipment (hottest motor, drive, charger; failed starts); Actions. Tint cells that break a threshold and mark the fleet's best value in each row. Below: a map of latest positions coloured by status, and fleet totals.
Other tabs: Diesel (league table, litres per day chart, charging source chart, generator runs), Batteries (every pack, with outliers highlighted, and trend charts), Arrivals (rates and cruise list), Explorer (UNS), Actions.

## Actions
Buttons per boat: Bring in, Schedule maintenance, Acknowledge, Dismiss. A dialog shows the reasons to record (checkboxes), a note, the author, and the exact policy that will be written, e.g. {"fleet_action": {"boat", "action", "reasons", "note", "author", "created", "window", "data_until"}} (window = the selected range as "<from> to <to> UTC"; data_until = the anchor time).
- When blockchain writing is enabled in Settings: POST with headers command: "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn" and AnyLog-Agent, and body "<new_policy={...}>". Closing an action writes a new fleet_action with action "close" and "closes": <original id>. An action is open until a close policy references it.
- When disabled (the default): keep actions in localStorage, with JSON export.
Open actions show in the boat's column and on an Actions tab with an open-count badge.

## Technical requirements
- One self-contained HTML file, opened locally (a hosted https page can't call an http node). Leaflet and Chart.js from cdnjs; OpenStreetMap tiles.
- Settings drawer, saved to localStorage: connection (protocol, host, port, database, destination, agent, Content-Type application/json or text/plain, optional Authorization, timeout, "Test connection" sending "get status"), known boats, not-reporting minutes, diesel price, weights, every threshold above, cruise settings, blockchain writing on/off, author name, theme (system/light/dark; dark dims the base map).
- A query list showing each query's SQL, row count, time, the panels it feeds, and "copy as curl"; a footer with the query count and total time.
- Clear error states: name the failing query and the node, and hint at CORS when fetch itself fails. Partial failures leave the rest of the page working.
- All times in UTC, labelled. Status colours always paired with the status word. Port = red, starboard = green. Responsive; keyboard focus visible.
- Design: this is an operations desk, not a marketing dashboard. The comparison table is the one bold element; keep everything else quiet. Avoid identical card grids and decorative gradients.
- If you have the AnyLog MCP connector, verify table names, columns and the UNS before writing queries, and test each query shape once.