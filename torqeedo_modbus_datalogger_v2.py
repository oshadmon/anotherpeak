"""
Major Changes:
1. when executing a GET REST request, there's no need to convert from dict (request.json()) to serialized JSON and back
to dict
2. the if /else for device is inside the parse processes
3. The code skips sending data to file / influxdb and instead sends directly into AnyLog/EdgeLake
4. The code publishes metadata into AnyLog/EdgeLake's blockchain with information regarding the boat
"""
import argparse
import datetime
import socket

from source.logger_config import logger, setup_logger
from source.data_parse import parse_vessel_json,parse_ACH65_json,parse_BCL25_json,parse_BMWix_json,parse_ElPtx350_json
from source.rest_api import fetch_raw_json
from source.modbus import modbus_main
from source.params import Helios_default, Helios_DL_devices, Helios_DL_IP, ANYLOG_CONN, MODBUS_CONN
from source.anylog_api import blockchain_policy, anylog_publish_data

def check_ping(is_dummy:bool=False):
    """
    Check whether REST server is active
    :args:
        is_dummy:bool
    :status:
        if accessible - True
        not accessible - exit program
    """
    if is_dummy is True:
        ip = '127.0.0.1'
        port = 8481
        try:
            with socket.create_connection((ip, port), timeout=5):
                pass
        except (socket.timeout, socket.error):
            logger.error(f"Connection failed to {ip} on port {port}")
            exit(1)
    else:
        for i in ["B", "T"]:
            ip, port = Helios_DL_IP[i].split(":")
            try:
                with socket.create_connection((ip, port), timeout=5):
                    pass
            except (socket.timeout, socket.error):
                logger.error(f"Connection failed to {ip} on port {port}")
                exit(1)


def main():
    """
    The following code is able to pull data from REST server (fetch_raw_json)  and Modbus (modbus.py) and store the
    data into AnyLog/EdgeLake.
    :process:
        1. get data and store into dict, where keys are table name(s) - data from both REST and Modbus
        2. when table name is generated, create a policy onm the metadata if DNE
        3. publish data to corresponding operator(s)
    :positional arguments:
        db_name               logical database to store data in
    :optional arguments:
        -h, --help                      show this help message and exit
        --use-dummy     [USE_DUMMY]     Use dummy servers / files rather than production device
    :global:
        ANYLOG_CONN - Connection to AnyLog node(s)
        MODBUS_CONN:str - connection to Modbus
    """
    parse = argparse.ArgumentParser()
    parse.add_argument('db_name', type=str, default='another_peak',
                       help='logical database to store data in')
    parse.add_argument('--use-dummy', type=bool, const=True,  default=False, nargs='?',
                       help='Use dummy servers / files rather than production device')
    args = parse.parse_args()

    setup_logger()
    check_ping(is_dummy=args.use_dummy)

    current_time = datetime.datetime.now()
    json_body = {
        'B': {},
        'T': {}
    }
    for i in ["B", "T"]:  # On parcourt Babord et Tribord et comme les componnents  ont le même nom, on rajoute "B" ou "T" pour les différencier
        for f in Helios_default:
            if f != "vessel":
                break
            url = f"http://127.0.0.1:8481/{f}" if args.use_dummy is True else f"http://{Helios_DL_IP[i]}/{f}"

            # On sauvegarde la donnée brute dans un fichier, un fichier par composant par jour
            filename = f"{current_time.strftime('%Y-%m-%d')}_Helios_DL_{i}_{f}.json"

            table_name = blockchain_policy(conn=ANYLOG_CONN[i], category=i, filename=filename, is_dummy=args.use_dummy)
            if table_name not in json_body[i]:
                json_body[i][table_name] = []
            json_data = fetch_raw_json(url)
            if json_data and f == "vessel":
                data = parse_vessel_json(json_data, i)
            else:
                logger.error("%s Failed to fetch data from %s", f, url)
            if 'timestamp' not in data or not data['timestamp']:
                data['timestamp'] = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            if 'category' not in data or not data['category']:
                data['category'] = i
            json_body[i][table_name].append(data)
        # on parcourt ici les composants hardware: batteries, chargeurs, convertisseurs, moteurs
        for f in Helios_DL_devices[i]:
            url = f"http://127.0.0.1:8481/{i}/{f}" if args.use_dummy is True else f"http://{Helios_DL_IP[i]}/device/{f}"
            filename = f"{current_time.strftime('%Y-%m-%d')}_Helios_DL_{i}_{f}.json"

            table_name = blockchain_policy(conn=ANYLOG_CONN[i], category=i, filename=filename, is_dummy=args.use_dummy)
            if table_name not in json_body[i]:
                json_body[i][table_name] = []

            json_data = fetch_raw_json(url)
            is_device = True if 'DEVICE' in f else False
            if not json_data:
                logger.error("device Failed to fetch data from %s", url)
            elif 'ACH65' in f:
                data = parse_ACH65_json(json_data, i, is_device)
            elif 'BCL25' in f:
                data = parse_BCL25_json(json_data, i, is_device)
            elif 'ElPtx350' in f:
                data = parse_ElPtx350_json(json_data, i, is_device)
            elif 'BMWix_' in f:
                id1 = f.split('BMWix_IP_')[1].split('_')[0]
                id2 = f.split('ID_')[1].split('_')[0]
                data = parse_BMWix_json(json_data, id1 + id2, i, is_device)
            if 'timestamp' not in data or not data['timestamp']:
                data['timestamp'] = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            if 'category' not in data or not data['category']:
                data['category'] = i
            json_body[i][table_name].append(data)

        # modbus section
        filename, generatrice_modbus_registers = modbus_main(conn=MODBUS_CONN)

        table_name = blockchain_policy(conn=ANYLOG_CONN[i], category=i, filename=filename, is_dummy=args.use_dummy)
        if table_name not in json_body[i]:
            json_body[i][table_name] = []

        if 'category' not in data or not data['category']:
            data['category'] = i
        json_body[i][table_name].append(data)

    for i in json_body:
        anylog_publish_data(conn=ANYLOG_CONN[i], data=json_body[i]  , db_name=args.db_name)




if __name__ == '__main__':
    main()
