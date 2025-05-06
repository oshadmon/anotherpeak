from influxdb import InfluxDBClient

host = 'localhost'  # or your InfluxDB host
port = 8086  # or your InfluxDB port
database = 'electrificationBateaux'  # your InfluxDB database name
measurement = 'Helios'  # Measurement name for battery state of charge percent


def connect_influx(host:str='localhost', port:int=8086, db_name:str='electrificationBateaux', measurement='Helios'):
    try:
        InfluxDBClient.c
