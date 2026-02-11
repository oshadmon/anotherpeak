import requests

def execute_command(method:str, conn:str, headers:dict, payload=None):
    try:
        response = requests.request(method=method.upper(), url=f"http://{conn}", headers=headers, data=payload)
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute {method.upper()} against {conn} (Error: {error})")
    return response