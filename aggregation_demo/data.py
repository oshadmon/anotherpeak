import datetime
import os
import json

from rest_call import execute_command
DATA = os.path.join(__file__.split("aggregation_demo")[0], "lcdb", "2024-08-15_Helios_DLB_vessel.json")

if not os.path.isfile(DATA):
    print(DATA)
    raise FileNotFoundError

with open(DATA) as f:
    headers = {
        'command': 'data',
       'topic': "anotherpeak-demo",
       'User-Agent': 'AnyLog/1.23',
       'Content-Type': 'text/plain'
    }
    
    for line in f:
        dict_line = json.loads(line.split(": ", 1)[-1].strip())
        dict_line["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        execute_command(method="POST", conn="50.116.20.125:32149", headers=headers, payload=json.dumps(dict_line))
        exit(1)
