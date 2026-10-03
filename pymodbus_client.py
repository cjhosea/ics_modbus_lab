import sys
import time

from gpiozero import LED
from pymodbus.client import ModbusTcpClient
from pymodbus.pdu.pdu import ModbusPDU

# use port 5020 instead of 502 for unprivileged sockets
client: ModbusTcpClient = ModbusTcpClient(host='192.168.86.80', port=5020)
led: LED = LED(17)

def check_coil() -> ModbusPDU:
    """Read coil and return result"""
    result: ModbusPDU = client.read_coils(51, count=1, device_id=1)
    return result

def led_light(result: ModbusPDU) -> None:
    """Turn LED on if coil is 1"""
    if result.bits[0] == True:
        led.on()
    else:
        led.off() 

def coil_loop() -> None:
    """"Write coils to be true or false"""
    client.write_coil(51, value=True, device_id=1)
    result: ModbusPDU = check_coil()
    led_light(result)
    time.sleep(3)
    client.write_coil(51, value=False, device_id=1)
    result: ModbusPDU = check_coil()
    led_light(result)
    time.sleep(3)

try:
    client.connect()
    # if connected, let coil infinitely loop
    while client.connect():
        coil_loop()
except KeyboardInterrupt:
    client.close()
    print('\nShutting down client.')
    sys.exit()
 

