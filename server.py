import sys

from pymodbus import ModbusDeviceIdentification
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import ServerStop, StartTcpServer
from pymodbus import pymodbus_apply_logging_config

# creates a Modbus device with discrete inputs, coils, etc 
dev: ModbusDeviceContext = ModbusDeviceContext(
        co = ModbusSequentialDataBlock(1, [1]*100),
        di = ModbusSequentialDataBlock(10001, [1]*100),
        ir = ModbusSequentialDataBlock(30001, [1]*100),
        hr = ModbusSequentialDataBlock(40001, [1]*100)
    )

# lets server use data from DeviceContext
server_context: ModbusServerContext = ModbusServerContext(devices=dev, single=True)

# optional device attributes
identity: ModbusDeviceIdentification = ModbusDeviceIdentification()
identity.ProductName = 'RPi Modbus'
identity.VendorName = 'Raspberry Pi Foundation'
identity.MajorMinorRevision = "2.0.0"
identity.ModelName = "Raspberry Pi Modbus Server"
identity.ProductCode = "RPiM"

pymodbus_apply_logging_config()

def start_server(srv_context, identity) -> None:
    """Start server and listen for any incoming requests"""
    try:
        # use port 5020 instead of 502 for unprivileged sockets
        StartTcpServer(context=srv_context, identity=identity, address=('0.0.0.0', 5020))
    except:
        ServerStop()

if __name__ == '__main__':
    start_server(server_context, identity=identity)
    if KeyboardInterrupt:
        print("\nShutting down server.")
        sys.exit()
