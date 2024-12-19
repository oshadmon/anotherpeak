import datetime
import json
import os
from os import times

DATA_DIR = os.path.join(os.path.dirname(__file__).split("source")[0], 'data')

def read_file(file_path:str):
    """
    Read content from file
    :args:
        file_path:str - file to read
    :params:
        content - content from file
        full_path:str - exptended fule path
    :return:
        content
    """
    content = None
    full_path = os.path.join(file_path)
    if os.path.isfile(full_path):
        try:
            with open(full_path) as f:
                try:
                    content = f.read()
                except Exception as error:
                    raise Exception(f'Failed to read content from {full_path} (Error: {error})')
        except Exception as error:
            raise Exception(f'Failed to open file {full_path} to be raed (Error: {error})')
    else:
        raise Exception(f'Failed to locate file {full_path}')

    return content


def write_file(table_name:str, db_name:str, data:list):
    """
    write content to (JSON) file
    :args:
        table_name:str - logical table name (to be used for table name)
        data:list - list rows to store
    :params:
        timestamp:str - timestamp to be used as part of file name
        file_name:str - file to write data to

    """
    if not os.path.isdir(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except Exception as error:
            raise Exception(f'Failed to create data dir {DATA_DIR} (Error: {error})')


    timestamp = datetime.datetime.now().strftime('%Y_%m_%d')
    if data and isinstance(data, list) and len(data) > 0:
        if '.' in data[0]['timestamp']:
            timestamp = datetime.datetime.strptime(data[0]['timestamp'], "%Y-%m-%d %H:%M:%S.%f").strftime('%Y_%m_%d')
        else:
            timestamp = datetime.datetime.strptime(data[0]['timestamp'], "%Y-%m-%d %H:%M:%S").strftime('%Y_%m_%d')
    file_name = os.path.join(DATA_DIR, f"{db_name}.{table_name}.0.{timestamp}.json")

    if not os.path.isfile(file_name):
        try:
            open(file_name, 'w').close()
        except Exception as error:
            raise Exception(f"Failed to create file {file_name} (Error: {error})")

    try:
        with open(file_name, 'a') as f:
            for line in data:
                try:
                    f.write(f"{json.dumps(line)}\n")
                except Exception as error:
                    raise Exception(f'Failed to write content into file (file name: {file_name} | line number: {data.index(line)} | Error: {error})')
    except Exception as error:
        raise Exception(f'Failed to open file {file_name} to write data (Error: {error})')


