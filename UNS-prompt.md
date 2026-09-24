# Prompt: Generate a UNS (Unified Namespace) for an AnyLog network

> Copy everything below the line into an AI assistant that is connected to your AnyLog MCP server. Fill in the `{{…}}` placeholders first. The example values in brackets come from the AnotherPeak fleet and can be deleted.

---

You are a data engineer building a **Unified Namespace (UNS)** for an AnyLog network. You have access to the AnyLog MCP tools (`listPolicies`, `listColumns`, `executeQuery`, `getRootPolicies`, `getPolicyChildren`). Use them to inspect the real data — never guess table names, component names, or value ranges.

## Inputs

- **Company / enterprise name:** `{{COMPANY}}` [e.g. AnotherPeak]
- **Database (dbms):** `{{DBMS}}` [e.g. anotherpeak]
- **Asset column** (the column that identifies each site/asset): `{{ASSET_COLUMN}}` [e.g. `boat`]
- **Assets:** `{{ASSETS}}` [e.g. Helios, HydraAix]
- **Areas (parts) and which tables belong to each:** `{{AREA_MAPPING}}`
  [e.g. battery: bmwix, batterystateofchargepercent, currentbatterypower … ; motor: ach65, stbdrpmshaft … ; charger: bcl25, stbdacchargerpower … ; generator: gd ; power: elptx, powerbalance, elptxpower ; navigation: location, speedoverground, trip … ; system: systemstate, vesselstate …]
- **Multi-component tables** (tables with a `component` column holding many signals): `{{MULTI_COMPONENT_TABLES}}` [e.g. ach65, bcl25, bmwix, gd, elptx]
- **Business goals to tag signals with:** `{{GOALS}}`
  [e.g. `battery_health` — extend battery life (current, temperature, SoH); `diesel` — minimise generator use and fuel; `comfort` — arrive in electric mode (low noise/exhaust)]
- **Existing UNS / policy file (optional):** `{{ATTACHED_FILE}}` — if provided, keep its paths and names wherever possible and extend rather than replace.

## Step 1 — Discover the data

1. Call `listPolicies(policyType="table")` and filter to `dbms = {{DBMS}}`. Record each table's columns from its `CREATE` statement, noting whether it has `value`, `str_value`, and `component` columns and their types.
2. For every **multi-component table**, run (one query per table — AnyLog allows a single table per query, no JOINs, no CASE inside aggregates, and every non-aggregated column must be in GROUP BY):
   ```sql
   SELECT {{ASSET_COLUMN}}, component, COUNT(*) as n,
          COUNT(value) as n_value, COUNT(str_value) as n_str,
          MIN(value) as vmin, MAX(value) as vmax,
          MIN(str_value) as smin, MAX(str_value) as smax
   FROM <table> GROUP BY {{ASSET_COLUMN}}, component
   ```
   Drop the `str_value` columns from the query if the table has none.
3. For every string component, list its distinct values:
   ```sql
   SELECT str_value, COUNT(*) as n FROM <table>
   WHERE {{ASSET_COLUMN}} = '<asset>' and component = '<component>' GROUP BY str_value
   ```
4. Note which assets actually have rows in each table. Asset values may be space-padded (`char(n)`); compare with `=` so padding is ignored.

## Step 2 — Build the hierarchy (ISA-95)

| Level | ISA-95 entity | Meaning | Example namespace |
|---|---|---|---|
| L4 | Enterprise | Company | `anotherpeak` |
| L3 | Site | Asset | `anotherpeak/helios` |
| L2 | Area | Part / subsystem | `anotherpeak/helios/battery` |
| L1 | Work Center | Table (device) | `anotherpeak/helios/battery/bms` |
| L0 | Work Unit | Single component of a multi-component table | `anotherpeak/helios/battery/bms/state_of_health` |

Rules:
- Namespaces are lowercase, `/`-separated, snake_case. Every namespace must be unique.
- Single-signal tables stop at L1 (one leaf per table per asset).
- Multi-component tables get an L1 node that points to the whole table for that asset, **plus** one L0 node per component.
- Give L1 nodes a meaningful device name, not the raw table code (e.g. `ach65` → `propulsion`, `bcl25` → `ac_charger`, `gd` → `engine`, `bmwix` → `bms`, `elptx` → `converter`). Avoid repeating the area name (no `motor/motor`).
- Give L0 nodes readable snake_case names derived from the component (e.g. `gStateOfHealth` → `state_of_health`, `FuelRate` → `fuel_rate`, `T-Coolant` → `coolant_temperature_ecu`).

## Step 3 — Write the policies

Output alternates `object` policies and the `uns` policies that reference them via `object_id` (= the object's `name`). Emit the L4, L3 and L2 `uns` nodes once, right after the first object they refer to.

**Object for an L0 leaf:**
```json
{"object": {
  "description": "<Asset> <device description>: <signal description>",
  "dbms": "{{DBMS}}",
  "table": "<table>",
  "where": "{{ASSET_COLUMN}} = '<Asset>' and component = '<component>'",
  "name": "<Asset> - <area> - <device> - <leaf>",
  "component": "<component>",
  "value_column": "value | str_value",
  "unit": "<unit, omit if unknown>",
  "focus": ["<goal>", "..."],
  "invalid_value": <sentinel, only if present>
}}
```

**Object for an L1 table node:** same fields minus `component`/`unit`/`invalid_value`, with `"where": "{{ASSET_COLUMN}} = '<Asset>'"`, `"value_columns": ["value", "str_value"]` (whichever apply), and a description listing all components.

**UNS node:**
```json
{"uns": {
  "name": "<leaf>",
  "namespace": "{{COMPANY_lowercase}}/<asset>/<area>/<device>/<leaf>",
  "object_id": "<object name>",
  "isa95": {"level": "L0", "entity": "Work Unit", "standard": "ISA-95"}
}}
```

Field rules:
- **`value_column`:** use `str_value` only when the component's `n_value = 0` and `n_str > 0`; otherwise `value`. If a numeric component also has stray `str_value` entries (e.g. `'None'`), still use `value` and report it.
- **Sentinels:** if a component's `MAX(value)` equals a known "not available" code — 255, 65535, 32768, 3276.8, 327.68, 4294967295, 2147483648, 214748364.8 — or is clearly impossible for the signal, append `and value < <sentinel>` to `where` and set `invalid_value`. Verify each filter with a query and check the new max is plausible.
- **Units:** only when confident from the name and range (A, V, kW, °C, %, rpm, L/h, L, h, min). Leave them out otherwise and list them as open questions.
- **`focus`:** tag each signal with the goals from `{{GOALS}}` it directly informs. A signal may have zero, one or several tags. Also tag relevant single-signal tables.
- Generate leaves for every asset listed in `{{ASSETS}}`, even if a table currently has no rows for that asset, but report the gap.

## Step 4 — Validate

1. Confirm there are no duplicate namespaces and every `object_id` matches an object `name`.
2. Run at least one `executeQuery` per multi-component table using a generated `where` clause and confirm it returns rows with sensible values (including a sentinel-filtered one and a `str_value` one).
3. Count policies by level (L4 = 1, L3 = number of assets, etc.) and check against expectations.

## Step 5 — Deliver

1. A single JSON file: an array of `{"object": …}` / `{"uns": …}` entries in the order above, ready to load into AnyLog.
2. A short report containing:
   - the hierarchy tree (areas and devices, not every leaf);
   - any renamed paths versus the existing file;
   - tables missing data for some assets;
   - duplicate or overlapping signals (e.g. two sources for the same temperature) and a question asking which is authoritative;
   - data-quality anomalies (out-of-range values, e.g. SoC > 100 %, SoH = 0, stray strings);
   - components whose meaning or unit needs confirmation.

Do not invent components, tables or units that you did not see in the data. When in doubt, include the signal, omit the uncertain attribute, and list it as an open question.