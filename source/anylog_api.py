"""
Disclaimer: blockchain related methods ccould may need to be updated based on production env as it is based on
the generated file names
"""
import json

from source.logger_config import logger
from source.rest_api import anylog_blockchain_get, anylog_blockchain_post, anylog_data_put

from source.file_io import write_file

def is_policy(conn:str, table_name, category, boat_id=None, component=None, ip=None):
    """
    Based on the given params, check whether policies exist
    :args:
        conn:str - REST connections
        table_name:str - generated table name
        category:str - B/T category
        boat_id:int - boat ID
        component:str - component name
        ip:str - boat ID
    :params:
        status:bool
        cmd:str - generated `blockchain get` command
    :return:
        True if exists False if does not
    """
    status = False
    cmd = f"blockchain get boat where name={table_name} and category={category}"
    cmd += f" and boat_id={boat_id}" if boat_id else ""
    cmd += f" and component={component}" if component else ""
    cmd += f" and ip={ip}" if ip else ""

    output = anylog_blockchain_get(conn=conn, cmd=cmd)
    if output:
        status = True

    return status


def declare_policy(conn:str, table_name, category, boat_id=None, component=None, ip=None):
    """
    Declare policy on the blockchain
    :sample policy:
     {'boat' : {
        'name' : 'T_BMWix_IP_4_ID_49_dummy',
        'category' : 'T',
        'boat_id' : 49,
        'component' : 'BMWix',
        'ip' : 4,
        'id' : 'f0f4fa22a974b46715eb9d239ca14000',
        'date' : '2024-12-13T23:16:19.237579Z',
        'ledger' : 'global'
    }}
    :args:
        cconn:str - connection to AnyLog node
        table_name:str - generated table name
        boat_id:int
        component:str
        IP:str
    :params:
        new_policy:dict - generated policy
        str_new_policy:str - policy as as striing to be published into AnyLog/EdgeLake
    """
    new_policy = {
        "boat": {
            "name": table_name.lower(),
            "category": category
        }
    }

    if boat_id:
        new_policy['boat']["boat_id"] = boat_id
    if component:
        new_policy['boat']["component"] = component
    if ip:
        new_policy['boat']["ip"] = ip

    str_new_policy = f"<new_policy={json.dumps(new_policy)}>"
    anylog_blockchain_post(conn=conn, payload=str_new_policy)


def blockchain_policy(conn:str, category:str, filename:str, is_dummy:bool=False):
    """
    Generate a new boat policy if one does not exist based on a set of params
    :extract from file name:
        file name: 2024-08-15_Helios_DLB_BMWix_IP_4_ID_49.json
        |--> table name:  t_bmwix_ip_4_id_49_dummy
        |--> category: T
        |--> component: BMWix
        |--> boat_id: 49
        |--> IP: 4
    :args:
        conn:str - Connection to node
        category:str - T or B
        filemane:str - file to generate table name / policy from
        is_dummy:bool - if dummy, then add _dummy aat the end of the table name
    :params:
        table_name:str - generated table name
        boat_id:int
        component:str
        IP:str
    """
    table_name = filename.split("_Helios_", 1)[-1].rsplit("_DEVICE", 1)[0].split('.json')[0]
    if f'DL_{category}_' in table_name:
        table_name = table_name.split(f"DL_{category}_")[-1]
    boat_id = None
    component = None
    ip = None

    if table_name != 'generatrice_modbus' and 'vessel' not in table_name:
        boat_id = int(table_name.split("_ID_")[-1])
        component = table_name.split("_IP")[0]
        ip = table_name.split("_IP_")[-1].split("_")[0]
    elif 'vessel' in table_name:
        component = 'vessel'
    elif 'generatrice_modbus' in table_name:
        component = 'generatrice_modbus'

    table_name = f"{category}_{table_name}"
    if is_dummy is True:
        table_name = f"{table_name}_dummy"

    if is_policy(conn=conn, table_name=table_name, category=category, boat_id=boat_id, component=component, ip=ip) is False:
        declare_policy(conn=conn, table_name=table_name, category=category, boat_id=boat_id, component=component, ip=ip)

    return table_name


def anylog_publish_data(conn:str, data, db_name:str):
    """
    Publish data into AnyLog/EdgeLake
    :args:
        conn:str - REST connection information for AnyLog
        data:dict - data generated in the first part of torqeedo_modbus_datalogger_v2.py
        db_name:str - logical database to store data in
    :params:
        payload - serialized list of data to publish onto a node
    """
    for table_name in data:
        write_file(table_name=table_name, db_name=db_name, data=data[table_name]) # write data to file
        try:
            payload = json.dumps(data[table_name])
        except json.JSONDecodeError as error:
            logger.critical(f'Échec de la sérialisation de JSON (Erreur: {error})')
        else:
            anylog_data_put(conn=conn, data=payload, db_name=db_name, table_name=table_name)








