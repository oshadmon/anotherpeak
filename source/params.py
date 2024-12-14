"""
File consisting of static params
"""

Helios_default = [
    "vessel",
    "errors",
    "info",
    "devices"
]

Helios_DL_IP = {
    'B': "10.85.9.111:8481",
    'T': "10.85.9.110:8481"
}

ANYLOG_CONN = {
    "T": '178.79.168.109:32149',
    "B": '178.79.168.113:32149'
}


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

# Define the Modbus client start address and the number of registers to read
base_address = 40001
address_ranges = [(base_address, 40801), (43000, 43477)]
#address_ranges = [(base_address, 40201)]
num_registers = 10  # max 125 registers per poll for modbus

# Modbus client (la generatrice)
modbus_timeout = 5  # maximum time in second to wait for an answer from modbus device - it's not a ping, modbbus device is accessible but the device behind it may not, ie generatrice is switched off
max_modbus_retries = 3  # /!\ every retry will delay the writing into influxDB by the number of retries multiplied by modbus timeout
MODBUS_CONN = '127.0.0.1:502'

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




