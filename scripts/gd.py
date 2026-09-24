import os
import json
import requests

BATCH_SIZE = 100000

IGNORED_FIELDS = {
    "Day",
    "Month",
    "Hours",
    "Minutes",
    "Seconds",
    "YearsSince1985",
    "hmiYear",
    "hmiMonth",
    "hmiDay",
    "hmiHour",
    "hmiMinute",
    "hmiSecond",
}

TABLES = {
         #"bmwix", 
         #"bcl25", 
         #"ach65", 
         #"elptx", 
         "gd"
}

CONTINUE = False 
URL = "http://172.233.253.95:32149"
ROOT_PATH = os.path.dirname(__file__)

FILES_LIST = []

REQUIRED_ROWS = ['IP', 'ID', 'side', 'boat', 'end_ts', 'start_ts', 'timestamp', 'component', 'value']

def publish_batch(session, headers, data):
    global CONTINUE

    if not data:
        return

    try:
        response = session.put(
            URL,
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()
        if CONTINUE is False: 
            input("continue: ")
            CONTINUE = True

    except Exception as error:
        raise Exception(
            f"Failed to publish data against {URL}: {error}"
        ) from error


def publish_data():
    dir_name = os.path.join(ROOT_PATH, "helios")

    if not os.path.isdir(dir_name):
        raise RuntimeError(f"Directory does not exist: {dir_name}")

    base_headers = {
        "type": "json",
        "dbms": "anotherpeak",
        "table": "location",
        "mode": "streaming",
        "Content-Type": "application/json",
    }

    files = [
        os.path.join(dir_name, fname)
        for fname in os.listdir(dir_name)
    ]

    with requests.Session() as session:

        for fname in files:

            table = os.path.basename(fname).split(".json")[0].lower()

            if "currentPosition" in fname:
                continue

            if table not in TABLES:
                continue

            print(f"Processing {table}")

            headers = base_headers.copy()
            headers["table"] = table

            try:
                with open(fname, "r") as f:

                    batch = []

                    for line in f:
                        raw_content = json.loads(line)

                        raw_row = {
                            key: raw_content.get(key)
                            for key in REQUIRED_ROWS
                        }

                        for key, value in raw_content.items():

                            if key in REQUIRED_ROWS:
                                continue

                            if key in IGNORED_FIELDS:
                                continue
                            row = {
                                **raw_row,
                                "component": key,
                                "value": value,
                                #"value": value if isinstance(value, (int, float)) else None,
                                #"str_value": value if not isinstance(value, (int, float)) else None,
                            }
                            batch.append(row)

                            # Send periodically instead of
                            # one request per input row.
                            if len(batch) >= BATCH_SIZE:
                        #print(batch)
                                publish_batch(session, headers, batch)
                                batch.clear()
                        #exit(1)

                    # Send remaining rows
                    if batch:
                        publish_batch(
                            session,
                            headers,
                            batch,
                        )

            except Exception as error:
                raise Exception(
                    f"Failed to read content from {fname}: {error}"
                ) from error

if __name__ == "__main__": 
    publish_data()
