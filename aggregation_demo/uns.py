"""
AnotherPeak (root)
-> boat
    -> device (tables)
        -> sensor
"""
import json
from rest_call import execute_command
import posixpath

def define_uns(name:str, uns_layer:str, base_namespace:str=None, parent:str=None, db_name:str=None,
                table_name:str=None, column:str=None, where_condition:str=None):

    uns = {
        "uns": {
            "name": name,
            "namespace": posixpath.join(base_namespace, name.replace(' ', '-')) if base_namespace else name.lower(),
            "uns_layer": uns_layer,
            **({"parent": parent} if parent else {}),
            **({"dbms": db_name} if db_name else {}),
            **({"table": table_name} if table_name else {}),
            **({"column": column} if column else {}),
            **({"where": where_condition} if where_condition else {})
        }
    }
    if column:
        uns["uns"]["namespace"] = posixpath.join(base_namespace, column)
    return uns

def uns_generic(conn:str, name:str, uns_layer:str, base_namespace:str=None, parent:str=None, db_name:str=None,
                table_name:str=None, column:str=None, where_condition:str=None):

    new_policy = define_uns(name=name, uns_layer=uns_layer, base_namespace=base_namespace, parent=parent,
                            db_name=db_name, table_name=table_name, column=column, where_condition=where_condition)

    get_headers = {
        "command": f'blockchain get uns where name="{name}" and uns_layer="{uns_layer}" bring [*][id]',
        "User-Agent": "AnyLog/1.23"
    }

    # if " " in name.strip():
    #     get_headers["command"] = get_headers["command"].replace(f"name={name}", f"name='{name}'")

    blockchain_headers = {
        "command": "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        "User-Agent": "AnyLog/1.23"
    }

    response = execute_command(method="GET", conn=conn, headers=get_headers)
    policy_id = response.text
    if policy_id == "[]":

        execute_command(method="POST", conn=conn, headers=blockchain_headers, payload=f"<new_policy={json.dumps(new_policy)}>")
        response = execute_command(method="GET", conn=conn, headers=get_headers)
        policy_id = response.text

    return policy_id, new_policy.get("uns").get("namespace")

def get_boats(conn:str):
    vessels = []
    headers = {
        "command": "sql anotherpeak format=json:list and stat=false SELECT distinct(vessel) as vessel FROM engine_telemetry",
        "User-Agent": "AnyLog/1.23",
        "destination": "network"
    }
    response = execute_command(method="GET", conn=conn, headers=headers)
    for vessel in response.json():
        vessels.append(vessel.get("vessel"))
    return vessels

def get_vessels(conn:str):
    vessels = []
    headers = {
        "command": "sql anotherpeak format=json:list and stat=false SELECT distinct(vessel) as vessel FROM engine_telemetry",
        "User-Agent": "AnyLog/1.23",
        "destination": "network"
    }
    response = execute_command(method="GET", conn=conn, headers=headers)
    for vessel in response.json():
        vessels.append(vessel.get("vessel"))
    return vessels


def get_tables(conn:str):
    tables = []
    headers = {
        "command": "blockchain get table where dbms=anotherpeak bring.json [*][name]",
        "User-Agent": "AnyLog/1.23"
    }
    response = execute_command(method="GET", conn=conn, headers=headers)
    for table in response.json():
        tables.append(table.get("name"))
    return tables


def get_columns(conn:str, table:str):
    sensors= []
    headers = {
        "command": f"get columns where dbms=anotherpeak and table={table} and format=json",
        "User-Agent": "AnyLog/1.23"
    }

    response = execute_command(method="GET", conn=conn, headers=headers)
    columns = response.json()
    for column in columns:
        if column not in ['row_id', 'insert_timestamp', 'tsd_name', 'tsd_id', 'timestamp', 'vessel']:
            sensors.append(column)
    return sensors


if __name__ == "__main__":
   root_policy, root_namespace = uns_generic(conn="50.116.20.125:32149", name="Anotherpeak", uns_layer="root", base_namespace=None,
                                             parent=None, db_name=None, table_name=None, column=None, where_condition=None)

   for table in get_tables(conn="50.116.20.125:32149"):
       table_policy, table_namespace = uns_generic(conn="50.116.20.125:32149", name=table, uns_layer="namespace",
                                                   base_namespace=root_namespace, parent=root_policy, db_name=None,
                                                   table_name=None, column=None, where_condition=None)
       for vessel in get_vessels(conn="50.116.20.125:32149"):
           vessel_id, vessel_namespace = uns_generic(conn="50.116.20.125:32149", name=vessel, uns_layer="vessel",
                                                     base_namespace=table_namespace, parent=table_policy,
                                                     db_name="anotherpeak", table_name=table, column=None,
                                                     where_condition=f"vessel='{vessel}'")
           for sensor in get_columns(conn="50.116.20.125:32149", table=table):
               print(sensor, vessel, vessel_id)
               sensor_id, sensor_namespace = uns_generic(conn="50.116.20.125:32149", name=posixpath.join(table, vessel, sensor),
                                                         uns_layer="sensor", base_namespace=vessel_namespace, parent=vessel_id,
                                                         db_name="anotherpeak", table_name=table, column=sensor,
                                                         where_condition=f"vessel='{vessel}'")