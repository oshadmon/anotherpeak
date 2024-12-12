"""
Major Changes:
1. when executing a GET REST request, there's no need to convert from dict (request.json()) to serialized JSON and back to dict
2. the if /else for device is inside the parse processes
3. Instead of writing to list and then to file, we're writing directly into AnyLog -- if you want we can thread / parallelize the code for efficency
"""
import datetime
import logging
import time
from source.data_parse import *
from source.rest_api import *
from source.modbus import *

Helios_default = ["vessel", "errors", "info", "devices"]
Helios_DL_IP = {'B': "10.85.9.111:8481", 'T': "10.85.9.110:8481"}
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


logger = logging.getLogger("main_logger")
logger.setLevel(logging.DEBUG)  # Set the logger to the lowest level you want to capture (DEBUG > INFO > WARNING > ERROR > CRITICAL)



def main():
    start_time = time.time()  # Enregistrer le temps de début d'exécution
    current_time = datetime.datetime.now()

    json_body = []
    for i in ["B", "T"]:  # On parcourt Babord et Tribord et comme les componnents  ont le même nom, on rajoute "B" ou "T" pour les différencier
        for f in Helios_default:
            if f != "vessel":
                break
            url = f"http://127.0.0.1:8481/{f}"
            # url = f"http://{Helios_DL_IP[i]}/{f}"
            # On sauvegarde la donnée brute dans un fichier, un fichier par composant par jour
            filename = f"{current_time.strftime('%Y-%m-%d')}_Helios_DL_{i}_{f}.json"
            json_data = fetch_raw_json(url)
            if json_data and f == "vessel":
                data = parse_vessel_json(json_data, i)
            else:
                logger.error("%s Failed to fetch data from %s", f, url)
            if 'timestamp' not in data or not data['timestamp']:
                data['timestamp'] = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            print(filename, data)
        # on parcourt ici les composants hardware: batteries, chargeurs, convertisseurs, moteurs
        for f in Helios_DL_devices[i]:
            url = f"http://127.0.0.1:8481/{i}/{f}"
            # url = f"http://{Helios_DL_IP[i]}/device/{f}"
            filename = f"{current_time.strftime('%Y-%m-%d')}_Helios_DL_{i}_{f}.json"
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
            print(filename, data)

        # modbus section
        filename = datetime.datetime.now().strftime("%Y-%m-%d") + "_Helios_generatrice_modbus.json"
        register_table = read_and_save_all_modbus_registers(c, base_address, num_registers, filename)
        generatrice_modbus_registers = print_modbus_register_table(register_table, registers_info)
        logger.info("Modbus registers from génératrice: %s", generatrice_modbus_registers)
        print(filename, generatrice_modbus_registers)
        exit(1)



if __name__ == '__main__':
    main()
