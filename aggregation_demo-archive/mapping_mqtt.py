import ast
import copy
import json
import re

from rest_call import execute_command
"""
AnyLog Policy: https://github.com/AnyLog-co/deployment-scripts/blob/os-dev/sample-scripts/edgex.al
"""
TABLES = {
    """
    Data from files is broken down into different tables  based on what they're providing 
    :logic: 
    "group": {
       "file": File,
       
        "table_name": [
            key in file -> column
        ]
    } 
    """        
    "vessel": {
        "file": "2024-08-15_Helios_DLB_vessel.json",
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

    "MOTOR_CONTROLLER": {
        "file": None,
        "motor_performance": [
            "motor_speed",
            "motor_torque",
            "motor_power",
            "motor_voltage",
            "speed_command",
            "torque_command",
            "actual_limit",
            "max_speed"
        ],
        "motor_thermal": [
            "motor_temperature",
            "electronic_temperature",
            "cooling_policy",
            "cooling_temperature"
        ],
        "motor_electrical": [
            "drive_voltage_command",
            "motor_voltage",
            "power_limit_motoring",
            "power_limit_regen",
            "dc_bus_current",
            "dc_bus_filtered_voltage",
            "rms_motor_current"
        ],
        "motor_control": [
            "control_mode",
            "requested_control_mode",
            "pwm_frequency",
            "high_side_switch*",
            "hvil*"
        ],
        "motor_status": [
            "state",
            "command",
            "error",
            "disable_reason"
        ],
        "motor_configuration": [
            "gear_ratio",
            "max_speed",
            "motor_poles",
            "param_max_drive_power",
            "field_weakening*",
            "boost*"
        ],
        "motor_diagnostics": [
            "total_time_enabled_hours",
            "back_emf*",
            "rotor_flux_calc",
            "sw_application_no",
            "sw_major_version",
            "sw_minor_version"
        ],
    },

    "BATTERY_PACK": {
        "file": None,
        "battery_energy": [
            "state_of_charge",
            "state_of_health",
            "energy_remaining",
            "param_max_capacity",
            "time_to_full_minute"
        ],
        "battery_electrical": [
            "bus_voltage",
            "pack_voltage",
            "current",
            "cell_balance",
            "max_cell_voltage",
            "min_cell_voltage"
        ],
        "battery_thermal": [
            "average_temperature",
            "max_cell_temperature",
            "min_cell_temperature",
            "cooling_policy"
        ],
        "battery_health": [
            "state_of_health",
            "power_limit_charge",
            "power_limit_discharge",
            "available_power_charge*",
            "available_power_discharge*"
        ],
        "battery_limits": [
            "param_max_charge_voltage",
            "min_voltage_discharge",
            "max_current_charge",
            "max_current_discharge",
            "min_soc_allowed"
        ],
        "battery_status": [
            "device_state",
            "error",
            "balancing_state",
            "command"
        ],
        "battery_thermal_management": [
            "cooling_type",
            "cooling_requested",
            "cooling_valve*",
            "ekmv*"  # thermal management system
        ],
    },

    # CHARGER_TABLES
"   charger_ac_input": [
        "act_ac_voltage",
        "act_ac_current",
        "act_ac_frequency",
        "command_ac_current_limit_pp",
        "param_max_ac_current_pp",
        "voltage_l*",
        "current_l*"
    ],
    "charger_dc_output": [
        "act_dc_voltage",
        "act_dc_power",
        "command_dc_power_limit",
        "max_dc_power",
        "command_max_dc_voltage",
        "battery_voltage",
        "battery_current"
    ],
    "charger_thermal": [
        "act_electronic_temperature",
        "inv_temp_amb",
        "bb_temp_amb",
        "signal_temp*",
        "cooling_behavior"
    ],
    "charger_control": [
        "cmd_enable",
        "cmd_mode",
        "control_mode",
        "inverter_state",
        "buck_boost_state"
    ],
    "charger_status": [
        "state",
        "command",
        "error",
        "error_status",
        "is_slave"
    ],
    "charger_evse": [
        "evse_type",
        "evse_type_status",
        "evse_status",
        "control_pilot*",
        "proximity_state"
    ],
    "charger_diagnostics": [
        "msg_cntr_hv_values",
        "msg_cntr_signal_status",
        "bbu_c_version",
        "inv_u_c_version",
        "signal_u_c_version",
        "hw_rev"
    ],

    # ISOLATION_MONITOR_TABLES
    "isolation_measurement": [
        "resistance",
        "voltage",
        "error_level",
        "warning_level"
    ],
    "isolation_status": [
        "state",
        "command",
        "error",
        "disable_reason"
    ],

    # HVIL_TABLES
    "hvil_monitoring": [
        "hvil_en",
        "hvil_in",
        "hvil_out",
        "hvil_current",
        "hvil_status"
    ],

    # CONTACTOR_TABLES
    "contactor_status": [
        "state_contactor",
        "request_contactor_close",
        "request_open_contactor*",
        "state_error_contactor"
    ],
    "contactor_diagnostics": [
        "alive_spec_contactor",
        "crc_spec_contactor"
    ],

    # ISOLATION_CONTROL_TABLES
    "isolation_management": [
        "control_iso_measurement",
        "state_error_external_isolation",
        "state_error_internal_isolation",
        "state_warn_isolation"
    ],
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


def _camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()



def get_types_per_key(rows):
    """
    Get data types for each key in the payload
    based on RAW_DATA
    """
    types_per_key = {}

    for row in rows:
        for key, value in row.items():

            # skip null/empty
            if value is None or value == "":
                continue

            # if value is a string, try to convert it
            if isinstance(value, str):
                try:
                    value = ast.literal_eval(value)
                except Exception:
                    pass

            # determine type
            if isinstance(value, bool):
                # ignore booleans or treat them as strings
                value_type = "bool"
            elif isinstance(value, float):
                value_type = "float"
            elif isinstance(value, int):
                value_type = "int"
            else:
                value_type = "string"

            # store in dict
            if key not in types_per_key:
                types_per_key[key] = set()
            types_per_key[key].add(value_type)

    # convert sets to lists
    data_types = {k: list(v) for k, v in types_per_key.items()}
    for key, value in data_types.items():
        # If only one type exists
        if len(value) == 1:
            data_types[key] = value[0]
            continue

        # If string exists with anything else → string
        if "string" in value:
            data_types[key] = "string"
            continue

        # If float exists → float (even if int exists)
        if "float" in value:
            data_types[key] = "float"
            continue

        # If only int exists
        if "int" in value:
            data_types[key] = "int"
            continue

    return data_types


def generate_policy(table:str, data_types:list):
    new_policy_headers = {
        "command": "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        "User-Agent": "AnyLog/1.23"
    }

    check_policy_headers = {
        "command": f"blockchain get * where id = {table.replace('_', '-')}",
        "User-Agent": "AnyLog/1.23"
    }

    response = execute_command(method="GET", conn="50.116.20.125:32149", headers=check_policy_headers)
    if not response.json():
        mapping_policy = copy.deepcopy(MAPPING_POLICY)
        mapping_policy["mapping"]["table"] = table
        mapping_policy["mapping"]["id"] = table.replace('_', '-')
        for column in TABLES[table]:
            if data_types.get(column):
                mapping_policy["mapping"]["schema"][_camel_to_snake(column)] = {
                    "type": data_types.get(column),
                    "bring": f"[{column}]"
                }

            else:
                for data_type in data_types:
                    if data_type.startswith(column.split("*")[0]):
                        mapping_policy["mapping"]["schema"][_camel_to_snake(data_type)] = {
                            "table": table,
                            "type": data_types.get(data_type),
                            "bring": f"[{data_type}]"
                        }
        new_policy = f"<new_policy={json.dumps(mapping_policy)}>"
        response = execute_command(method="POST", conn="50.116.20.125:32149", headers=new_policy_headers, payload=new_policy)
        print(response)


def main():
    data_types = get_types_per_key(RAW_DATA)
    headers = {
        "command": "run msg client where broker=rest and user-agent=anylog and log=false and topic=(name=anotherpeak-demo and ",
        "User-Agent": "AnyLog/1.23"
    }
    for table in TABLES:
        print(table)
        generate_policy(table, data_types)
        headers["command"] += f" policy={table.replace('_', '-')} and "

    headers["command"] = headers["command"].rsplit(" and ", 1)[0] + ")"
    response = execute_command(method="POST", conn="50.116.20.125:32159", headers=headers, payload=None)
    print(response)


if __name__ == "__main__":
    main()

