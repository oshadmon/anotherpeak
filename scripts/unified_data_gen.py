import argparse
import datetime
import json

import bs4
import requests
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = "http://45.33.11.32/Sample-Data/vessel-data2/"
FULL_URL_PATH = None
FILES_LIST = {}
TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

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

REQUIRED_ROWS = ['IP', 'ID', 'side', 'boat', 'end_ts', 'start_ts', 'timestamp', 'component', 'value']



def _exec_cmd(method:str, url:str, headers:dict=None, payload:dict=None)->requests.request:
    try:
        response = requests.request(method=method.upper(), url=url, headers=headers, json=payload)
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute {url} (Error: {error})")

    return response

def _count_url_lines(url):
    """
    Fetches the content from the given URL and counts the number of lines.
    Returns the line count or raises an exception if something goes wrong.
    """
    try:
        # Open the URL and read its content
        with urllib.request.urlopen(url) as response:
            # Decode bytes to string and split into lines
            content = response.read().decode('utf-8', errors='replace')
            lines = content.splitlines()
            return len(lines)
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch URL: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")


def list_files():
    global FILES_LIST
    if not FULL_URL_PATH:
        raise ValueError(f"Missing value for FULL_URL_PATH param")

    response = _exec_cmd(method="GET", url=FULL_URL_PATH)
    if response:
        try:
            soup_response = bs4.BeautifulSoup(response.text, "html.parser")
            FILES_LIST = {link.get("href"): {
                            "total": _count_url_lines(url=urllib.parse.urljoin(FULL_URL_PATH, link.get("href"))),
                            "current": 0,
                            "timestamp": None} for link in soup_response.find_all('a') if
                link.get("href").endswith('.json') and "currentPosition" not in link.get("href")}

        except Exception as error:
            raise Exception(F"Failed to extract list of files from {FULL_URL_PATH} (Error: {error})")




def fix_timestamp(this_row:dict, previous_row:dict, last_timestamp:datetime.datetime|None=None)->(datetime.datetime, dict):
    if last_timestamp is None or previous_row is None:
        last_timestamp = datetime.datetime.now(datetime.timezone.utc)
    else:
        this_ts = datetime.datetime.strptime(this_row["timestamp"], TS_FORMAT)
        prev_ts = datetime.datetime.strptime(previous_row["timestamp"], TS_FORMAT)
        last_timestamp += abs(this_ts - prev_ts)
    this_row["timestamp"] = last_timestamp  # optional: write it back

    if this_row.get("start_ts") and this_row.get("end_ts"):
        start_ts = datetime.datetime.strptime(this_row["start_ts"], TS_FORMAT)
        end_ts   = datetime.datetime.strptime(this_row["end_ts"], TS_FORMAT)

        this_row["start_ts"] = last_timestamp
        this_row["end_ts"] = last_timestamp + abs(end_ts - start_ts)

    for key in ["timestamp", "start_ts", "end_ts"]:
        this_row[key] = this_row.get(key).strftime(TS_FORMAT)

    return last_timestamp, this_row

def format_rows(this_row):
    raw_row = {key: this_row.get(key) for key in REQUIRED_ROWS}
    batch = []
    table = this_row.get("component")
    for key, value in this_row.items():
        if key in REQUIRED_ROWS or key in IGNORED_FIELDS:
            continue
        row = {**raw_row, "component": key}
        if table in ["bcl25", "elptx"]:
            is_num = isinstance(value, (int, float))
            row["value"] = value if is_num else None
            row["str_value"] = None if is_num else value
        else:
            row["value"] = value
        batch.append(row)

    return batch


def main():
    global FULL_URL_PATH
    parse = argparse.ArgumentParser()
    parse.add_argument("boat", type=str, default="helios", choices=["helios", "hydraaix"])
    args = parse.parse_args()

    # FULL_URL_PATH  = urllib.parse.urljoin(BASE_URL, args.boat)
    FULL_URL_PATH = urllib.parse.urljoin(BASE_URL, args.boat) + '/'
    list_files()
    for file in FILES_LIST:
        current_line = FILES_LIST.get(file).get("current")
        total_lines = FILES_LIST.get(file).get("total")
        if current_line <= total_lines:
            content = _exec_cmd(method="GET",url=urllib.parse.urljoin(FULL_URL_PATH, file))

            this_line = content.text.splitlines()[current_line].strip()
            previous_line = content.text.splitlines()[current_line + 1 if current_line < total_lines else current_line - 1].strip()
            if this_line:
                this_line = json.loads(this_line)
            if previous_line:
                previous_line = json.loads(previous_line)


            FILES_LIST[file]["timestamp"], this_row = fix_timestamp(this_row=this_line, previous_row=previous_line,
                                                                    last_timestamp=FILES_LIST[file]["timestamp"])
            if file.split('.')[0].lower()  in ["bmwix", "bcl25", "ach65", "elptx", "gd"]:
                this_row = format_rows(this_row)
            # if file.split('.')[0].lower() not:
            #
            #     print(this_row)
            print(this_row)
            current_line += 1
            if current_line <= total_lines:
                current_line  = 0
            FILES_LIST[file]["current"] = current_line
    exit(1)



if __name__ == "__main__":
    main()