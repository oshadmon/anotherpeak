import argparse
import json
import posixpath

import support

def create_uns(name:str, uns_level:str, base_namespace:str=None, parent:str=None, dbms:str=None, table:str=None,
               column:str=None, where:str=None):
    uns = {
        "uns": {
            "name": name,
            "uns_level": uns_level,
            "namespace": (
                posixpath.join(base_namespace, name)
                if base_namespace else name
            ),
            **({"parent": parent} if parent else {}),
            **({"dbms": dbms} if dbms else {}),
            **({"table": table} if table else {}),
            **({"column": column} if column else {}),
            **({"where": where} if where else {})
        }
    }

    return uns


def get_uns(conn:str, name:str, uns_level:str, namespace:str):
    headers = {
        "command": f'blockchain get uns where name="{name}" and uns_level={uns_level} and namespace="{namespace}" bring.json',
        "User-Agent": "AnyLog/1.23"
    }

    response = support.execute_command(method="GET", conn=conn, headers=headers)
    return response.json()

def publish_policy(conn:str, policy:dict):
    policy_info = get_uns(conn=conn, name=policy["uns"]["name"], uns_level=policy["uns"]["uns_level"],
                          namespace=policy["uns"]["namespace"])

    if not policy_info:
        publish_policy_headers = {
            "command": "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
            "User-Agent": "AnyLog/1.23"
        }
        new_policy = f"<new_policy={json.dumps(policy)}>"
        support.execute_command(method="POST", conn=conn, headers=publish_policy_headers, payload=new_policy)

        policy_info = get_uns(conn=conn, name=policy["uns"]["name"], uns_level=policy["uns"]["uns_level"],
                              namespace=policy["uns"]["namespace"])

    return policy_info[0].get("uns").get("id"), policy_info[0].get("uns").get("namespace")


def get_tables(conn:str):
    headers = {
        "command": "blockchain get table bring [*][name] separator=,",
        "User-Agent": "AnyLog/1.23"
    }

    response = support.execute_command(method="GET", conn=conn, headers=headers)
    return response.text.split(',')


def get_columns(conn:str, table:str):
    columns = []
    headers = {
        "command": f"get columns where dbms=anotherpeak and table={table} and format=json",
        "User-Agent": "AnyLog/1.23"
    }

    response = support.execute_command(method="GET", conn=conn, headers=headers)
    for column in response.json():
        if column not in ["row_id", "insert_timestamp", "tsd_name", "tsd_id", "timestamp", "vessel"]:
            columns.append(column)
    return columns

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=str, default=None, help="REST connection")
    args = parse.parse_args()


    policy = create_uns(name="AnotherPeak", uns_level="root", base_namespace=None)
    root_id, root_namespace = publish_policy(conn=args.conn, policy=policy)
    policy = create_uns(name="Helix", uns_level="vessel", base_namespace=root_namespace, parent=root_id)
    vessel_id, vessel_namespace = publish_policy(args.conn, policy=policy)
    for side in ["DLB", "DLT"]:
        policy  = create_uns(name=side, uns_level="side", base_namespace=vessel_namespace, parent=vessel_id)
        side_id, side_namespace = publish_policy(args.conn, policy=policy)

        tables = get_tables(conn=args.conn)
        for table in tables:
            policy = create_uns(name=f"Helix_{side} - {table}", uns_level="device", base_namespace=side_namespace,
                                parent=side_id, dbms="anotherpeak", table=table, where=f"vessel='Helix_{side}'")
            table_id, table_namespace = publish_policy(args.conn, policy=policy)
            columns = get_columns(conn=args.conn, table=table)
            for column in columns:
                policy = create_uns(name=f"Helix_{side} - {table}: {column}", uns_level="sensor",
                                    base_namespace=table_namespace, parent=table_id, dbms="anotherpeak", table=table,
                                    column=column, where=f"vessel='Helix_{side}'")
                publish_policy(args.conn, policy=policy)


if __name__ == "__main__":
    main()