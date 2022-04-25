# #!/usr/bin/env python3

import paho.mqtt.client as mqtt

# This is the Subscriber

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))
#     client.subscribe("topic/test")

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Connected with result code " + str(rc))
        client.subscribe("topic/test")
    else:
        print("Bad connection Returned code=", rc)


def on_message(client, userdata, msg):
    if msg.payload.decode() == "Hello world!":
        print("Yes!")
        client.disconnect()


client = mqtt.Client()
client.connect("141.140.253.14", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()


# python3.6

import random

# from paho.mqtt import client as mqtt_client
#
#
# broker = 'broker.emqx.io'
# port = 1883
# topic = "python/mqtt"
# # generate client ID with pub prefix randomly
# # randint = random.randint(0, 100)
# # client_id = 'python-mqtt-', randint
# username = 'emqx'
# password = 'public'
#
#
# def connect_mqtt() -> mqtt:
#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("Connected to MQTT Broker!")
#         else:
#             print("Failed to connect, return code %d\n", rc)
#
#     # client = mqtt_client.Client(client_id)
#     # client = mqtt_client.Client("mqtt-test")
#     client = mqtt.Client()
#     client.username_pw_set(username, password)
#     client.on_connect = on_connect
#     client.connect(broker, port)
#     return client
#
#
# def subscribe(client: mqtt):
#     def on_message(client, userdata, msg):
#         # print(f"Received '{msg.payload.decode()}' from '{msg.topic}' topic")
#         print("topic: ", msg.topic, " Payload: ", msg.payload.decode())
#
#     client.subscribe(topic)
#     client.on_message = on_message
#
#
# def run():
#     client = connect_mqtt()
#     subscribe(client)
#     client.loop_forever()
#
#
# if __name__ == '__main__':
#     run()