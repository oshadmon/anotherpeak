"""
Major Changes:
1. when executing a GET REST request, there's no need to convert from dict (request.json()) to serialized JSON and back to dict
2. the if /else for device is inside the parse processes
3. Instead of writing to list and then to file, we're writing directly into AnyLog -- if you want we can thread / parallelize the code for efficency
"""
import argparse
import datetime
import socket

from source.logger_config import logger, setup_logger
from source.data_parse import parse_vessel_json,parse_ACH65_json,parse_BCL25_json,parse_BMWix_json,parse_ElPtx350_json
from source.rest_api import fetch_raw_json
from source.modbus import modbus_main
from source.params import Helios_default,Helios_DL_devices,Helios_DL_IP
from source.anylog_api import blockchain_policy, anylog_publish_data

ANYLOG_CONN = {"T": '178.79.168.109:32149', "B": '178.79.168.113:32149'}
MODBUS_CONN = '127.0.0.1:502'


def check_ping(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=5):
            pass
    except (socket.timeout, socket.error):
        logger.error(f"Connection failed to {ip} on port {port}")
        exit(1)


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('db_name', type=str, default='another_peak', help='logical database to store data in')
    parse.add_argument('--use-dummy', type=bool, const=True,  default=False, nargs='?',  help='Use dummy servers / files rather than production device')
    args = parse.parse_args()

    current_time = datetime.datetime.now()
    json_body = {}
    for i in ["B", "T"]:  # On parcourt Babord et Tribord et comme les componnents  ont le même nom, on rajoute "B" ou "T" pour les différencier
        for f in Helios_default:
            if f != "vessel":
                break
            url = f"http://127.0.0.1:8481/{f}" if args.use_dummy is True else f"http://{Helios_DL_IP[i]}/{f}"

            # On sauvegarde la donnée brute dans un fichier, un fichier par composant par jour
            filename = f"{current_time.strftime('%Y-%m-%d')}_Helios_DL_{i}_{f}.json"

            table_name = blockchain_policy(conn=ANYLOG_CONN[i], category=i, filename=filename, is_dummy=args.use_dummy)
            if table_name not in json_body:
                json_body[table_name] = []
            json_data = fetch_raw_json(url)
            if json_data and f == "vessel":
                data = parse_vessel_json(json_data, i)
            else:
                logger.error("%s Failed to fetch data from %s", f, url)
            if 'timestamp' not in data or not data['timestamp']:
                data['timestamp'] = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            if 'category' not in data or not data['category']:
                data['category'] = i
            json_body[table_name].append(data)
        # on parcourt ici les composants hardware: batteries, chargeurs, convertisseurs, moteurs
        for f in Helios_DL_devices[i]:
            url = f"http://127.0.0.1:8481/{i}/{f}" if args.use_dummy is True else f"http://{Helios_DL_IP[i]}/device/{f}"
            filename = f"{current_time.strftime('%Y-%m-%d')}_Helios_DL_{i}_{f}.json"

            table_name = blockchain_policy(conn=ANYLOG_CONN[i], category=i, filename=filename, is_dummy=args.use_dummy)
            if table_name not in json_body:
                json_body[table_name] = []

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
            json_body[table_name].append(data)

        # modbus section
        filename, generatrice_modbus_registers = modbus_main(conn=MODBUS_CONN)

        table_name = blockchain_policy(conn=ANYLOG_CONN[i], category=i, filename=filename, is_dummy=args.use_dummy)
        if table_name not in json_body:
            json_body[table_name] = []

        if 'category' not in data or not data['category']:
            data['category'] = i
        json_body[table_name].append(data)

    anylog_publish_data(conn=ANYLOG_CONN[i], data=json_body, db_name=args.db_name)


if __name__ == '__main__':
    setup_logger()
    check_ping('127.0.0.1', 8481)
    main()
