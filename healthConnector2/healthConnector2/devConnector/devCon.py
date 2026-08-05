import sys
import os

# Aggiunge la cartella root del progetto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import time
import uuid
import requests
from datetime import datetime, timezone
from MyMQTT import *
from sensors.HealthSensors import HealthSensors
class DeviceConnector:
    def __init__(self, interval):
        #Device Connector che gestisce i sensori e pubblica i dati via MQTT.

        settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
        self.settings = json.load(open(settings_path))
        self.catalogURL=self.settings['catalogURL']
        self.deviceInfo=self.settings['deviceInfo']
        self.deviceId=self.deviceInfo['id']
        
        # MQTT parameters
        self.mqtt_data=self.settings['mqtt_data']
        self.topic_publish=self.mqtt_data['mqtt_topic_publish']
        self.broker=self.mqtt_data['broker']
        self.port=self.mqtt_data['port']
        self.clientID = str(uuid.uuid1())
        self.sensors={}
        self.message = {
                            "bn": f"DeviceConnector_{self.clientID}",
                            "e": [
                                {
                                    "n": "spo2",
                                    "v": 0,
                                    "t": "",
                                    "u": "mmHg"
                                },
                                {
                                    "n": "hr",
                                    "v": 0,
                                    "t": "",
                                    "u": "bpm"
                                }
                            ]
                        }
        
        # Inizializza il client mqtt
        self.client = MyMQTT(clientID=self.clientID, broker=self.broker, port=self.port)

        # Inizializza i sensori
        self.sensor = HealthSensors(interval)

        # Avvia i sensori
        self.sensor.start()
        self.client.start()
        self.isactive = False

    def publish(self):
        #Legge i dati dai sensori e li pubblica in formato SenML su MQTT.

        # Costruisce il messaggio SenML
        self.message["e"][0]["v"] = self.sensor.spo2_value
        self.message["e"][0]["t"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.message["e"][1]["v"] = self.sensor.hr_value
        self.message["e"][1]["t"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Pubblica su MQTT usando MyMQTT
        self.client.myPublish(f"{self.topic_publish}/{self.deviceId}/health", self.message)
        print(f"Message published with topic {self.topic_publish}/{self.deviceId}/health")

    def registerDevice(self):
        #Registra il device sul catalog.

        try:
            requests.post(f'{self.catalogURL}/devices/{self.deviceId}', data=json.dumps(self.deviceInfo),timeout=1)
        except:
            print('CATALOG NOT CONNECTED')

    def pingCatalog(self):
        try:
            self.deviceInfo["last_update"] = time.time()
            requests.put(f'{self.catalogURL}/devices/{self.deviceId}', data=json.dumps(self.deviceInfo),timeout=1)
        except:
            print('Error updating device...')

    def active(self):
        try:
            response=requests.get(f'{self.catalogURL}/devices/{self.deviceId}/active',timeout=1)
            print(response.text)
            self.isactive = response.text == "1"
            self.deviceInfo["active"] = int(response.text)
            self.settings['deviceInfo'] = self.deviceInfo
            with open(os.path.join(os.path.dirname(__file__), 'settings.json'), 'w') as f:
                json.dump(self.settings, f, indent=4)
        except:
            print('CATALOG NOT CONNECTED')


    def stop(self):
        #Ferma il device connector e i sensori.
        
        print("Stopping Device Connector...")
        requests.delete(f'{device.catalogURL}/devices/{device.deviceId}')
        self.sensor.stopSim()
        self.sensor.join()
        self.client.stop()
        print("Device Connector stopped.")


# Avvio del Device Connector
if __name__ == "__main__":
    time.sleep(10)
    interval = 1  # Intervallo di lettura dei sensor
    device = DeviceConnector(interval=interval)
    device.registerDevice()
    device.active()
    try:
        counter_ping = 0
        while True:
            if device.isactive:
                device.publish()
            if counter_ping == 5:
                print("Pinging catalog...")
                device.active()
                device.pingCatalog()
                print(f"Device is active: {device.isactive}")
                counter_ping = 0
            time.sleep(interval)
            counter_ping += 1

    except KeyboardInterrupt:
        device.stop()