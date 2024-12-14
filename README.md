# AnotherPeak 

* [torqeedo_modbus_datalogger_v1.py](torqeedo_modbus_datalogger_v1.py) - Original code 
* [torqeedo_modbus_datalogger_v2.py](torqeedo_modbus_datalogger_v2.py) - updated code supporting AnyLog/EdgeLake 
instead of InfluxDB. "Complex" python methods that are not main can be found under [source](source/) 
* [servers](servers) - Python scripts that can act as dummy servers for Modbus and REST

## Requirements
* Active AnyLog / EdgeLake setup
* Install [requirements](requirements.txt)
   * Flask 
   * pyModBus
```shell
python3 -m pip install --uprade pip 
python3 -m pip install --upgrade -r ./requirements.txt
```

## Deployment

### Start Dummy Servers (Optional) 
* [modbus_server.py](servers/modbus_server.py)
```shell
python3 servers/modbus_server.py
```
* [rest_server.py](servers/rest_server.py)
```shell
python3 servers/rest_server.py
```

### Start Data processing
1. Update [params.py](source/params.py) with correct values: 
    * ANYLOG_CONN - IP and port connection information to communicate with AnyLog / EdgeLake via REST
    * MODBUS_CONN - IP and port connection information for modbus
    * Any other values
    
2. Start Process  - when enabling `--use-dummy`, the code will use the configurations for the dummy servers rather than 
the production environment 
```shell
python3 torqeedo_modbus_datalogger_v2.py [DB_NAME] [--use-dummy]
```
