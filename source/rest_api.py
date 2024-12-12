import requests
from torqeedo_modbus_datalogger_v2 import logger

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