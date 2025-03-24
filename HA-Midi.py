#!/usr/bin/env python

import mido
import paho.mqtt.client as mqtt

# MQTT Configuration
mqtt_server = "192.168.86.23"
mqtt_port = 1883
mqtt_topic = "midi/pk"
mqtt_username = "lebjones"
mqtt_password = "F5589144f233$"
midi_attached_device = 'MPKmini2:MPKmini2 MIDI 1 20:0'

print("Discovered MIDI devices:")
print(mido.get_output_names())

# Variable to persist the current pad
current_pad = None

# Callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print(f"Connected to MQTT broker at {mqtt_server}:{mqtt_port}")
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")


# Callback for messages sent to the topic
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


# Create an object from the raw MIDI message and publish serialized JSON to the topic
def publish_to_mqtt_topic(message):
    global current_pad

    # Parse the MIDI message
    if message.type in ["note_on", "note_off"]:
        event = message.type
        note = message.note
        velocity = message.velocity

        # Check if the note corresponds to a pad (pad1 to pad8)
        if 44 <= note <= 51:  # Pads correspond to MIDI notes 44–51
            current_pad = f"pad{note - 43}"  # Map MIDI note 44-51 to pad1-pad8
            print(f"Pad pressed: {current_pad}")  # Log the pad press
            return  # Do not send MQTT for pad presses

        # Prepare the payload
        payload = {
            "event": event,
            "note": note,
            "velocity": velocity,
            "current_pad": current_pad
        }

        # Publish to MQTT
        client.publish(mqtt_topic, payload=str(payload).replace("'", '"'))
        print(f"Published: {payload}")


# MQTT Client Setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(mqtt_username, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_server, mqtt_port, 60)

# MIDI Input Setup
port = mido.open_input(midi_attached_device)
port.callback = publish_to_mqtt_topic

# Start MQTT Client Loop
client.loop_forever()
