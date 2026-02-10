import argparse
import json
import os
import datetime
import time

from rest_call import execute_command

TIMESTAMP_DICT = {
    "hmiYear": "%Y",
    "hmiMonth": "%m",
    "hmiDay": "%d",
    "hmiHour": "%H",
    "hmiMinute": "%M",
    "hmiSecond": "%S"
}

HEADERS = {
    'command': 'data',
    'topic': "anotherpeak-demo",
    'User-Agent': 'AnyLog/1.23',
    'Content-Type': 'text/plain'
}

def get_content(conn:str, data_file:str, vessel:str):
    with open(data_file) as f:
        for line in f:
            line = line.strip().split(': ', 1)[-1].strip()
            timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

            if line:
                line = json.loads(line)
                line["vessel"] = vessel

                for key in TIMESTAMP_DICT:
                    if line.get(key) is not None:
                        line[key] = int(timestamp.strftime(TIMESTAMP_DICT[key]))

                line["timestamp"] = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                execute_command(method="POST", conn=conn, headers=HEADERS, payload=json.dumps(line))
                # print(json.dumps(line, indent=2))
                time.sleep(10)
            # exit(1)


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=str, default=None, help="REST connection to AnyLog")
    parse.add_argument("file_path", type=str, default=None, help="file to pull data from")
    args = parse.parse_args()

    args.file_path = os.path.expanduser(os.path.expandvars(args.file_path))
    if not os.path.isfile(args.file_path):
        raise FileNotFoundError(f"Failed to locate {args.file_path}")
    vessel = os.path.basename(args.file_path).split('.')[0].split('_', 1)[-1].split("_vessel")[0]

    while True:
        get_content(conn=args.conn, data_file=args.file_path, vessel=vessel)

if __name__ == "__main__":
    main()
