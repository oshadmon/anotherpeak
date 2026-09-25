# AnotherPeak v2

A second version of the AnotherPeak work: two diesel-electric passenger boats (Helios and HydraAix) monitored through
an AnyLog network, a UNS, and dashboards for captains and fleet managers.

Each boat's data arrived as a single CSV exported from InfluxDB. We split it into one AnyLog table per signal or device,
and reshaped multi-field devices such as the battery packs, chargers, motors and generator into one row per measurement,
tagged with the boat, the physical unit (IP, ID and side) and the timestamp. We then published a UNS that organizes it
as company → boat → component → measurement. Each node points to the exact table and filter behind it, and is tagged
with the goal it serves: diesel, battery life or electric arrivals. That lets both boats be compared side by side from
the same queries.

**Source data**: The original data has a timestamp range of  "2026-07-10 00:00:00" to "2026-08-21 00:00:00" UTC
- [Helios](http://45.33.11.32/Sample-Data/vessel-data2/helios/)
- [HydraAix](http://45.33.11.32/Sample-Data/vessel-data2/hydraaix/)

**Live Dashboards**: 
- [Captain View](http://45.33.11.32/Sample-Data/vessel-data2/captain-dashboard.html)
- [Fleet View](http://45.33.11.32/Sample-Data/vessel-data2/fleet-dashboard.html)

## Network

- **AnyLog version:** 2.1.2609-9cf217
- **Remote-GUI:** 2.1.6, at http://172.233.253.95:31800
- **Database:** `anotherpeak`

| Role     | Node name                 | IP              | TCP port | REST port | Stores       |
|----------|---------------------------|-----------------|----------|-----------|--------------|
| Master   | master-ACME-32223         | 172.233.253.95  | 32048    | 32049     |              |
| Query    | ori-vm1-acme-query-9624   | 172.233.253.95  | 32348    | 32349     |              |
| Operator | anotherpeak-operator1     | 172.233.253.95  | 32148    | 32149     | Helios       |
| Operator | anotherpeak-operator2     | 104.105.205.183 | 32148    | 32149     | HydraAix     |
| GUI      | remote-gui                | 172.233.253.95  | 31800    |           |              |

Dashboards and the MCP connect to the query node's REST port (`172.233.253.95:32349`). Data is inserted through the
operators' REST ports.

## Contents

- Sample UNS policies
- Prompts and dashboards: one per boat (captain) and one for the whole fleet (management)
- [Data management scripts](./scripts/)

## Connecting Claude through MCP

1. Install Claude Desktop.
2. Install `mcp-proxy` and find its path:
   ```shell
   python3 -m pip install --upgrade mcp-proxy

   which mcp-proxy    # Linux / macOS
   where mcp-proxy    # Windows
   ```
3. Add the server to Claude Desktop's configuration file. Set `command` to the path from step 2, and point `args` at
   the query node's REST port:
   ```json
   {
     "mcpServers": {
       "anylog-api-mcp-proxy": {
         "command": "/path/to/mcp-proxy",
         "args": ["http://172.233.253.95:32349/mcp/sse"],
         "env": {},
         "timeout": 30000
       }
     }
   }
   ```
4. Restart Claude Desktop.

## Loading the data

Always load HydraAix first. AnyLog creates each table's columns from the first rows it receives, so the `boat` column
takes its width from the first boat name it sees. "HydraAix" (8 characters) makes it `char(8)`; loading "Helios"
(6 characters) first would create a column too narrow for HydraAix. This is also why Helios comes back padded as
`"Helios  "` in query results.

1. [data.py](./scripts/data.py) inserts the tables that don't need reshaping.
2. Run the remaining scripts to reshape and insert the device tables (`bmwix`, `bcl25`, `ach65`, `elptx`, `gd`).

## Known issues

- **"Not available" values are stored.** CAN markers such as 65535, 3276.8, 32768, 327.68, 214748364.8 and
  2147483648 are in the data, as is 32.767 for `ekmvPresHigh` on HydraAix. The UNS object policies and the dashboards
  filter them; dropping them at ingestion would be better.
- **HydraAix's chargers load as one unit.** Its raw messages carry three chargers under repeated keys with no IP/ID/side,
  and only one survives parsing. Splitting them needs `object_pairs_hook` when reading the JSON.
- **Text values** (for example charger state `gState`) are stored in a separate `str_value` column of the same table.

## To do

- Unify the scripts into one process that can insert new data continuously, based on the sample.
- Add aggregation once the customer confirms what should be aggregated from new data.
