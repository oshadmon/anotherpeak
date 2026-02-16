# AnotherPeak Aggregation Demo 

Data can be seen via [Remote-GUI](http://50.116.20.125:3001/dashboard/) - **Destination**: `50.116.20.125:32149`

The data provided in [lcdb](../lcdb) can be broken down into 4 tiers of information:
* **Tier 1** - Core Operational State (Critical). <br/>These directly represent system-level state and are what operators, analytics, and dashboards mostly care about:

  * 2024-08-15_Helios_DLB_vessel.json
  * 2024-08-15_Helios_DLT_vessel.json
```json
2024-08-15 00:03:57: {"acChargerPowerPercent": 40.5, "batteryStateOfChargePercent": 90, "boxLinkEnable": 1, "buttonCenterState": 0, "buttonRightState": 0, "currentBatteryPower": 300, "currentHeading": 0, "currentPositionLatitude": 45.70500799999999, "currentPositionLongitude": 5.885448999999994, "currentPositionToggle": 1, "dcacEnable": 0, "dcacPower": 0, "dcacPowerConfirmed": 0, "dcacPowerConfirmedPercent": 0, "dcacPowerPercent": 0, "dcdcEnable": 0, "dcdcPower": 0, "dcdcPowerConfirmed": 0, "dcdcPowerConfirmedPercent": 0, "dcdcPowerPercent": 0, "debug": 0, "displayEnable": 1, "distanceDestination": 5114.8, "distanceHome": 5114.8, "drivePowerConfirmed": 0, "drivePowerConfirmedPercent": 0, "driveType": "parker_", "efficientGenSetPowerHmi": 5, "elPtxPower": 0, "elPtxPowerConfirmed": 50, "elPtxPowerConfirmedPercent": 100, "elPtxPowerPercent": 127.5, "elPtxVisible": 1, "gCommand": "undefined", "gCommandState": "unknown", "gensetType": "", "headingDestination": 188.20000000000002, "headingHome": 188.20000000000002, "hmiDay": 15, "hmiHour": 0, "hmiMinute": 3, "hmiMonth": 8, "hmiSecond": 55, "hmiSmuIp": 0, "hmiYear": 2024, "hvBatteryCapacity": 146.232, "hvBatteryType": "bmwi3_", "hvSolarVisible": 0, "hydroGenerationPort": "autoUnavailable", "hydroGenerationStbd": "autoUnavailable", "kickDownTimer": 0, "lengthUnit": "unit not selected", "lvBatteryCapacity": 0, "lvBatteryMaxCapacity": 0, "lvBatteryStateOfChargePercent": 0, "lvBatteryType": "", "lvBatteryVoltage": 0, "lvBatteryVoltagePercent": 0, "lvSolarVisible": 0, "maxBatteryPower": 300, "maxGenSetPowerHmi": 0, "maxPower": 3, "maxSolarPower": 0, "maxSolarPower_hv": 0, "maxSpeed": 1, "minGenSetPowerHmi": 5, "motorPowerCombined": 0, "motorPowerCombinedPercent": 0, "motorPowerLimit": 0, "nightModeActive": 0, "portAcChargerEnable": 1, "portAcChargerPower": 0, "portAcChargerVisible": 1, "portBatteryConnectionState": "all", "portBatteryStateOfChargePercent": 127, "portBatteryStateOfChargePercentVisible": 0, "portDriveState": "notPresent", "portGenSetEnable": 0, "portGenSetFuelConsumption": 0, "portGenSetPower": 0, "portGenSetPowerPercent": 0, "portGenSetVisible": 0, "portHvBatteryVisible": 1, "portMotorPower": 0, "portMotorPowerPercent": 0, "portRpmShaft": 0, "portRpmShaftPercent": 0, "portStarterBatteryVisible": 0, "portTankLevel": 0, "portTankLevelPercent": 0, "portTankVisible": 0, "portThrottleGearState": "Unknown", "powerBalance": 16.889999999999986, "ptoPower": 0, "ptoPowerConfirmed": 0, "ptoPowerConfirmedPercent": 0, "ptoPowerPercent": 0, "ptoVisible": 0, "rangeBattery": 0, "rangeFuel": 0, "recoveryState": "0", "regenerationEnable": 0, "regenerationPower": 0, "regenerationPowerPercent": 0, "resolution": 0, "runTimeGenset": 0, "scuConnectionState": "0x0", "selectSystemMode": "Electric", "serverCompilationTime": 22091029, "serverCpuLoad": 10.5, "serverMemoryUsage": 33384, "serverSoftwareVersion": 17170441, "socDestination": 0, "socHome": 0, "sogValid": 1, "solarPower": 0, "solarPower_hv": 0, "speedOverGround": 0.038, "speedOverGroundFixed": 0.02, "speedOverGroundPercent": 0, "speedThroughWater": 0, "starterBatteryVoltage": 13.200000000000001, "starterBatteryVoltagePercent": 94.5, "stbdAcChargerEnable": 1, "stbdAcChargerPower": 17.879999999999995, "stbdAcChargerVisible": 1, "stbdBatteryConnectionState": "all", "stbdDriveState": "offByCharger", "stbdGenSetEnable": 0, "stbdGenSetFuelConsumption": 0, "stbdGenSetPower": 0, "stbdGenSetPowerPercent": 0, "stbdGenSetVisible": 0, "stbdHvBatteryVisible": 1, "stbdMotorPower": 0, "stbdMotorPowerPercent": 0, "stbdRpmShaft": 0, "stbdRpmShaftPercent": 0, "stbdStarterBatteryVisible": 1, "stbdTankLevel": 0, "stbdTankLevelPercent": 0, "stbdTankVisible": 0, "stbdThrottleGearState": "Neutral", "systemState": "device_wake", "tankLevelCombinedPercent": 0, "timeBattery": 0, "timeDestHour": 0, "timeDestMinute": 0, "timeHomeHour": 0, "timeHomeMinute": 0, "timeToFullMinute": 130, "trip": 280.154, "updateRateMs": 1000, "vesselState": "Invalid"}
2024-08-15 00:08:57: {"acChargerPowerPercent": 41, "batteryStateOfChargePercent": 91, "boxLinkEnable": 1, "buttonCenterState": 0, "buttonRightState": 0, "currentBatteryPower": 300, "currentHeading": 0, "currentPositionLatitude": 45.70500799999999, "currentPositionLongitude": 5.885449999999992, "currentPositionToggle": 0, "dcacEnable": 0, "dcacPower": 0, "dcacPowerConfirmed": 0, "dcacPowerConfirmedPercent": 0, "dcacPowerPercent": 0, "dcdcEnable": 0, "dcdcPower": 0, "dcdcPowerConfirmed": 0, "dcdcPowerConfirmedPercent": 0, "dcdcPowerPercent": 0, "debug": 0, "displayEnable": 1, "distanceDestination": 5114.8, "distanceHome": 5114.8, "drivePowerConfirmed": 0, "drivePowerConfirmedPercent": 0, "driveType": "parker_", "efficientGenSetPowerHmi": 5, "elPtxPower": 0, 
```
* **Tier 2** - Equipment-Level Operational Telemetry (Useful, but Optional). <br/>These give deep insight, but aren’t always required for a UNS MVP.
  * **2024-08-15_Helios_DLB_BCL25_700_8_CH_IP_3_ID_65.json**
  * **2024-08-15_Helios_DLT_BCL25_700_8_CH_IP_3_ID_65.json**
  * 2024-08-15_Helios_DLB_BMWix_IP_3_ID_33.json 
  * 2024-08-15_Helios_DLB_BMWix_IP_3_ID_49.json 
  * 2024-08-15_Helios_DLB_BMWix_IP_3_ID_81.json 
  * 2024-08-15_Helios_DLB_BMWix_IP_4_ID_49.json
  * 2024-08-15_Helios_DLT_BMWix_IP_3_ID_33.json 
  * 2024-08-15_Helios_DLT_BMWix_IP_3_ID_49.json 
  * 2024-08-15_Helios_DLT_BMWix_IP_3_ID_81.json
  * 2024-08-15_Helios_DLT_BMWix_IP_4_ID_49.json
  * 2024-08-15_Helios_generatrice_modbus.json

```json
2024-08-15 00:04:16: {"gActAcCurrent": 0.22000000000002728, "gActAcFrequency": 49.900000000000006, "gActAcVoltage": 389.20000000000005, "gActDcPower": 0.040000000000020464, "gActDcVoltage": 401.1, "gActElectronicTemperature": 50, "gCommand": "Enable", "gCommandAcCurrentLimitPP": 29, "gCommandDcPowerLimit": 0, "gCommandMaxDcVoltage": 403.1, "gCoolingPolicy": "Normal", "gDisableReason": "unknown", "gError": "NoError", "gIsSlave": 0, "gMaxDcPower": 22, "gParamMaxAcCurrentPP": 32, "gSimConnectedPhaseCount": 1, "gState": "PreOperational", "gWake": 1}
2024-08-15 00:09:01: {"gActAcCurrent": 0.20000000000004547, "gActAcFrequency": 49.900000000000006, "gActAcVoltage": 389.8, "gActDcPower": 0.040000000000020464, "gActDcVoltage": 401, "gActElectronicTemperature": 50, "gCommand": "Enable", "gCommandAcCurrentLimitPP": 29, "gCommandDcPowerLimit": 0, "gCommandMaxDcVoltage": 403.1, "gCoolingPolicy": "Normal", "gDisableReason": "unknown", "gError": "NoError", "gIsSlave": 0, "gMaxDcPower": 22, "gParamMaxAcCurrentPP": 32, "gSimConnectedPhaseCount": 1, "gState": "PreOperational", "gWake": 1}
```

* **Tier 3** - Safety / Diagnostics Layer (Advanced)<br/>These files provide insulation monitoring, protection relays, and error diagnostics.
  * 2024-08-15_Helios_DLB_BMWixIsoMon_IP_3_ID_34.json 
  * 2024-08-15_Helios_DLB_BMWixIsoMon_IP_3_ID_50.json 
  * 2024-08-15_Helios_DLB_BMWixIsoMon_IP_3_ID_82.json 
  * 2024-08-15_Helios_DLB_BMWixIsoMon_IP_4_ID_50.json 
  * 2024-08-15_Helios_DLT_BMWixIsoMon_IP_3_ID_34.json 
  * 2024-08-15_Helios_DLT_BMWixIsoMon_IP_3_ID_50.json 
  * 2024-08-15_Helios_DLT_BMWixIsoMon_IP_3_ID_82.json 
  * 2024-08-15_Helios_DLT_BMWixIsoMon_IP_4_ID_50.json
  * 2024-08-15_Helios_DLB_ElPtx350_IP_4_ID_81.json
  
* **Tier 4** - Static Metadata (Not Telemetry)<br/>These files define device metadata, system info, and configuration.
  * 2024-08-15_Helios_DLB_devices.json 
  * 2024-08-15_Helios_DLT_devices.json 
  * 2024-08-15_Helios_DLB_info.json 
  * 2024-08-15_Helios_DLT_info.json


For our demo I'm going to focus only on tier 1 and 2 of the data and do the following: 
1. create a mapping policies that breaks down the data into smaller tables -- I will use two files per tier, corresponding to the sample data shown above. 
2. insert data into tables 
3. create a UNS logic to demonstrate gainst 
```tree
Company (root) 
|- Boat 
   |- Side (DLB vs DLT)
      |- Device  (table) 
         |- Sensor (column / keys from table) 
```