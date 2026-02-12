import json
import re

import requests


def camel_to_snake(name:str)->str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def read_file(file_path:str, index:int, row_count:int):
    try:
        with open(file_path, 'r') as f:
            for line_index, line in enumerate(f, start=1):
                if line_index == index + 1:
                    index += 1
                    if index > row_count:
                        index = 0
                    return line, index
    except Exception as error:
        raise Exception(f"Failed to read content from {file_path} (Error: {error})")


def __extract_asterisk(table_columns: list, data:dict)->list:
    """
    Expands table_columns with wildcards (*) to actual keys in data.
    """
    updated_columns = set()  # use set to avoid duplicates
    for column in table_columns:
        if '*' in column:
            base = column.replace('*', '')
            for key in data:
                if key.startswith(base):
                    updated_columns.add(key)
        else:
            if column in data:
                updated_columns.add(column)

    return list(updated_columns)

def calculate_data_types(table_columns:list, data)->dict:
    data_types = {key: [] for key in __extract_asterisk(table_columns=table_columns, data=data[0])}

    for key in data_types:
        for row in data:
            if row.get(key) is not None:
                if isinstance(row.get(key), int):
                    data_types[key].append("int")
                elif isinstance(row.get(key), float):
                    data_types[key].append("float")
                elif isinstance(row.get(key), bool):
                    data_types[key].append("bool")
                else:
                    data_types[key].append("string")

    for key in data_types:
        if all(value == data_types[key][0] for value in data_types[key]):
            data_types[key] = data_types[key][0]
        elif all(value in ["int", "float"] for value in data_types[key]):
            data_types[key] = "float"
        else:
            data_types[key] = "string"

    return data_types

def execute_command(method:str, conn:str, headers=dict, payload:str=None)->requests.Response:
    try:
        response = requests.request(method=method.upper(), url=f"http://{conn}", headers=headers, data=payload)
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute {method.upper()} against {conn} (Error: {error})")
    return response