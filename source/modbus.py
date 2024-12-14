import datetime
import time
import socket

from source.logger_config import logger
from pyModbusTCP.client import ModbusClient
from source.params import base_address, address_ranges, num_registers, modbus_timeout, max_modbus_retries, registers_info

# Fonction pour imprimer le tableau des registres Modbus
def print_modbus_register_table(register_table, registers_info):
    # prints and creates a list of all registers described in registers_info list
    gen_body = {}
    for info in registers_info:
        register_id, name, unit, type, length, decimals = info

        if length == 4:
            value = combine_modbus_registers(register_table, register_id, 2)
        elif length == 3:
            value = combine_modbus_registers(register_table, register_id, 2)
        elif length == 16:
            value = combine_modbus_registers(register_table, register_id, 4)
        elif length == 32:
            value = combine_modbus_registers(register_table, register_id, 8)
        else:
            value = register_table.get(register_id)

        if value is not None:
            if decimals is not None and unit is not None:
                formatted_value = value / (10 ** decimals)
                gen_body[name] = formatted_value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {formatted_value} {unit}")
            elif decimals is not None:
                formatted_value = value / (10 ** decimals)
                gen_body[name] = formatted_value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {formatted_value}")
            elif unit is not None:
                gen_body[name] = value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {value} {unit}")
            else:
                gen_body[name] = value
                logger.info(f"Register {register_id} [{length}]: {value} || {name}: {value}")
        else:
            logger.info(f"Register {register_id} [{length}]: No data || {name}")

    return gen_body


# Fonction pour lire et sauvegarder tous les registres Modbus dans un fichier
def read_modbus_memory_block(client, start_address, num_registers):
    # Read a block of memory and return the raw register values.
    #logger.info(f"{client} ||| {start_address} ||| {num_registers}")
    try:
        start_time = time.time()
        regs_l = client.read_holding_registers(start_address - base_address, num_registers)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > modbus_timeout:
            logger.error(f"{client} ||| {start_address} ||| {num_registers} read_timeout: {elapsed_time}")
            return ('read_timeout', None)
        elif regs_l:
            return ('success', regs_l)
        else:
            return ('no_read', None)
    except socket.timeout:
        logger.error(f"Timeout occurred while reading Modbus memory block starting at address {start_address}")
        return ('socket_timeout', None)
    except Exception as e:
        logger.error(f"Failed to read memory block starting at address {start_address}: {e}")
        return ('exception_error', None)


def read_and_save_all_modbus_registers(connection, base_address, block_size, filename):
    register_table = {}
    retries = 0
    for start_address, end_address in address_ranges:
        total_registers = end_address - start_address + 1
        # Calculate the number of blocks to read
        num_blocks = (total_registers + block_size - 1) // block_size
        logger.info("total_registers: %s // block_size: %s // num_blocks: %s", total_registers, block_size, num_blocks)

        for i in range(num_blocks):
            current_address = start_address + i * block_size
            count = min(block_size, total_registers - i * block_size)
            status, raw_data = read_modbus_memory_block(connection, current_address, count)
            if status == 'success':
                for j, value in enumerate(raw_data):
                    register_id = current_address + j
                    register_table[register_id] = value
            elif status == 'read_timeout' or status == 'socket_timeout':
                retries+=1
                logger.error("Error %s Modbus ||  number of retries left: %s", status, max_modbus_retries - retries)
                if retries >= max_modbus_retries:
                    break
            else:
                logger.error("No data returned for address range %s to %s: %s", current_address, current_address + count - 1, status)

        if retries >= max_modbus_retries:
            logger.error("%s Modbus max retries reached: %s", status, retries)
            break

    return register_table


def combine_modbus_registers(register_table, register_id, length):
    value = 0
    for offset in range(length):
        addr = register_id + offset
        if addr in register_table:
            value = (value << 16) | register_table[addr]
        else:
            return None
    return value

def modbus_main(conn:str):
    filename = datetime.datetime.now().strftime("%Y-%m-%d") + "_Helios_generatrice_modbus.json"
    ip, port = conn.split(":")

    try:
        c = ModbusClient(host='127.0.0.1', port=int(port), auto_open=True, timeout=modbus_timeout)
    except Exception as error:
        logger.critical(f'Échec de la connexion à Modbus contre {conn} (Erreur: {error})')

    register_table = read_and_save_all_modbus_registers(c, base_address, num_registers, filename)
    generatrice_modbus_registers = print_modbus_register_table(register_table, registers_info)
    logger.info("Modbus registers from génératrice: %s", generatrice_modbus_registers)

    return filename, generatrice_modbus_registers
