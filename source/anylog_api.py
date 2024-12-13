import json

from servers.modbus_server import logger
from source.rest_api import anylog_get, anylog_post, anylog_put


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

    output = anylog_get(conn=conn, cmd=cmd)
    if output:
        status = True

    return status


def declare_policy(conn:str, table_name, category, boat_id=None, component=None, ip=None):
    new_policy = {
        "boat": {
            "name": table_name,
            "category": category
        }
    }

    if boat_id:
        new_policy['boat']["boat_id"] = boat_id
    if component:
        new_policy['component']["component"] = component
    if ip:
        new_policy['component']["ip"] = ip

    str_new_policy = f"<new_policy={json.dumps(new_policy)}>"
    anylog_post(conn=conn, data=str_new_policy)


def blockchain_policy(category, filename):
    table_name = filename.split("_Helios_", 1)[-1].rsplit("_DEVICE", 1)[0].split('.json')[0]
    if f'DL_{category}_' in table_name:
        table_name = table_name.split(f"DL_{category}_")[-1]
    boat_id = None
    component = None
    ip = None

    if table_name != 'generatrice_modbus' and 'vessel' not in table_name:
        boat_id = int(table_name.split("_ID_")[-1])
        component = table_name.split("_IP")[0]
        ip = int(table_name.split("_IP_")[-1].split("_")[0])
    if is_policy(conn='178.79.168.109:32149', table_name=table_name, category=category, boat_id=boat_id, component=component, ip=ip) is False:
        declare_policy(conn='178.79.168.109:32149', table_name=table_name, category=category, boat_id=boat_id, component=component, ip=ip)

    return table_name

def anylog_publish_data(conn:str, data:dict, db_name:str):
    for table_name in data:
        try:
            str_data = [json.dumps(row) for row in data[table_name]]
        except json.JSONDecodeError as error:
            logger.critical(f'Échec de la sérialisation de JSON (Erreur: {error})')
        else:
            print(str_data)
            exit(1)
            # anylog_put(conn=conn, data=str_data, db_name=db_name, table_name=table_name)







