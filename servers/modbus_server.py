from pyModbusTCP.server import ModbusServer, DataBank
import logging
import time
from torqeedo_modbus_datalogger_v2 import registers_info

# Initialize logging
logger = logging.getLogger("modbus_server")
logging.basicConfig(level=logging.DEBUG)

# Initialize the Modbus server
server = ModbusServer(host="0.0.0.0", port=502, no_block=True)

# List of initialized registers
initialized_registers = []


# Sample Modbus register initialization
def initialize_registers(registers_info):
    global initialized_registers
    for register_id, name, unit, reg_type, length, decimals in registers_info:
        if length == 4:
            value = 1000  # Example value for long registers
        elif length == 16:
            value = 123456  # Example string-like register
        else:
            value = 100  # Default test value

        # Set holding register value
        server.data_bank.set_holding_registers(register_id - 40001, [value])
        initialized_registers.append(register_id - 40001)
        logger.info(f"Register {register_id} initialized to {value}")


# Function to update registers dynamically
def update_registers():
    while True:
        for register_id in initialized_registers:
            current_value = server.data_bank.get_holding_registers(register_id, 1)[0]
            new_value = (current_value + 1) % 65536
            server.data_bank.set_holding_registers(register_id, [new_value])
            logger.info(f"Register {register_id + 40001} updated to {new_value}")
        time.sleep(5)


# Start the Modbus server
try:
    initialize_registers(registers_info)
    server.start()
    logger.info("Modbus server started")
    update_registers()
except Exception as e:
    logger.error(f"Server error: {e}")
finally:
    server.stop()
    logger.info("Modbus server stopped")