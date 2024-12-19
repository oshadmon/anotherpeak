import json
import os
import re
import random

from flask import Flask, jsonify
from source.file_io import read_file
from torqeedo_modbus_datalogger_v2 import Helios_DL_devices, Helios_default  # Assuming this imports the devices dictionary

app = Flask(__name__)

# Directory to hold your mock JSON files
JSON_DIRECTORY = os.path.join(os.path.dirname(__file__).split('server')[0], 'lcdb')  # Change this path to where your mock JSON files are located


def __clean_json(data):
    timestamp_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}): '
    clean_data = []

    # Iterate over each line in the data
    for line in data.split("\n"):
        try:
            # Search for the timestamp in the beginning of the line
            match = re.match(timestamp_pattern, line)

            if match:
                # Extract timestamp from the line
                timestamp_str = match.group(1)

                # Remove the timestamp from the line to leave just the JSON
                clean_line = re.sub(timestamp_pattern, '', line)

                # Parse the JSON content
                json_data = json.loads(clean_line)

                # Convert the timestamp string to a datetime object and add it to the JSON data
                json_data = json_data[0] if isinstance(json_data, list) else json_data
                json_data['timestamp'] = timestamp_str  # Add timestamp in ISO 8601 format

                # Append the modified JSON to the clean_data list
                clean_data.append(json_data)

        except json.JSONDecodeError:
            pass  # If JSON decoding fails, ignore that line

    # Return a random item from the cleaned data
    return random.choices(clean_data)[0] if clean_data else None


@app.route('/<side>', methods=['GET'])
@app.route('/<side>/<component>', methods=['GET'])
def get_json_data(side, component=None):
    """
    Retrieves the JSON data for the given side (B/T) and component.
    side: 'B' or 'T' (the side of the vessel)
    component: the name of the component (e.g., 'vessel', 'ACH65_IP_3_ID_66', etc.)
    """
    # Ensure side is valid
    if side not in Helios_DL_devices and side not in Helios_default:
        return jsonify({'error': 'Invalid side'}), 400

    # Check if the component exists in the list for the given side
    if component:
        if side in Helios_DL_devices and component not in Helios_DL_devices[side]:
            return jsonify({'error': 'Component not found for this side'}), 404
        # Generate the file name for side/component
        file_name = f'2024-08-15_Helios_DLB_{component}.json'
    else:
        # If no component, use default logic to create file name
        if side in Helios_default:
            file_name = f'2024-08-15_Helios_DLB_{side}.json'
        else:
            return jsonify({'error': 'Component not provided or file not found for this side'}), 400

    file_path = os.path.join(JSON_DIRECTORY, file_name)

    if os.path.exists(file_path):
        # Read and return the contents of the file
        data = read_file(file_path=file_path)
        return __clean_json(data), 200  # Return the file content with HTTP 200 OK
    else:
        return jsonify({'error': 'File not found'}), 404  # Return 404 if the file does not exist



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8481)  # The default port is 8481 in your original code
