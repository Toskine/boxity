import json
import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker: str, port: int, topic: str, keepalive: int = 60):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.keepalive = keepalive

    def _on_connect(self, client, userdata, flags, rc):
        status = "connected" if rc == 0 else f"error {rc}"
        print(f"MQTT {status}")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, self.keepalive)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT connect error: {e}")

    def publish(self, data: dict):
        try:
            self.client.publish(self.topic, json.dumps(data))
        except Exception as e:
            print(f"MQTT publish error: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()