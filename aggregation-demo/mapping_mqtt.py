import copy
import os

import support
import json

DATA_DIR = os.path.join(__file__.split("aggregation-demo")[0], "lcdb")
if not os.path.isdir(DATA_DIR):
    raise NotADirectoryError(f"Failed to locate {DATA_DIR}")


MAPPING_INFO = {
    "anotherpeak-tier1": {
        "file": "2024-08-15_Helios_DLB_vessel.json",
        "tables": {
            "battery_telemetry": [
                "batteryStateOfChargePercent",
                "hvBatteryCapacity",
                "hvBatteryType",
                "lvBattery*",
                "currentBatteryPower",
                "maxBatteryPower",
                "timeBattery",
                "timeToFullMinute",
                "starterBatteryVoltage"
                "starterBatteryVoltagePercent"
            ],
            "navigation_telemetry": [
                "currentPositionLatitude",
                "currentPositionLongitude",
                "speedOverGround",
                "speedOverGroundFixed",
                "speedThroughWater",
                "heading*",
                "distance*",
                "trip",
                "sogValid"
            ],
            "charger_telemetry": [
                "acChargerPowerPercent",
                "portAcCharger*",
                "stbdAcCharger*",
                "elPtx*",
                "dcac*",
                "dcdc*",
                "regeneration*"
            ],
            "engine_telemetry": [
            "motor*",
            "rpm*",
            "throttle*",
            "drive*",
            "powerBalance",
            "maxPower",
            "maxSpeed",
            "selectSystemMode",
            "vesselState",
            "systemState"
        ],
        },
    },
    "anotherpeak-tier2": {
        "file": "2024-08-15_Helios_DLB_BCL25_700_8_CH_IP_3_ID_65.json",
        "tables": {
            "ac_power_telemetry": [
                "gActAcCurrent",
                "gActAcVoltage",
                "gActAcFrequency",
                "gCommandAcCurrentLimitPP",
                "gMaxDcPower",
                "gParamMaxAcCurrentPP"
            ],
            "dc_power_telemetry": [
                "gActDcPower",
                "gActDcVoltage",
                "gCommandDcPowerLimit",
                "gCommandMaxDcVoltage"
            ],
            "thermal_telemetry": [
                "gActElectronicTemperature",
                "gCoolingPolicy"
            ],
            "control_state": [
            "gCommand",
            "gState",
            "gWake",
            "gIsSlave",
            "gError",
            "gDisableReason",
            "gSimConnectedPhaseCount"
        ]
        }
    }
}


MAPPING_POLICY = {
    "mapping": {
        "id": "anotherpeak-demo",
        "dbms": "anotherpeak",
        "table": "anotherpeak_generic",
        "readings": "",
        "schema": {
            "timestamp": {
                "bring": "[timestamp]",
                "default": "now",
                "type": "timestamp"
            },
            "vessel": {
                "bring": "[vessel]",
                "default": "UNKNOWN",
                "type": "string"
            }
        }
    }
}

def publish_policy(conn:str, mapping_policy:dict):
    policy_id = mapping_policy.get("mapping").get("id")
    check_policy_headers = {
        "command": f"blockchain get mapping where id={policy_id}",
        "User-Agent": "AnyLog/1.23"
    }
    publish_policy_headers ={
        "command": "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        "User-Agent": "AnyLog/1.23"
    }

    response = support.execute_command(method="GET", conn=conn, headers=check_policy_headers)
    if response.text == "[]":
        new_policy = f"<new_policy={json.dumps(mapping_policy)}>"
        support.execute_command(method="POST", conn=conn, headers=publish_policy_headers, payload=new_policy)

def create_msg_client(conn:str, command:str):
    msg_headers = {
        "command": command,
        "User-Agent": "AnyLog/1.23"
    }

    support.execute_command(method="POST", conn=conn, headers=msg_headers, payload=None)

def check_mqtt_client(conn:str):
    topics = list(MAPPING_INFO.keys())
    status = False


    for topic in topics:
        if not status:
            headers = {
                "command": f"get msg client where topic={topics}",
                "User-Agent": "AnyLog/1.23"
            }

            response = support.execute_command(method="GET", conn=conn, headers=headers)
            if response.text.strip() not in ["No such client subscription", "No message client subscriptions"]:
                status = True

    return status


def mqtt_mapping(conn:str):
    mapping_ids = []

    msg_client = "run msg client where broker=rest and user-agent=anylog and log=false"
    for topic in MAPPING_INFO:
        msg_client += f" and topic=(name={topic}"
        file_path = None
        file_name = MAPPING_INFO[topic].get('file')
        if file_name:
            file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.isfile(file_path) or not file_path:
            raise FileNotFoundError

        index = 0
        content = {}
        while index < 5:
            row, index = support.read_file(file_path, index=index, row_count=5)
            timestamp, line = row.split(": ", 1)
            content[timestamp] = json.loads(line)

        for table in MAPPING_INFO[topic]["tables"]:
            mapping_policy = copy.deepcopy(MAPPING_POLICY)
            mapping_policy["mapping"]["id"] = table.replace("_", "-")
            mapping_policy["mapping"]["table"] = table

            columns_info = support.calculate_data_types(table_columns=MAPPING_INFO[topic]["tables"][table], data=list(content.values()))
            for column in columns_info:
                mapping_policy["mapping"]["schema"][support.camel_to_snake(column)] = {
                    "type": columns_info.get(column),
                    "bring": f"[{column}]",
                    **({"default": "UNKNOWN"} if columns_info.get(column) == "string" else {})
                }


            publish_policy(conn=conn, mapping_policy=mapping_policy)
            msg_client += f" and policy={mapping_policy['mapping']['id']}"
        msg_client += ')'

    if not check_mqtt_client(conn=conn):
        create_msg_client(conn=conn, command=msg_client)

if __name__ == "__main__":
    mqtt_mapping(conn="50.116.20.125:32149")