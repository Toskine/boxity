#!/usr/bin/env python3
import paho.mqtt.client as mqtt
# Module Imports
import json
import mysql.connector
from datetime import datetime
from datetime import datetime as d

day=""
idd=""
temp=""
pres=""
lum=""
hum=""
bruit=""

mysql=mysql.connector.connect(
    host="10.224.0.220",
    user="adimaker",
    passwd="adimaker",
    database="adimakerdb"
)

def on_connect(client, userdata, flags, rc):
    # This will be called once the client connects
    print(f"Connected with result code {rc}")
    # Subscribe here!
    client.subscribe("data")
    print("on_connect")
    


def on_message(client, userdata, msg):

    global idd,temp,pres,lum,hum,bruit
    
    date = d.now()
    day = date.strftime("%Y-%m-%d %H:%M:%S")

    text = msg.payload.decode('utf-8')
    data = json.loads(text)
    
    day = day
    idd =data["id"]
    temp = data["temperature"]
    pres = data["pression"]
    lum = data["luminosite"]
    hum = data["humidité"]
    bruit = data["bruit"]


    print("---------on_message------------------")
    mycursor=mysql.cursor()

    sql= f"INSERT INTO theapp-adimaker(day,idd,temp,hum,pres,lum,bruit) VALUES(%s,%s,%s,%s,%s,%s,%s)"
    val=(str(day),str(idd),str(temp),str(pres),str(lum),str(hum),str(bruit))

    mycursor.execute(sql,val)

    mysql.commit();

    print("data is saved");

client = mqtt.Client("ADIAIRMOOD") # client ID "mqtt-test"
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("adimaker", "adimaker")
client.connect('10.224.0.220', 1883)
client.loop_forever()  # Start networking daemon


