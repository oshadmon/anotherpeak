import argparse
import copy
import json
import os 
import requests

ROOT_PATH = os.path.dirname(__file__)
FILES_LIST = []

REQUIRED_ROWS = ['IP', 'ID', 'side', 'boat', 'end_ts', 'start_ts', 'timestamp', 'component', 'value']

def publish_data(): 
    headers = {
        "type": "json",
        "dbms": "anotherpeak",
        "table": "location",
        "mode": "streaming",
        "Content-Type": "application/json"
    }
 
    dir_name = os.path.join(ROOT_PATH, "helios")
    if not os.path.isdir(dir_name): 
        exit(1) 

    FILES_LIST = [os.path.join(dir_name, fname) for fname in os.listdir(dir_name)]
 
    for fname in FILES_LIST:
        headers["table"] = os.path.basename(fname).split(".json")[0].lower()

        if os.path.isfile(fname): 
            try:
                with open(fname, 'r') as f: 
                    if "currentPosition" not in fname and headers["table"] not in ["bmwix", "bcl25", "ach65", "elptx", "gd"]:
                        print(headers["table"])
                        data = [json.loads(row.split('\n')[0]) for row in f.readlines()]
                        try: 
                            response = requests.put(url="http://172.233.253.95:32149" , headers=headers, json=data)
                            response.raise_for_status()
                        except Exception as error: 
                            raise Exception(f"Failed to publish data against http://172.233.253.95:32149 (Error: {error})")
            except Exception as error: 
                raise Exception(f"Failed to read content from {fname} (Error: {error})")

            
def main(): 
    global FILES_LIST 
    global MAX_LINES 
    parse = argparse.ArgumentParser()
    parse.add_argument("boat", type=str) 
    parse.add_argument("--conn", type=str)
    args = parse.parse_args() 

    if args.boat == "helios": 
        MAX_LINES = 4724
    else: 
        MAX_LINES = 5960

if __name__ == "__main__":
    # main()
    publish_data()
