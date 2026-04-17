
# Import library
import paho.mqtt.client as mqtt
import ssl
import time

####   client >>> only subscribe and receive data


SUB_TOPIC = "co326/sensor/data"

# connect and subscribe to topic
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with the result code",rc)
    client.subscribe(SUB_TOPIC)       # subscribe

# receive msg
def on_message(client, userdata, msg):
    print("Received ", msg.payload.decode())
      

def on_disconnect(client, userdata, rc, properties=None):
    print("Disconnected: ",rc)
    client.unsubscribe(SUB_TOPIC)

# err situation
def on_err(client, userdata, err):
    print("Got Error: ",err)

# create  client with mqtt5
client = mqtt.Client(client_id="co326_subscriber_client", protocol=mqtt.MQTTv5)


# calll functions
client.on_connect = on_connect
client.on_message = on_message

client.on_disconnect = on_disconnect

# define connect
client.connect("broker.hivemq.com",1883, 60)

# start loop
client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.loop_stop()
    client.disconnect()