"""
Methods for parsing data provided from REST service
"""
import datetime
from source.logger_config import logger


def make_it_always_a_float(string):
    float_value = None
    if string:
        try:
            float_value = float(string)
        except ValueError:
            float_value = string
        # logger.error("La valeur fournie n'est pas une chaîne valide: %s", string)
    return float_value


# Function to parse Torqeedo JSON data for vessel page
def parse_vessel_json(input_data, boat_side):
    """
    note: removed boat side from column name(s) in order to allow for query across tables in AnyLog/EdgeLake
    """
    fields_str = {}
    try:
        # Extraire les champs pertinents des données JSON
        fields_str = {
            "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            f"hmiYear": input_data.get("hmiYear", None),
            f"hmiMonth": input_data.get("hmiMonth", None),
            f"hmiDay": input_data.get("hmiDay", None),
            f"hmiHour": input_data.get("hmiHour", None),
            f"hmiMinute": input_data.get("hmiMinute", None),
            f"hmiSecond": input_data.get("hmiSecond", None),
            f"batteryStateOfChargePercent": input_data.get('batteryStateOfChargePercent'),
            f"currentBatteryPower": make_it_always_a_float(input_data.get("currentBatteryPower", None)),
            f"currentPositionLatitude": make_it_always_a_float(input_data.get("currentPositionLatitude", None)),
            f"currentPositionLongitude": make_it_always_a_float(input_data.get("currentPositionLongitude", None)),
            f"distanceDestination": make_it_always_a_float(input_data.get("distanceDestination", None)),
            f"drivePowerConfirmed": input_data.get("drivePowerConfirmed", None),
            f"headingDestination": make_it_always_a_float(input_data.get("headingDestination", None)),
            f"headingHome": make_it_always_a_float(input_data.get("headingHome", None)),
            f"hmiSmuIp": input_data.get("hmiSmuIp", None),
            f"hvBatteryCapacity": make_it_always_a_float(input_data.get("hvBatteryCapacity", None)),
            f"lvBatteryMaxCapacity": input_data.get("lvBatteryMaxCapacity", None),
            f"powerBalance":  make_it_always_a_float(input_data.get("powerBalance", None)),
            f"serverCpuLoad": make_it_always_a_float(input_data.get("serverCpuLoad", None)),  ## always be careful when the field must be a floa>
            f"starterBatteryVoltage": make_it_always_a_float(input_data.get("starterBatteryVoltage", None)),
            f"timeBattery": input_data.get("timeBattery", None)
        }
    except Exception as e:
        # Enregistrer un message d'erreur si l'extraction des données échoue
        logger.error("VESSELLLLLLLLLLLLL error: %s\n%s", e, fields_str)

    return fields_str


# Function to parse Torqeedo JSON data for multi devices
def parse_ACH65_json(input_data, boat_side, is_device:bool=False):
    fields_str = {}
    try:
        if is_device is False:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"ACH65{boat_side}_gMotorVoltage": make_it_always_a_float(input_data.get("gMotorVoltage", None)),
                f"ACH65{boat_side}_ggMotorPower": make_it_always_a_float(input_data.get("gMotorPower", None)),
                f"ACH65{boat_side}_ggMotorTemperature":input_data.get("gMotorTemperature", None),
                f"ACH65{boat_side}_ggElectronicTemperature": input_data.get("gElectronicTemperature", None),
                f"ACH65{boat_side}_ggError": input_data.get("gError", None)
            }
        else:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"ACH65{boat_side}_deviceState": input_data.get("deviceState", None),
                f"ACH65{boat_side}_error": input_data.get("error", None),
                f"ACH65{boat_side}_totalTimeEnabledHours": input_data.get("totalTimeEnabledHours", None)
            }
    except Exception as e:
        logger.error("ACH65 error: %s\n%s", e, fields_str)
    return fields_str

def parse_BCL25_json(input_data, boat_side, is_device:bool=False):
    fields_str = {}
    try:
        if is_device is False:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"BCL25{boat_side}_gState": input_data.get("gState", None),
                f"BCL25{boat_side}_gActAcVoltage": make_it_always_a_float(input_data.get("gActAcVoltage", None)),
                f"BCL25{boat_side}_gActAcCurrent": make_it_always_a_float(input_data.get("gActAcCurrent", None)),
                f"BCL25{boat_side}_gActDcPower": make_it_always_a_float(input_data.get("gActDcPower", None)),
                f"BCL25{boat_side}_gActElectronicTemperature": input_data.get("gActElectronicTemperature", None),
                f"BCL25{boat_side}_gError": input_data.get("gError", None),
                f"BCL25{boat_side}_gWake": input_data.get("gWake", None)
            }
        else:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"BCL25{boat_side}_currentL1": make_it_always_a_float(input_data.get("currentL1", None)),
                f"BCL25{boat_side}_currentL2": make_it_always_a_float(input_data.get("currentL2", None)),
                f"BCL25{boat_side}_currentL3": make_it_always_a_float(input_data.get("currentL3", None)),
                f"BCL25{boat_side}_voltageL1": make_it_always_a_float(input_data.get("voltageL1", None)),
                f"BCL25{boat_side}_voltageL2": make_it_always_a_float(input_data.get("voltageL2", None)),
                f"BCL25{boat_side}_voltageL3": make_it_always_a_float(input_data.get("voltageL3", None)),
                f"BCL25{boat_side}_error": input_data.get("error", None),
                f"BCL25{boat_side}_errorStatus": input_data.get("errorStatus", None)
            }
    except Exception as e:
        logger.error("BCL25 error: %s\n%s", e, fields_str)
    return fields_str

def parse_BMWix_json(input_data, id, boat_side, is_device:bool=False):
    fields_str = {}
    try:
        if is_device is False:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"BMWix{id}{boat_side}_batteryErrorCode": input_data.get("batteryErrorCode", None),
                f"BMWix{id}{boat_side}_gCurrent": make_it_always_a_float(input_data.get("gCurrent", None)),
                f"BMWix{id}{boat_side}_gAverageTemperature": input_data.get("gAverageTemperature", None),
                f"BMWix{id}{boat_side}_gMaxCellTemperature": input_data.get("gMaxCellTemperature", None),
                f"BMWix{id}{boat_side}_gPackVoltage": make_it_always_a_float(input_data.get("gPackVoltage", None)),
                f"BMWix{id}{boat_side}_gStateOfCharge": make_it_always_a_float(input_data.get("gStateOfCharge", None)),
                f"BMWix{id}{boat_side}_gStateOfHealth": make_it_always_a_float(input_data.get("gStateOfHealth", None)),
                f"BMWix{id}{boat_side}_gTimeToFullMinute": input_data.get("gTimeToFullMinute", None)
            }
        else:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"BMWix{id}{boat_side}_actualCurrent": make_it_always_a_float(input_data.get("actualCurrent", None)),
                f"BMWix{id}{boat_side}_actualSoc": make_it_always_a_float(input_data.get("actualSoc", None)),
                f"BMWix{id}{boat_side}_actualTempBattery": input_data.get("actualTempBattery", None),
                f"BMWix{id}{boat_side}_actualTempBatteryMax": input_data.get("actualTempBatteryMax", None),
                f"BMWix{id}{boat_side}_ekmvPresHigh": make_it_always_a_float(input_data.get("ekmvPresHigh", None)),
                f"BMWix{id}{boat_side}_error": input_data.get("error", None)
            }
    except Exception as e:
        logger.error("BMWix_ error: %s\n%s", e, fields_str)
    return fields_str

def parse_ElPtx350_json(input_data, boat_side, is_device:bool=False):
    fields_str = {}
    try:
        if is_device is False:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"ElPtx350{boat_side}_gState": input_data.get("gState", None),
                f"ElPtx350{boat_side}_gPowerRequested": input_data.get("gPowerRequested", None),
                f"ElPtx350{boat_side}_gPowerActual": make_it_always_a_float(input_data.get("gPowerActual", None)),
                f"ElPtx350{boat_side}_gExternalError": input_data.get("gExternalError", None)
            }
        else:
            fields_str = {
                "timestamp": input_data.get("timestamp", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                f"ElPtx350{boat_side}_dcVoltage": make_it_always_a_float(input_data.get("dcVoltage", None)),
                f"ElPtx350{boat_side}_externalError": input_data.get("externalError", None),
                f"ElPtx350{boat_side}_powerActual": make_it_always_a_float(input_data.get("powerActual", None)),
                f"ElPtx350{boat_side}_powerRequest": input_data.get("powerRequest", None)
            }
    except Exception as e:
        logger.info("ElPtx350 error: %s\n%s", e, fields_str)
    return fields_str