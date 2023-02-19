# BLE-Influxdb/MQTT_gateway
Gateway script written in python to send data recieved from Bluetooth Low Energy (BLE) devices to a InfluxDB database and as well as a MQTT broker. Based on python Asynchio framework.

The flowchart for the gatewaycode is seen below
![gateway](https://user-images.githubusercontent.com/85490469/219934565-874b9b4f-622a-48ac-bcc3-06c26e72b3cb.png)


1) At first, the gateway scans for the Arduino sensor node peripheral by reading the peripheral identifier of all the detected BLE devices. Once the gateway detects the Arduino, the connection is established, and the data is read by the topic. The data is read using the client.read_gatt_char( ) function as bytes and gets converted into integers. The integer values of each sensor is sent to the other coroutines using the queue.put() function.

2) The next coroutine of the code is responsible for querying the data obtained from the sensors to the influx dB database. The queue.get() function is used to get the data from the BLE central coroutine and the influxbd write api is used to query the data into the influx db database. Before querying the data, a data bucket has to be configured to store the data collected from this project. 

3) The MQTT, which is the last coroutine  is responsible for publishing the sensor data to an MQTT broker. This allows the sensor data to be visualised by external dashboards by subscribing to the topic of the data. In addition, this coroutine sends a message to the node red server when the motor is started. This message is sent when the motor current value has passed beyond a certain threshold. 

FUTURE IMPROVEMENTS
- Code gets buggy when all three coroutines are made to run simultaneously. However the program can run Coroutine 1 & 2 or Coroutine 1 & 3 without any issues
- Adding a start/stop scan option to the first coroutine for choosing which BLE device to conect to.
