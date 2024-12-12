import logging, requests, json, time, socket
from datetime import datetime
from influxdb import InfluxDBClient
from itertools import chain
from pyModbusTCP.client import ModbusClient
from logging.handlers import RotatingFileHandler

# InfluxDB connection details
host = 'localhost'  # or your InfluxDB host
port = 8086  # or your InfluxDB port
database = 'electrificationBateaux'  # your InfluxDB database name
measurement = 'Helios'  # Measurement name for battery state of charge percent

# Gestion des logs
# Configurer la journalisation pour enregistrer et afficher les messages d'erreur et d'information
logger = logging.getLogger("main_logger")
logger.setLevel(logging.DEBUG)  # Set the logger to the lowest level you want to capture (DEBUG > INFO > WARNING > ERROR > CRITICAL)

# Create a rotating file handler for INFO and above
file_handler = RotatingFileHandler("torqeedo_modbus_datalogger_v1.log", maxBytes=5000000, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Create a stream handler for ERROR and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Liste des objets du bateau Helios
# Obtenu en faisant un https://[IP_datalogger]:8481/devices
# Sur tous les dataloggers installes
Helios_DL_IP = {'B': "10.85.9.111:8481", 'T': "10.85.9.110:8481"}  # 2x dataloggers, babord / tribord respectivement
Helios_default = ["vessel", "errors", "info", "devices"]
Helios_DL_devices = {
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

# Modbus client (la generatrice)
modbus_timeout = 5  # maximum time in second to wait for an answer from modbus device - it's not a ping, modbbus device is accessible but the device behind it may not, ie generatrice is switched off
max_modbus_retries = 3  # /!\ every retry will delay the writing into influxDB by the number of retries multiplied by modbus timeout
c = ModbusClient(host='10.85.9.120', port=502, auto_open=True, debug=False, timeout=modbus_timeout)

# Define the Modbus client start address and the number of registers to read
base_address = 40001
address_ranges = [(base_address, 40801), (43000, 43477)]
#address_ranges = [(base_address, 40201)]
num_registers = 10  # max 125 registers per poll for modbus

# Define Modbusregister addresses, names, units, lengths and decimals based on the reference document
# Note that all the following registers are saved in influxDB. If not necessary, simply comment the line
registers_info = [
    (40011, "GD_BatteryVolt", "V", "Binary", 2, 1),
    (40012, "GD_CPUTemp", "°C", "Binary", 2, 1),
#    (40013, "GD_Seawater", "Bar", "Integer", 2, 2),
    (40017, "GD_ExhaustTemp", "°C", "Integer", 2, None),
    (40053, "GD_EngineSpeed", "rpm", "Integer", 2, None),
    (40054, "GD_FuelRate", "L/h", "Integer", 2, 1),
    (40055, "GD_T-Coolant", "°C", "Integer", 2, None),
    (40056, "GD_T-IntManifold", "°C", "Integer", 2, None),
    (40057, "GD_P-Oil", "bar", "Integer", 2, 2),
    (40059, "GD_Load", "%", "Integer", 2, None),
    (40073, "GD_EngineRunHours", "h", "Integer", 4, None),
    (40075, "GD_TotalFuelUsed", "L", "Integer", 4, 1),
#    (40118, "GD_SwBranch", None, "List", 2, None),
#    (40119, "GD_PasswordDecode", None, "Unsigned", 4, None),
    (40121, "GD_EngineState", None, "List", 2, None),
#    (40127, "GD_PLC-BOUT1", None, "Binary", 1, None),
#    (40155, "GD_Application", None, "List", 1, None),
#    (40156, "GD_TimerText", None, "List", 1, None),
#    (40157, "GD_TimerVal", "s", "Unsigned", 2, None),
    (40158, "GD_SpeedRequest", "%", "Integer", 2, 1),
    (40166, "GD_EngineRPM", "RPM", "Integer", 2, None),
    (40167, "GD_TCylAver", "°C", "Integer", 2, None),
    (40168, "GD_TCylMax", "°C", "Integer", 2, None),
    (40169, "GD_TCylMin", "°C", "Integer", 2, None),
#    (40171, "GD_ECU_FC", None, "Unsigned", 4, None),
#    (40173, "GD_ECU_FMI", None, "Unsigned", 1, None),
#    (40174, "GD_ECU_OC", None, "Unsigned", 1, None),
    (40179, "GD_OilPress", "bar", "Integer", 2, 2),
    (40180, "GD_CoolTemp", "°C", "Integer", 2, None),
    (40213, "GD_RemoteControl", None, "Binary", 2, None),
#    (40214, "GD_DiagCode", None, "List", 1, None),
#    (40215, "GD_MID", None, "Unsigned", 1, None),
#    (40216, "GD_PMStatus", None, "Binary", 1, None),
    (40217, "GD_MomAvgFlCon", "L /nm", "Integer", 2, 1),
    (40218, "GD_PriBattery", "V", "Unsigned", 2, 2),
    (40219, "GD_SecBattery", "V", "Unsigned", 2, 2),
    (40220, "GD_EngRPMfiltered", "RPM", "Unsigned", 2, None),
    (40221, "GD_GPSSpeed", "kts", "Integer", 2, 1),
    (40222, "GD_Latitude", None, "String", 16, None),
    (40230, "GD_Longitude", None, "String", 16, None),
    (40238, "GD_ST", None, "Binary", 4, None),
#    (40240, "GD_LogBout5", None, "Binary", 2, None),
    (40281, "GD_OilPress", "bar", "Integer", 2, 2),
    (40282, "GD_CoolTemp", "°C", "Integer", 2, None),
#    (40383, "GD_AFTregistr", None, "Binary", 4, None),
#    (40385, "GD_LogBout6", None, "Binary", 2, None),
#    (40387, "GD_DEF_Level", "%", "Integer", 2, None),
#    (40449, "GD_DPF_SootLoad", "%", "Integer", 2, None),
#    (40472, "GD_LogBout7", None, "Binary", 2, None),
    (40498, "GD_D+", "V", "Integer", 2, 1),
    (40553, "GD_Seconds", "s", "Unsigned", 1, None),
    (40554, "GD_Minutes", "m", "Unsigned", 1, None),
    (40555, "GD_Hours", "h", "Unsigned", 1, None),
    (40556, "GD_Month", None, "Unsigned", 1, None),
    (40557, "GD_Day", None, "Unsigned", 1, None),
    (40558, "GD_YearsSince1985", None, "Unsigned", 1, None),
    (40559, "GD_SpeedReqRPM", "RPM", "Unsigned", 2, None),
#    (40576, "GD_ModuleName", None, "List", 1, None),
#    (40577, "GD_ModuleIndex", None, "Unsigned", 1, None),
#    (40786, "GD_DPF_AshLoad", "%", "Unsigned", 2, None),
#    (40787, "GD_LogBout8", None, "Binary", 2, None),
#    (40788, "GD_ECU_State", None, "Binary", 1, None),
    (40789, "GD_FuelUsed", "L", "Integer", 4, None),
    (40791, "GD_OilTemp", "°C", "Integer", 2, None),
    (40792, "GD_FuelLevel", "%", "Integer", 2, None),
    (43034, "GD_RunHours", "h", "Integer", 4, None),
    (43036, "GD_NumSuccStarts", None, "Unsigned", 2, None),
    (43037, "GD_NumUnscStarts", None, "Unsigned", 2, None),
    (43038, "GD_ServiceTime", "h", "Unsigned", 2, None),
    (43043, "GD_EngineName", None, "String", 16, None),
    (43059, "GD_ModeID", None, "List", 1, None),
    (43060, "GD_ModeLoc", None, "List", 1, None),
    (43061, "GD_GearTeeth", None, "Unsigned", 2, None),
#    (43063, "GD_ECU_Diag", None, "List", 1, None),
    (43115, "GD_WarningCall", None, "List", 1, None),
    (43116, "GD_ShutDownCall", None, "List", 1, None),
    (43117, "GD_CoolDownCall", None, "List", 1, None),
    (43118, "GD_LightTimeOff", "min", "Unsigned", 1, None),
    (43119, "GD_HornTimeout", "s", "Unsigned", 2, None),
    (43132, "GD_HornOnBinIn.", None, "List", 1, None),
    (43133, "GD_StartSignal", None, "Binary", 2, None),
    (43134, "GD_EndSignal", None, "Binary", 2, None),
    (43135, "GD_SyncSignal", None, "Binary", 2, None),
    (43143, "GD_StartCurrentSens", None, "List", 1, None),
    (43144, "GD_StopCurrentSens", None, "List", 1, None),
    (43148, "GD_EndCurrentSens", None, "List", 1, None),
    (43149, "GD_WarningCurrentSens", None, "List", 1, None),
    (43150, "GD_ShutDownCurrentSens", None, "List", 1, None),
    (43151, "GD_CoolDownCurrentSens", None, "List", 1, None),
    (43156, "GD_TripCurrent", None, "List", 1, None)
]

# Connect to InfluxDB
influxDBclient = InfluxDBClient(host=host, port=port, database=database)

# Function to create database if it doesn't exist
def create_database(database_name):
    influxDBclient.create_database(database_name)

def make_it_always_a_float(string):
    try:
        float_value = float(string)
        return float_value
    except ValueError:
        logger.error("La valeur fournie n'est pas une chaîne valide: %s", string)

# Function to parse Torqeedo JSON data for vessel page
def parse_vessel_json(input_data, boat_side):
    try:
        # Tenter de décoder les données JSON fournies en entrée
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        # Enregistrer un message d'erreur si le décodage JSON échoue
        logger.error("vessel Failed to decode JSON: %s", e)
        return {}

    fields_str = {}
    try:
        # Extraire les champs pertinents des données JSON
        fields_str = {
            f"hmiYear{boat_side}": json_data.get("hmiYear", None),
            f"hmiMonth{boat_side}": json_data.get("hmiMonth", None),
            f"hmiDay{boat_side}": json_data.get("hmiDay", None),
            f"hmiHour{boat_side}": json_data.get("hmiHour", None),
            f"hmiMinute{boat_side}": json_data.get("hmiMinute", None),
            f"hmiSecond{boat_side}": json_data.get("hmiSecond", None),
            f"batteryStateOfChargePercent{boat_side}": json_data.get('batteryStateOfChargePercent'),
            f"currentBatteryPower{boat_side}": make_it_always_a_float(json_data.get("currentBatteryPower", None)),
            f"currentPositionLatitude{boat_side}": make_it_always_a_float(json_data.get("currentPositionLatitude", None)),
            f"currentPositionLongitude{boat_side}": make_it_always_a_float(json_data.get("currentPositionLongitude", None)),
            f"distanceDestination{boat_side}": make_it_always_a_float(json_data.get("distanceDestination", None)),
            f"drivePowerConfirmed{boat_side}": json_data.get("drivePowerConfirmed", None),
            f"headingDestination{boat_side}": make_it_always_a_float(json_data.get("headingDestination", None)),
            f"headingHome{boat_side}": make_it_always_a_float(json_data.get("headingHome", None)),
            f"hmiSmuIp{boat_side}": json_data.get("hmiSmuIp", None),
            f"hvBatteryCapacity{boat_side}": make_it_always_a_float(json_data.get("hvBatteryCapacity", None)),
            f"lvBatteryMaxCapacity{boat_side}": json_data.get("lvBatteryMaxCapacity", None),
            f"powerBalance{boat_side}":  make_it_always_a_float(json_data.get("powerBalance", None)),
            f"serverCpuLoad{boat_side}": make_it_always_a_float(json_data.get("serverCpuLoad", None)),  ## always be careful when the field must be a floa>
            f"starterBatteryVoltage{boat_side}": make_it_always_a_float(json_data.get("starterBatteryVoltage", None)),
            f"timeBattery{boat_side}": json_data.get("timeBattery", None)
        }
    except Exception as e:
        # Enregistrer un message d'erreur si l'extraction des données échoue
        logger.error("VESSELLLLLLLLLLLLL error: %s\n%s", e, fields_str)
    return fields_str

# Function to parse Torqeedo JSON data for multi devices
def parse_ACH65_json(input_data, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("ACH65 Failed to decode JSON: %s", e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"ACH65{boat_side}_gMotorVoltage": make_it_always_a_float(json_data.get("gMotorVoltage", None)),
            f"ACH65{boat_side}_ggMotorPower": make_it_always_a_float(json_data.get("gMotorPower", None)),
            f"ACH65{boat_side}_ggMotorTemperature":json_data.get("gMotorTemperature", None),
            f"ACH65{boat_side}_ggElectronicTemperature": json_data.get("gElectronicTemperature", None),
            f"ACH65{boat_side}_ggError": json_data.get("gError", None)
        }
    except Exception as e:
        logger.error("ACH65 error: %s\n%s", e, fields_str)
    return fields_str

def parse_ACH65_DEVICE_json(input_data, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("ACH_DEVICE Failed to decode JSON: %s", e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"ACH65{boat_side}_deviceState": json_data.get("deviceState", None),
            f"ACH65{boat_side}_error": json_data.get("error", None),
            f"ACH65{boat_side}_totalTimeEnabledHours": json_data.get("totalTimeEnabledHours", None)
        }
    except Exception as e:
        logger.error("ACH65_DEVICE error: %s\n%s", e, fields_str)
    return fields_str

def parse_BCL25_json(input_data, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("BCL25 Failed to decode JSON: %s", e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"BCL25{boat_side}_gState": json_data.get("gState", None),
            f"BCL25{boat_side}_gActAcVoltage": make_it_always_a_float(json_data.get("gActAcVoltage", None)),
            f"BCL25{boat_side}_gActAcCurrent": make_it_always_a_float(json_data.get("gActAcCurrent", None)),
            f"BCL25{boat_side}_gActDcPower": make_it_always_a_float(json_data.get("gActDcPower", None)),
            f"BCL25{boat_side}_gActElectronicTemperature": json_data.get("gActElectronicTemperature", None),
            f"BCL25{boat_side}_gError": json_data.get("gError", None),
            f"BCL25{boat_side}_gWake": json_data.get("gWake", None)
        }
    except Exception as e:
        logger.error("BCL25 error: %s\n%s", e, fields_str)
    return fields_str

def parse_BCL25_DEVICE_json(input_data, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("BCL25_DEVICE Failed to decode JSON: %s", e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"BCL25{boat_side}_currentL1": make_it_always_a_float(json_data.get("currentL1", None)),
            f"BCL25{boat_side}_currentL2": make_it_always_a_float(json_data.get("currentL2", None)),
            f"BCL25{boat_side}_currentL3": make_it_always_a_float(json_data.get("currentL3", None)),
            f"BCL25{boat_side}_voltageL1": make_it_always_a_float(json_data.get("voltageL1", None)),
            f"BCL25{boat_side}_voltageL2": make_it_always_a_float(json_data.get("voltageL2", None)),
            f"BCL25{boat_side}_voltageL3": make_it_always_a_float(json_data.get("voltageL3", None)),
            f"BCL25{boat_side}_error": json_data.get("error", None),
            f"BCL25{boat_side}_errorStatus": json_data.get("errorStatus", None)
        }
    except Exception as e:
        logger.error("BCL25_DEVICE error: %s\n%s", e, fields_str)
    return fields_str

def parse_BMWix_json(input_data, id, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("BMWix%s Failed to decode JSON: %s", id, e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"BMWix{id}{boat_side}_batteryErrorCode": json_data.get("batteryErrorCode", None),
            f"BMWix{id}{boat_side}_gCurrent": make_it_always_a_float(json_data.get("gCurrent", None)),
            f"BMWix{id}{boat_side}_gAverageTemperature": json_data.get("gAverageTemperature", None),
            f"BMWix{id}{boat_side}_gMaxCellTemperature": json_data.get("gMaxCellTemperature", None),
            f"BMWix{id}{boat_side}_gPackVoltage": make_it_always_a_float(json_data.get("gPackVoltage", None)),
            f"BMWix{id}{boat_side}_gStateOfCharge": make_it_always_a_float(json_data.get("gStateOfCharge", None)),
            f"BMWix{id}{boat_side}_gStateOfHealth": make_it_always_a_float(json_data.get("gStateOfHealth", None)),
            f"BMWix{id}{boat_side}_gTimeToFullMinute": json_data.get("gTimeToFullMinute", None)
        }
    except Exception as e:
        logger.error("BMWix_ error: %s\n%s", e, fields_str)
    return fields_str

def parse_BMWix_DEVICE_json(input_data, id, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("BMWix%s_DEVICE Failed to decode JSON: %s", id, e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"BMWix{id}{boat_side}_actualCurrent": make_it_always_a_float(json_data.get("actualCurrent", None)),
            f"BMWix{id}{boat_side}_actualSoc": make_it_always_a_float(json_data.get("actualSoc", None)),
            f"BMWix{id}{boat_side}_actualTempBattery": json_data.get("actualTempBattery", None),
            f"BMWix{id}{boat_side}_actualTempBatteryMax": json_data.get("actualTempBatteryMax", None),
            f"BMWix{id}{boat_side}_ekmvPresHigh": make_it_always_a_float(json_data.get("ekmvPresHigh", None)),
            f"BMWix{id}{boat_side}_error": json_data.get("error", None)
        }
    except Exception as e:
        logger.error("BMWix_DEVICE error: %s\n%s", e, fields_str)
    return fields_str

def parse_ElPtx350_json(input_data, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("ElPtx350 Failed to decode JSON: %s", id, e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"ElPtx350{boat_side}_gState": json_data.get("gState", None),
            f"ElPtx350{boat_side}_gPowerRequested": json_data.get("gPowerRequested", None),
            f"ElPtx350{boat_side}_gPowerActual": make_it_always_a_float(json_data.get("gPowerActual", None)),
            f"ElPtx350{boat_side}_gExternalError": json_data.get("gExternalError", None)
        }
    except Exception as e:
        logger.info("ElPtx350 error: %s\n%s", e, fields_str)
    return fields_str

def parse_ElPtx350_DEVICE_json(input_data, boat_side):
    try:
        json_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        logger.error("ElPtx350_DEVICE Failed to decode JSON: %s", e)
        return {}

    fields_str = {}
    try:
        fields_str = {
            f"ElPtx350{boat_side}_dcVoltage": make_it_always_a_float(json_data.get("dcVoltage", None)),
            f"ElPtx350{boat_side}_externalError": json_data.get("externalError", None),
            f"ElPtx350{boat_side}_powerActual": make_it_always_a_float(json_data.get("powerActual", None)),
            f"ElPtx350{boat_side}_powerRequest": json_data.get("powerRequest", None)
        }
    except Exception as e:
        logger.error("ElPtx350_DEVICE error: %s\n%s", e, fields_str)
    return fields_str

# Write data to InfluxDB
def insert_json_influxdb(measurement_name, input_data):
    result = {}
    for item in input_data:  # on doit normaliser le contenu JSON qui est un assemblage de plusieurs objets afin de les inserer en une entrée dans influxdb
        for key, value in item.items():
            result[key] = value

    json_body = [{
        "measurement": measurement_name,
        "fields": result
    }]

    logger.info("INSERT POINTTTTTTTTTTT\n%s", json_body)

#    json_body.append(point)

    try:
        influxDBclient.write_points(json_body)
    except Exception as e:
        logger.critical("Error writing JSON in influxDB: %s", e)

def fetch_and_save_raw_json(url, filename):
    try:
        response = requests.get(url)
        #logger.info("HTTP response for %s is %s", url, response.status_code)
        if response.status_code == 200:  # HTTP response code is 200 as expected
            data = response.json()
            try:
                with open(filename, 'a') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f'{timestamp}: {json.dumps(data)}\n')
                return data
            except IOError as e:
                logger.critical("fetch_and_save_raw_json - Error writing to file %s: %s", filename, e)
                return None
        else:
            logger.error("fetch_and_save_raw_json - HTTP response for %s is not 200, code: %s", url, response)
            return None
    except requests.ConnectionError as e:
        logger.error("fetch_and_save_raw_json - Erreur de connexion pour %s : %s", url, e)
        return None
    except requests.Timeout as e:
        logger.error("fetch_and_save_raw_json - La requête a expiré pour %s : %s", url, e)
        return None
    except requests.RequestException as e:
        logger.error("fetch_and_save_raw_json - Erreur lors de la requête pour %s : %s", url, e)
        return None
    except Exception as e:
        logger.error("fetch_and_save_raw_json - Error fetching JSON: %s", e)
        return None

# Fonction pour lire et sauvegarder tous les registres Modbus dans un fichier
def read_modbus_memory_block(client, start_address, num_registers):
    # Read a block of memory and return the raw register values.
    #logger.info(f"{client} ||| {start_address} ||| {num_registers}")
    try:
        start_time = time.time()
        regs_l = client.read_holding_registers(start_address - base_address, num_registers)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > modbus_timeout:
            logger.error(f"{client} ||| {start_address} ||| {num_registers} read_timeout: {elapsed_time}")
            return ('read_timeout', None)
        elif regs_l:
            return ('success', regs_l)
        else:
            return ('no_read', None)
    except socket.timeout:
        logger.error(f"Timeout occurred while reading Modbus memory block starting at address {start_address}")
        return ('socket_timeout', None)
    except Exception as e:
        logger.error(f"Failed to read memory block starting at address {start_address}: {e}")
        return ('exception_error', None)

def read_and_save_all_modbus_registers(connection, base_address, block_size, filename):
    register_table = {}
    retries = 0
    for start_address, end_address in address_ranges:
        total_registers = end_address - start_address + 1
        # Calculate the number of blocks to read
        num_blocks = (total_registers + block_size - 1) // block_size
        logger.info("total_registers: %s // block_size: %s // num_blocks: %s", total_registers, block_size, num_blocks)

        for i in range(num_blocks):
            current_address = start_address + i * block_size
            count = min(block_size, total_registers - i * block_size)

            try:
                status, raw_data = read_modbus_memory_block(connection, current_address, count)
                if status == 'success':
                    try:
                        # save all registers in a raw format
                        with open(filename, 'a') as f:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            f.write(f'{timestamp}: register {current_address} raw_data: {raw_data}\n')
                    except IOError as e:
                        logger.critical("fetch_and_save_raw_json - Error writing to file %s: %s", filename, e)
                        return None
                    #logger.info("register %s raw_data: %s", current_address, raw_data)
                    for j, value in enumerate(raw_data):
                        register_id = current_address + j
                        register_table[register_id] = value
                elif status == 'read_timeout' or status == 'socket_timeout':
                    retries+=1
                    logger.error("Error %s Modbus ||  number of retries left: %s", status, max_modbus_retries - retries)
                    if retries >= max_modbus_retries:
                        break
                else:
                    logger.error("No data returned for address range %s to %s: %s", current_address, current_address + count - 1, status)
            except ValueError as e:
                logger.error(f"Error reading data at address %s: %s", current_address, e)
                break
        if retries >= max_modbus_retries:
            logger.error("%s Modbus max retries reached: %s", status, retries)
            break

    return register_table

def combine_modbus_registers(register_table, register_id, length):
    value = 0
    for offset in range(length):
        addr = register_id + offset
        if addr in register_table:
            value = (value << 16) | register_table[addr]
        else:
            return None
    return value

# Fonction pour imprimer le tableau des registres Modbus
def print_modbus_register_table(register_table, registers_info):
    # prints and creates a list of all registers described in registers_info list
    gen_body = {}
    for info in registers_info:
        register_id, name, unit, type, length, decimals = info

        if length == 4:
            value = combine_modbus_registers(register_table, register_id, 2)
        elif length == 3:
            value = combine_modbus_registers(register_table, register_id, 2)
        elif length == 16:
            value = combine_modbus_registers(register_table, register_id, 4)
        elif length == 32:
            value = combine_modbus_registers(register_table, register_id, 8)
        else:
            value = register_table.get(register_id)

        if value is not None:
            if decimals is not None and unit is not None:
                formatted_value = value / (10 ** decimals)
                gen_body[name] = formatted_value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {formatted_value} {unit}")
            elif decimals is not None:
                formatted_value = value / (10 ** decimals)
                gen_body[name] = formatted_value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {formatted_value}")
            elif unit is not None:
                gen_body[name] = value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {value} {unit}")
            else:
                gen_body[name] = value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {value}")
        else:
            logger.info(f"Register {register_id} [{length}]: No data || {name}")

    return gen_body

# Main read loop
if __name__ == "__main__":
    while True:
        start_time = time.time()  # Enregistrer le temps de début d'exécution
        current_time = datetime.now()
        # Torqeedo datalogger section
        json_body = []
        for i in ["B", "T"]:   # On parcourt Babord et Tribord et comme les composants ont le même nom, on rajoute "B" ou "T" pour les différencier
            for f in Helios_default:
                url = "http://" + Helios_DL_IP[i] + "/" + f    # On fabrique toutes les URLs de récupération des datas
                filename = current_time.strftime("%Y-%m-%d") + "_Helios_DL" + i + "_" + f + ".json"   # On sauvegarde la donnée brute dans un fichier, un fichier par composant par jour
                jason = fetch_and_save_raw_json(url, filename)
                if jason is not None:
                    try:
                        if 'vessel' in f:
                            json_body.append(parse_vessel_json(json.dumps(jason),i))
                    except Exception as e:
                        logger.error("Error in saving the value to Influxdb %s", e)
                else:
                    logger.error("%s Failed to fetch data from %s", f, url)

            for f in Helios_DL_devices[i]:   # on parcourt ici les composants hardware: batteries, chargeurs, convertisseurs, moteurs
                url = "http://" + Helios_DL_IP[i] + "/device/" + f
                filename = current_time.strftime("%Y-%m-%d") + "_Helios_DL" + i + "_" + f + ".json"
                jason = fetch_and_save_raw_json(url, filename)
                if jason is not None:
                    try:
                        if 'ACH65' in f:
                            if 'DEVICE' in f:
                                json_body.append(parse_ACH65_DEVICE_json(json.dumps(jason),i))
                            else:
                                json_body.append(parse_ACH65_json(json.dumps(jason),i))
                        elif 'BCL25' in f:
                            if 'DEVICE' in f:
                                json_body.append(parse_BCL25_DEVICE_json(json.dumps(jason),i))
                            else:
                                json_body.append(parse_BCL25_json(json.dumps(jason),i))
                        elif 'BMWix_' in f:
                            id1 = f.split('BMWix_IP_')[1].split('_')[0]
                            id2 = f.split('ID_')[1].split('_')[0]
                            if 'DEVICE' in f:
                                json_body.append(parse_BMWix_DEVICE_json(json.dumps(jason), id1 + id2, i))
                            else:
                                json_body.append(parse_BMWix_json(json.dumps(jason), id1 + id2, i))
                        elif 'ElPtx350' in f:
                            if 'DEVICE' in f:
                                json_body.append(parse_ElPtx350_DEVICE_json(json.dumps(jason),i))
                            else:
                                json_body.append(parse_ElPtx350_json(json.dumps(jason),i))
                    except Exception as e:
                        logger.error("Error at step %s || %s", f, e)
                else:
                    logger.error("device Failed to fetch data from %s", url)
        # modbus section
        filename = datetime.now().strftime("%Y-%m-%d") + "_Helios_generatrice_modbus.json"
        register_table = read_and_save_all_modbus_registers(c, base_address, num_registers, filename)
        generatrice_modbus_registers = print_modbus_register_table(register_table, registers_info)
        logger.info("Modbus registers from génératrice: %s", generatrice_modbus_registers)
        json_body.append(generatrice_modbus_registers)

        try:
            insert_json_influxdb(measurement, json_body)
        except Exception as e:
            logger.critical("Error in saving the value to Influxdb: %s", e)

        execution_time = time.time() - start_time
        logger.info("Execution time : %s seconds", execution_time)
#        for i in ["B", "T"]:
 #          for f in Helios_default +  Helios_DL_devices[i]:
  #             url = "http://" + Helios_DL_IP[i] + "/" + f
   #            print(url)
    #           print (current_time.strftime("%Y-%m-%d") + "_Helios_DL" + i + "_" + f + ".json")
        # Pause de 5 minutes (300 secondes), moins le temps d'exécution pour éviter la dérive du temps 
        time.sleep(300 - execution_time)  # Sleep for 5 minutes (300 seconds), minus execution time to avoid timedrifting
