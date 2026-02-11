import datetime
import os
import json
import time
from pydoc_data.topics import topics

import support

DATA_DIR = os.path.join(__file__.split("aggregation-demo")[0], "lcdb")
if not os.path.isdir(DATA_DIR):
    raise NotADirectoryError(f"Failed to locate {DATA_DIR}")

FILES = {
    "anotherpeak-tier1": "2024-08-15_Helios_DLB_vessel.json",
    "anotherpeak-tier2": "2024-08-15_Helios_DLB_BCL25_700_8_CH_IP_3_ID_65.json"
}

def publish_data(conn:str, row:dict, topic:str="anotherpeak"):
    headers = {
        "command": "data",
        "topic": topic,
        "User-Agent": "AnyLog/1.23",
        "Content-Type": "text/plain"
    }

    support.execute_command(method="POST", conn=conn, headers=headers, payload=json.dumps(row))


def data_generator():
    row_count = 280
    index = 0

    base_date = datetime.datetime.now() - datetime.timedelta(days=7)
    day_offset = 0   # moves forward 1 day after full file pass

    while True:   # infinite streaming loop
        rows = {}

        for i, topic in enumerate(FILES):
            fname = FILES[topic]
            file_path = os.path.join(DATA_DIR, fname)
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Failed to locate {file_path}")

            row, new_index = support.read_file(
                file_path,
                index=index,
                row_count=row_count
            )

            timestamp, line = row.split(": ", 1)
            time_timestamp = datetime.datetime.strptime(timestamp.split(" ")[-1], "%H:%M:%S")

            line = json.loads(line)

            # 🔥 Build rolling timestamp
            virtual_time = (base_date + datetime.timedelta(days=day_offset)).replace(
                hour=time_timestamp.hour,
                minute=time_timestamp.minute,
                second=time_timestamp.second
            )

            line["timestamp"] = virtual_time.strftime("%Y-%m-%d %H:%M:%S")
            line["vessel"] = "Helios_DLB"
            # line["side"] = "DLB"

            rows[fname] = line
            print(line)
            publish_data(conn="50.116.20.125:32149", row=line, topic=topic)
            if i == len(FILES) - 1:
                index = new_index
                time.sleep(30)

        # 🔁 If we completed a full file → advance 1 day
        if index == 0:
            day_offset += 1
            print(f"Advancing to next day: +{day_offset}")

        # yield rows   # stream rows into pipeline



if __name__ == "__main__":
    for _ in data_generator():
        pass