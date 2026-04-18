
# Import library
import paho.mqtt.client as mqtt
import ssl
import time
import json

####   client >>> only subscribe and receive data

temp_accepted_range = range(19,36)
humidity_accepted_range = range(29,71)

# data receive at this
SUB_TOPIC = "co326/sensor/data"

# connect and subscribe to topic
def on_connect(client, userdata, flags, rc, properties=None):
    print("Subscriber Connected with the result code",rc)
    client.subscribe(SUB_TOPIC)       # subscribe

# receive msg and print if anomaly
def on_message(client, userdata, msg):
    #print("Received ", msg.payload.decode())

    data = json.loads(msg.payload.decode())

    temp = data["temperature"]
    humidity = data["humidity"]

    # check anomalies
    temp_anomaly = not (19 <= temp <= 36)
    humidity_anomaly = not (29 <= humidity <= 71)

    if temp_anomaly:
        print("⚠️ Temperature anomaly:", temp)

    if humidity_anomaly:
        print("⚠️ Humidity anomaly:", humidity)

    if not temp_anomaly and not humidity_anomaly:
        print(f"🟢 Normal data: \n Temp: {temp}\n Humidity:{humidity}\n \n")


def on_disconnect(client, userdata, rc, properties=None):
    print("Disconnected: ",rc)
    client.unsubscribe(SUB_TOPIC)

# err situation
def on_err(client, userdata, err):
    print("Got Error: ",err)

# create  client with mqtt5
subscriber = mqtt.Client(client_id="co326_subscriber_client", protocol=mqtt.MQTTv5)


# calll functions
subscriber.on_connect = on_connect
subscriber.on_message = on_message

subscriber.on_disconnect = on_disconnect

# define connect
subscriber.connect("broker.hivemq.com",1883, 60)

# start loop
subscriber.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    subscriber.loop_stop()
    subscriber.disconnect()