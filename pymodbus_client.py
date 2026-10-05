import sys
import time

from pymodbus.client import ModbusTcpClient
from pymodbus.pdu.pdu import ModbusPDU
from pymodbus import pymodbus_apply_logging_config

# use port 5020 instead of 502 for unprivileged sockets
client: ModbusTcpClient = ModbusTcpClient(host='192.168.86.205', port=5020)

pymodbus_apply_logging_config()

def check_coil() -> ModbusPDU:
    """Read coils and return result"""
    result: ModbusPDU = client.read_coils(1, count=4, device_id=1)
    return result

def check_register() -> ModbusPDU:
    """Read registers and return result"""
    result: ModbusPDU = client.read_holding_registers(40001, count=4, device_id=1)
    return result

def rw_loop() -> None:
    """"Write coils to be true or false"""
    client.write_coils(1, values=[True, True, False, True], device_id=1)
    client.write_registers(40001, values=[25, 36, 75, 6], device_id=1)
    check_coil()
    check_register()
    time.sleep(3)
    client.write_coils(1, values=[True, True, False, True], device_id=1)
    client.write_registers(40001, values=[25, 36, 75, 6], device_id=1)
    check_coil()
    check_register()
    time.sleep(3)

try:
    client.connect()
    # if connected, let coil infinitely loop
    while client.connect():
        rw_loop()
except KeyboardInterrupt:
    client.close()
    print('\nShutting down client.')
    sys.exit()
 

