# AnotherPeak v2

The following is a secondary version of the work done for AnotherPeak. 

Each boat's data arrived as a single CSV exported from InfluxDB. We split it into one AnyLog table per signal or device, 
and reshaped multi-field devices such as the battery packs, chargers, motors and generator into one row per measurement, 
tagged with the boat, the physical unit (IP, ID and side) and the timestamp. We then published a UNS that organizes it 
as company → boat → component → measurement. Each node points to the exact table and filter behind it, and is tagged 
with the goal it serves: diesel, battery life or electric arrivals. That lets both boats be compared side by side from 
the same queries.

**Actual data is located**: 
- <a href="http://45.33.11.32/Sample-Data/vessel-data2/helios/" target="_blank">Helios</a> 
- <a href="http://45.33.11.32/Sample-Data/vessel-data2/hydraaix/" target="_blank">HydraAix</a>

## Data distribution

**AnyLog Version**: 2.1.2609-9cf217
**Remote-GUI**: 2.1.6

Boat         |Policy   Name                    Ip              Port  Rest_port  
-------------|--------|-----------------------|---------------|-----|---------|
             |master  |master-ACME-32223      | 172.233.253.95|32048|    32049|
             |query   |ori-vm1-acme-query-9624| 172.233.253.95|32348|    32349| 
boat-helios  |operator|anotherpeak-operator1  | 172.233.253.95|32148|    32149|  
boat-hydraaix|operator|anotherpeak-operator2  |104.105.205.183|32148|    32149|    
             |        |remote-gui             | 172.233.253.95|31800|         |  <- website: http://172.233.253.95:31800

## Content

1. Sample UNS policies  
2. Sample prompt + dashboard for both boat specific + overall administrative 
3. [data management scripts]()

## Setting up an MCP (Claude)

1. Download Claude Desktop 
2. Download mcp-proxy & get path 
```shell
python3 -m pip install --upgrade mcp-proxy 

# linux / Mac 
which mcp-proxy 
```

3. Update the configuration file with connection information command is to be updated with the value from which 
mcp-proxy IP and address args is to be associated with your desired query node

```editorconfig
{
  "mcpServers": {
    "anylog-api-mcp-proxy": {
      "command": "C:\\Users\\oshad\\AnyLog-code\\AnyLog-Network\\venv\\Scripts\\mcp-proxy.exe", 
      "args": ["http://23.239.12.151:32349/mcp/sse"], 
      "env": {},
      "timeout": 30000
    }
  }
}
```

