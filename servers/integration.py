from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient
from flask import Flask, jsonify
import threading
import logging
import time

# Initialize logging
logger = logging.getLogger("modbus_rest_server")
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Initialize the Modbus server
server = ModbusServer(host="0.0.0.0", port=502, no_block=True)
initialized_registers = []

# Initialize Modbus client (for REST API access)
client = ModbusClient(host="localhost", port=502, auto_open=True)

# Sample Modbus register initialization
def initialize_registers():
    global initialized_registers
    registers_info = [
        (40001, "Sensor1", "Unit", "Type", 4, 0),
        (40002, "Sensor2", "Unit", "Type", 4, 0),
    ]

    for register_id, _, _, _, length, _ in registers_info:
        value = 1000 if length == 4 else 100
        server.data_bank.set_holding_registers(register_id - 40001, [value])
        initialized_registers.append(register_id - 40001)
        logger.info(f"Register {register_id} initialized to {value}")

# Periodically update registers
def update_registers():
    while True:
        for register_id in initialized_registers:
            current_value = server.data_bank.get_holding_registers(register_id, 1)[0]
            new_value = (current_value + 1) % 65536
            server.data_bank.set_holding_registers(register_id, [new_value])
            logger.info(f"Register {register_id + 40001} updated to {new_value}")
        time.sleep(5)

# REST API endpoint to get Modbus register data
@app.route('/register/<int:register_id>', methods=['GET'])
def get_register_data(register_id):
    if client.is_open():
        data = client.read_holding_registers(register_id - 40001, 1)
        if data:
            return jsonify({
                "register_id": register_id,
                "value": data[0]
            }), 200
        else:
            return jsonify({"error": "Register not found"}), 404
    else:
        return jsonify({"error": "Modbus server not available"}), 500

# Start servers
if __name__ == '__main__':
    try:
        # Start Modbus server
        initialize_registers()
        server_thread = threading.Thread(target=server.start)
        server_thread.start()

        # Start periodic register updates
        update_thread = threading.Thread(target=update_registers)
        update_thread.start()

        # Start Flask REST API
        app.run(debug=True, host='0.0.0.0', port=8481)

    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.stop()
        logger.info("Modbus server stopped")
