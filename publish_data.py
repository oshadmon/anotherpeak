import datetime 
import json
import os
import random
import requests 

DATA_DIR = os.path.expanduser(os.path.expandvars('$HOME/lcdb'))
CONN = ["178.79.168.109:32149", "178.79.168.113:32149"]
MASTER = "178.79.168.108"

HELIOS_DEFAULT = ["vessel", "errors", "info", "devices"]
# Helios Information
HELIOS_DL_DEVICES = {
    'B': [
         "ACH65_IP_3_ID_66",
         "ACH65_IP_3_ID_66_DEVICE",
         "BCL25_700_8_CH_IP_3_ID_65",
         "BCL25_700_8_CH_IP_3_ID_65_DEVICE",
         "BCL25_700_8_CH_IP_4_ID_65",
         "BCL25_700_8_CH_IP_4_ID_65_DEVICE",
         "BMWixIsoMon_IP_4_ID_50",
         "BMWixIsoMon_IP_4_ID_50_DEVICE",
         "BMWixIsoMon_IP_3_ID_50",
         "BMWixIsoMon_IP_3_ID_50_DEVICE",
         "BMWix_IP_3_ID_33",
         "BMWix_IP_3_ID_33_DEVICE",
         "BMWix_IP_3_ID_49",
         "BMWix_IP_3_ID_49_DEVICE",
         "BMWix_IP_3_ID_81",
         "BMWix_IP_3_ID_81_DEVICE",
         "BMWix_IP_4_ID_49",
         "BMWix_IP_4_ID_49_DEVICE",
         "BMWixIsoMon_IP_3_ID_82",
         "BMWixIsoMon_IP_3_ID_82_DEVICE",
         "BMWixIsoMon_IP_3_ID_34",
         "BMWixIsoMon_IP_3_ID_34_DEVICE",
         "ElPtx350_IP_4_ID_81",
         "ElPtx350_IP_4_ID_81_DEVICE"
    ],
    'T': [
         "ACH65_IP_3_ID_66",
         "ACH65_IP_3_ID_66_DEVICE",
         "BCL25_700_8_CH_IP_3_ID_65",
         "BCL25_700_8_CH_IP_3_ID_65_DEVICE",
         "BMWix_IP_3_ID_33",
         "BMWix_IP_3_ID_33_DEVICE",
         "BMWix_IP_3_ID_49",
         "BMWix_IP_3_ID_49_DEVICE",
         "BMWix_IP_3_ID_81",
         "BMWix_IP_3_ID_81_DEVICE",
         "BMWix_IP_4_ID_49",
         "BMWix_IP_4_ID_49_DEVICE",
         "BMWixIsoMon_IP_4_ID_50",
         "BMWixIsoMon_IP_4_ID_50_DEVICE",
         "BMWixIsoMon_IP_3_ID_50",
         "BMWixIsoMon_IP_3_ID_50_DEVICE",
         "BMWixIsoMon_IP_3_ID_82",
         "BMWixIsoMon_IP_3_ID_82_DEVICE",
         "BMWixIsoMon_IP_3_ID_34",
         "BMWixIsoMon_IP_3_ID_34_DEVICE"
    ]
}


def blockchain_policy(category, table_name): 
    new_policy = {
        "boat": {
            "name": table_name, 
            "category": category,
            "boat_id": int(table_name.split("_ID_")[-1]),
            "component": table_name.split("_IP")[0],
            "ip": int(table_name.split("_IP_")[-1].split("_")[0])
        }
    }

    raw_policy = f"<new_policy={json.dumps(new_policy)}>"
    try: 
        r = requests.post(url='http://178.79.168.108:32049', 
                          headers={'command': 'blockchain push !new_policy',
                                   'User-Agent': 'AnyLog/1.23', 
                                   'destination': '178.79.168.108:32048'},
                          data=raw_policy)
    except Exception as e: 
        raise Exception('Failed to POST policy against 178.79.168.108 (Error; %s)' % e)
    else: 
        if int(r.status_code) != 200: 
            raise Exception('Failed to POST policy against 178.79.168.108 (Network Error: %s)' % r.status_code)


def publish_data(table, data): 
    conn = random.choice(CONN) 
    headers = {
        "command": 'data', 
        'dbms': 'another_peak', 
        'table': table, 
        'mode': 'streaming',
        'Content-Type': 'text/plain',
        'User-Agent': 'AnyLog/1.23', 
    }

    try: 
        r = requests.put(url=f'http://{conn}', headers=headers, data=json.dumps(data))
    except Exception as e:    
        raise Exception('Failed to PUT policy against %s (Error; %s)' % (conn, e))
    else: 
        if int(r.status_code) != 200:
            raise Exception('Failed to PUT policy against %s (Network Error: %s)' % (conn, r.status_code))


def parse_hybrid_log_format(hybrid_log):
    """
    Parses Hybrid Log Format (HLF) data into a structure suitable for InfluxDB.
    """
    parsed_data = []
    for line in hybrid_log:
        if not line.strip():
            continue  # Skip empty line
        try:
            timestamp_str, json_part = line.split(": ", 1)
            data = json.loads(json_part)
            data['timestamp'] = timestamp_str
            if not parsed_data:
                parsed_data.append(data)
            else: 
                status = False
                for i in range(len(parsed_data)): 
                    if data['timestamp'] == parsed_data[i]['timestamp']: 
                        parsed_data[i] = {**parsed_data[i], **data}
                        status = True
                if status is False:
                    parsed_data.append(data)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing line: {line}\n{e}")
    return parsed_data

def main():
    for category in HELIOS_DL_DEVICES: 
        for boat in HELIOS_DL_DEVICES[category]: 
            hybrid_log = []
            if 'DEVICE' in boat: 
                continue
            blockchain_policy(category, table_name=boat)
            for fn in os.listdir(DATA_DIR) : 
                if boat in fn: 
                    print(category, boat, fn) 
                    full_path = os.path.join(DATA_DIR, fn)
                    with open(full_path, 'r') as f: 
                        hybrid_log += f.read().split('\n')[:-1]
            parsed_data=parse_hybrid_log_format(hybrid_log)
            publish_data(table=boat,  data=parsed_data)

        
if __name__ == '__main__': 
    main()
