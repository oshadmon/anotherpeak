import requests
from source.logger_config import logger

# this method is instead of fetch_raw_json
def fetch_raw_json(url):
    """
    Given a URL pull data and add timestamp
    :args:
        url:str - URL to execute request against
    :params:
        data:dict - Data from URL request
    :return:
        data
    """
    data = None
    try:
        response = requests.get(url)
    except requests.ConnectionError as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {url} (Erreur: {error})')
    except requests.Timeout as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {url} (Erreur: {error})')
    except requests.RequestException as error:
        logger.critical(f'Impossible de récupérer les données de {url} (Erreur: {error})')
    else:
        if not 200 <= int(response.status_code) < 300:
            logger.critical(f'Impossible de récupérer les données de {url} (Réseau Erreur: {response.status_code})')
        else:
            try:
                data = response.json()
            except ValueError as error:
                logger.critical(f'Échec de la conversion de la sortie de réponse en JSON (Erreur: {error})')
            # else:
            #     data = data[0] if isinstance(data, list) else data
            #     data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return data


def anylog_blockchain_get(conn:str, cmd:str):
    """
    (blockchain) GET command against the database
    :args:
        conn:str - REST connection information
        cmd:str - `blockchain get`
    :params:
        headers:dict - REST headers
        data:list - REST results
        response:requests.GET - response from GET
    :return:
        data
    """
    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }
    data = []
    try:
        response = requests.get(url=f"http://{conn}", headers=headers)
    except requests.ConnectionError as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {conn} (Erreur: {error})')
    except requests.Timeout as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {conn} (Erreur: {error})')
    except requests.RequestException as error:
        logger.critical(f'Impossible de récupérer les données de {conn} (Erreur: {error})')
    else:
        if not 200 <= int(response.status_code) < 300:
            logger.critical(f'Impossible de récupérer les données de {conn} (Réseau Erreur: {response.status_code})')
        else:
            try:
                data = response.json()
            except ValueError as error:
                logger.critical(f'Échec de la conversion de la sortie de réponse en JSON (Erreur: {error})')
    return data

def anylog_blockchain_post(conn:str, payload:str):
    """
    Publish blockchain policy into AnyLog via POST
    :args:
        conn:str - REST connection information
        payload:str - policy to publish
    :params:
       headers:dict - REST headers
       response:requests.GET - response from GET
    """
    headers = {
        "command": "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        "User-Agent": "AnyLog/1.23"
    }

    try:
        response = requests.post(url=f'http://{conn}', headers=headers, data=payload)
    except requests.ConnectionError as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {conn} (Erreur: {error})')
    except requests.Timeout as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {conn} (Erreur: {error})')
    except requests.RequestException as error:
        logger.critical(f'Impossible de récupérer les données de {conn} (Erreur: {error})')
    else:
        if not 200 <= int(response.status_code) < 300:
            logger.critical(f'Impossible de récupérer les données de {conn} (Réseau Erreur: {response.status_code})')


def anylog_data_put(conn:str, db_name:str, table_name:str, data:str):
    """
    Publish data into AnyLog via PUT
    :args:
        conn:str - REST connection information
        data:list - data to publish into AnyLog (operator) node
    :params:
       headers:dict - REST headers
       response:requests.GET - response from GET
    """
    headers = {
        'type': 'json',
        'dbms': db_name,
        'table': table_name,
        'mode': 'streaming',
        'Content-Type': 'text/plain',
        'User-Agent': 'AnyLog/1.23'
    }

    try:
        response = requests.put(url=f'http://{conn}', headers=headers, data=data)
    except requests.ConnectionError as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {conn} (Erreur: {error})')
    except requests.Timeout as error:
        logger.critical(f'Erreur de dépassement de délai de connexion par rapport à {conn} (Erreur: {error})')
    except requests.RequestException as error:
        logger.critical(f'Impossible de récupérer les données de {conn} (Erreur: {error})')
    else:
        if not 200 <= int(response.status_code) < 300:
            logger.critical(f'Impossible de récupérer les données de {conn} (Réseau Erreur: {response.status_code})')



