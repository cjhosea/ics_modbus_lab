import sys

from pymodbus import ModbusDeviceIdentification
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import ServerStop, StartTcpServer

# creates a Modbus device with discrete inputs, coils, etc 
dev: ModbusDeviceContext = ModbusDeviceContext(
        di = ModbusSequentialDataBlock(0x01, [1]*50),
        co = ModbusSequentialDataBlock(0x01, [1]*50),
        ir = ModbusSequentialDataBlock(0x01, [1]*50),
        hr = ModbusSequentialDataBlock(0x01, [1]*50)
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


def start_server(srv_context, identity) -> None:
    """Start server and listen for any incoming requests"""
    try:
        StartTcpServer(context=srv_context, identity=identity, address=('0.0.0.0', 5020))
    except:
        ServerStop()

if __name__ == '__main__':
    start_server(server_context, identity=identity)
    if KeyboardInterrupt:
        print("\nShutting down server.")
        sys.exit()
