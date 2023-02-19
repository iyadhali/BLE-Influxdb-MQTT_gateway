import asyncio
import platform
import sys
from bleak import BleakClient, discover
import numpy as np
import influxdb_client
import random

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
var = []
r = 0

from paho.mqtt import client as mqtt_client

#InfluxDB API details
# You can generate an API token from the "API Tokens Tab" in the UI
token = "7J9lPnAS9LLrotu4da8osTmR6B4MQ2Do_YGs2tkfLgf8sCxrWmsX0Vlpdqk-d2Q3ZHXgwc_lSg2OBQ5zKeoF1g=="
org = "fyp"
bucket = "fyp"
url = "http://localhost:8086"

broker = '1.9.126.5'
port = 1883

#MQTT access detaails
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'iotadmin'
password = 'XR5nsgs0cSqy3vR'



clientt = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


client = mqtt_client.Client(client_id)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.connect(broker, port)


#BLE UUID for both sensors
accelerometer = '13012F01-F8C3-4F4A-A8F4-15CD926DA146'
current_sensor = '13012F02-F8C3-4F4A-A8F4-15CD926DA146'

#BLE device adress
ADDRESS = (
    "84:CC:A8:77:97:76"
    if platform.system() != "ble"
    else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"
)
class D:
    def __init__(self):
        self.queue = asyncio.Queue(1)


#Coroutine 1 - Receive data from the BLE device
    async def cor1(self, address):

          async with BleakClient(address, winrt=dict(use_cached_services=True)) as client:

            print(f"Connected: {client.is_connected}")
            while True:
                #RECEIVE VIBRATION VALUES
                val = await client.read_gatt_char(accelerometer)
                print(val)
                #CONVERT VIBRATION BYTES TO INTEGER
                intval = int.from_bytes(val, byteorder='little')
                print(intval)
                intV= intval
                await self.queue.put(intval)
                # RECEIVE CURRENT VALUES
                amp = await client.read_gatt_char(current_sensor)
                print(amp)
                #CONVERT PLACE BYTES TO INTEGER

                intamp = int.from_bytes(amp, byteorder='little')
                intc = intamp
                # PLACE VIBRATION AND CURRENT INSIDE QUEUE
                await self.queue.put(intamp)


#Coroutine 2 - Upload BLE data to an InfluxDB database
    async def cor2(self):
        while True:
            intval = await self.queue.get() # Get vibration
            intamp = await self.queue.get() # Get current
            print('C', intamp)
            print('V', intval)
            write_api = clientt.write_api(write_options=SYNCHRONOUS)
            p = influxdb_client.Point("gatewayy").field("vvibration", intval).field("ccurrent", intamp).time(datetime.utcnow())
            write_api.write(bucket=bucket, org=org, record=p)
            await asyncio.sleep(0)


#Coroutine 3 - Publish BLE data to MQTT broker
    async def cor3(self):
        while True:
            intV = await self.queue.get()
            intc = await self.queue.get()

            vib = str(intV)
            cur = str(intc)
            print('vi', vib)
            client.publish('Vib', vib)
            client.publish('Current', cur)

            if intc > 0.1:
                client.publish('Motor_status', 'Motor ON')
            else:
                client.publish('Motor_status', 'Motor OFF')
            await asyncio.sleep(0)




loop = asyncio.get_event_loop()
d=D()
try:
    asyncio.ensure_future(d.cor1(sys.argv[1] if len(sys.argv) == 2 else ADDRESS))
    #asyncio.ensure_future(d.cor2())
    asyncio.ensure_future(d.cor3())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()