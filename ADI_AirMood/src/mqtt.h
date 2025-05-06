#include <Arduino.h>
#include <Wire.h>

bool valuesChange = false;

#include <PubSubClient.h>
WiFiClient espClient;
PubSubClient mqttClient(espClient);
const char *mqttServer = "10.224.0.220";
uint32_t mqttServerPort = 1883;
const char *mqttLogin = "adimaker";
const char *mqttPassword = "adimaker";
long lastReconnectAttempt = 0;

void mqttCallback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void mqttInit()
{
  mqttClient.setServer(mqttServer, mqttServerPort);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(255);
  lastReconnectAttempt = 0;
}

boolean mqttReconnect()
{
  Serial.print("Attempting MQTT connection...");
  // Create a random client ID
  String clientId = "ESP32_" + WiFi.macAddress();
  Serial.println("ClientId: " + clientId);
  // Attempt to connect
  if (mqttClient.connect(clientId.c_str(), mqttLogin, mqttPassword))
  {
    Serial.println("connected");
    // Once connected, publish an announcement...
    // mqttClient.publish("outTopic", "hello world");
    // ... and resubscribe
    // mqttClient.subscribe("inTopic");
  }
  else
  {
    Serial.print("failed, rc=");
    Serial.println(mqttClient.state());
  }
  return mqttClient.connected();
}

String on2(int value)
{
  if (value < 10)
    return "0" + String(value);
  return String(value);
}

void mqtt_init(bool debug)
{
  if (debug)
  {
    Serial.println("______________");
    Serial.println("MQTT_INIT");
    Serial.println("______________");
  }
  mqttInit();
  if (!mqttClient.connected())
  {
    mqttReconnect();
  }
  if (debug)
  {
    Serial.println("success");
  }
}

double lum;
double temp2;
double pres;
double hum2;
double bruit;

void mqtt_set_data(double *data, bool debug)
{
  if (debug)
  {
    Serial.println("______________");
    Serial.println("MQTT_SET_DATA");
    Serial.println("______________");
    Serial.print(data[0]);
    Serial.print('\t');
    Serial.print(data[1]);
    Serial.print('\t');
    Serial.print(data[2]);
    Serial.print('\t');
    Serial.print(data[3]);
    Serial.print('\t');
    Serial.print(data[4]);
  }

  lum = data[0];
  temp2 = data[1];
  pres = data[2];
  hum2 = data[3];
  bruit = data[4];

  if (debug)
  {
    Serial.println("success");
  }
}

void mqttSend(bool debug)
{

  if (WiFi.status() == WL_CONNECTED)
  {
    if (!mqttClient.connected())
    {
      long now = millis();
      if (now - lastReconnectAttempt > 5000)
      {
        lastReconnectAttempt = now;
        // Attempt to reconnect
        if (mqttReconnect())
        {
          lastReconnectAttempt = 0;
        }
      }
    }
    else
    {
      mqttClient.loop();
    }
  }
  String ts = "error";
  //String json = "{\"idd\":\"" + WiFi.macAddress() + "\",\"temperature\":" + String(temp2) + ",\"pression\":" + String(pres) + ",\"luminosite\":" + String(lum) + ",\"humidité\":" + String(hum2) + ",\"bruit\":" + String(bruit) + "}";
  String json = "{\"idd\":\"" + WiFi.macAddress() + "\",\"temperature\":" + String(22+random(-1,1)) + ",\"pression\":" + String(1018+random(-10,10)) + ",\"luminosite\":" + String(1546+random(-20,20)) + ",\"humidité\":" + String(46+random(-5,5)) + ",\"bruit\":" + String(68+random(-3,3)) + "}";

  mqttClient.publish("data", json.c_str());

  if (debug)
  {
    Serial.println("______________");
    Serial.println("MQTT_SEND_DATA");
    Serial.println("______________");
    Serial.println(json);
  }
}