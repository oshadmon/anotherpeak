import argparse
import requests
import json

BOAT_INFO = {
    'b': {
        "table": "Helios_B",
        "side": "starboard"
    },
    't': {
        "table": "Helios_T",
        "side": "port"
    }
}

def get_data(url:str)->(dict or list):
    """
    GET data to be stored into AnyLog/EdgeLake
    :args:
        url:str - connection information
    :params:
        response:requests.GET - raw output from data
        output:dict - generated output from data
    :return:
        output
    """
    try:
        response = requests.get(url=f"http://{url}")
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to get data from {url} (Error: {error})")
    else:
        try:
            output = response.json()
        except Exception as error:
            raise Exception(f"Failed to extract results from {url} (Error; {error})")
    return output

def create_payload(get_conn:str, data:dict, boat_side:str, filter_columns:list=None)->dict:
    """
    Given the data set, generate payload
    :args:
        get_conn:str - REST connection used to GET data
        data:dict - payload to convert for insert into AnyLog
        boat_side:str - startboard or port
        filter_columns:list - comma separated list of (data) keys to store in payload
    :params:
        payload:dict - generated payload
    :return:
        payload
    """
    payload = {'conn': get_conn, 'boat_side': boat_side}
    if not filter_columns:
        payload.update(data)
    else:
        for key in filter_columns:
            if key in data:
                payload[key] = data[key]
    return payload

def publish_data(conn:str, payloads:list, db_name:str, table_name:str):
    """
    Code to publish into AnyLog/EdgeLake
    :args:
        conn:str - REST connection information
        payloads:list - data to publish
        db_name:str - logical database name
        table_name:str - logical table name (based on boat side)
    :params:
        headers:dict - REST header
        response:requests.PUT - get response
    """
    headers = {
        'type': 'json',
        'dbms': db_name,
        'table': table_name,
        'mode': 'streaming',
        'Content-Type': 'text/plain'
    }

    try:
        response = requests.put(url=f'http://{conn}', headers=headers, data=json.dumps(payloads))
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute PUT against {conn} (Error: {error})")


def main():
    """
    :positional arguments:
        get_conn              REST IP + Port for getting data
        post_conn             REST IP + Port to post data (into AnyLog/EdgeLake)
    :optional arguments:
        -h, --help                              show this help message and exit
        --db-name           DB_NAME             logical database to store data in
        --boat-side         {b,t}               boat size
        --filter-columns    FILTER_COLUMNS      Comma separated list of columns to be used be sent into AnyLog/EdgeLake based on results
    :global:
        BOAT_INFO:dict - general boat information
    :params:
        table_name:str - table name
        boat_side:str - startboard or port
        data:dict - data from get_conn
        payloads:list - data to publish into AnyLog
        filter_list:str - comma seperated filter list
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('get_conn', type=str, default=None, help='REST IP + Port for getting data')
    parser.add_argument('post_conn', type=str, default=None, help='REST IP + Port to post data (into AnyLog/EdgeLake)')
    parser.add_argument('--db-name', type=str, default='anotherpeak', help='logical database to store data in ')
    parser.add_argument('--boat-side', type=str, default='b', choices=['b', 't'], help='boat size')
    parser.add_argument('--filter-columns', type=str, default=None, help='Comma separated list of columns to be used be sent into AnyLog/EdgeLake based on results')
    args = parser.parse_args()

    table_name = BOAT_INFO[args.boat_side]['table']
    boat_side = BOAT_INFO[args.boat_side]['side']

    data = get_data(url=args.get_conn)
    payloads = []
    filter_list = args.filter_columns.split(",") if args.filter_columns is not None else None
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                payloads.append(create_payload(args.get_conn, data=row, boat_side=boat_side, filter_columns=filter_list))
    elif isinstance(data, dict):
        payloads.append(create_payload(args.get_conn, data=data, boat_side=boat_side, filter_columns=filter_list))

    publish_data(conn=args.post_conn, payloads=payloads, db_name=args.db_name, table_name=table_name)



if __name__ == '__main__':
    main()


